from pathlib import Path
from typing import cast

from combadge.core.errors import BackendError
from fastapi import APIRouter, Body, Depends
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from shipaw.config import ShipawSettings
from shipaw.fapi.alerts import Alert, AlertType, Alerts, maybe_alert_phone_number
from shipaw.fapi.backend import convert_choice, maybe_alert_apc, try_book_shipment, try_get_write_label
from shipaw.fapi.form_data import shipment_request_form, shipment_request_form_json
from shipaw.fapi.requests import AddressRequest, ShipmentRequest
from shipaw.fapi.responses import ShipawTemplate, ShipawTemplateResponse
from shipaw.models.address import Address, AddressChoice as AddressChoiceAgnost
from shipaw.models.logging import log_obj
from shipaw.models.shipment import Shipment
from shipaw.providers.parcelforce.provider import ParcelforceShippingProvider
from shipaw.providers.parcelforce.provider_funcs import (
    address_from_agnostic,
)
from shipaw.providers.registry import PROVIDER_TYPE_REGISTER

router = APIRouter()
router.mount('/static', StaticFiles(directory=str(ShipawSettings.from_env().static_dir)), name='static')


@router.post('/shipping_form', response_model=ShipawTemplateResponse)
async def shipping_form_api(request: Request, shipment: Shipment = Body(...)) -> ShipawTemplateResponse:
    log_obj(shipment, 'Shipment received at /ship_form:')
    alerts: Alerts = request.app.alerts

    if any(['prdev' in str(_).lower() for _ in Path(__file__).parents]):
        msg = '"prdev" in cwd tree - BETA MODE - This is a development version'
        logger.warning(msg)
        alerts += Alert(message=msg, type=AlertType.WARNING)

    if ShipawSettings.from_env().shipper_live:
        msg = 'Shipper Live is True - Real Shipments will be booked'
    else:
        msg = 'Shipper_live is False - No Shipments will be booked'
    logger.warning(msg)
    alerts += Alert(message=msg, type=AlertType.NOTIFICATION)

    tmplt = ShipawTemplate(template_path='shipping_form_container.html', context={'shipment': shipment})
    return ShipawTemplateResponse(template=tmplt, alerts=alerts)


@router.post('/order_summary', response_model=ShipawTemplateResponse)
async def order_summary_api(
    request: Request,
    shipment_request: ShipmentRequest = Depends(shipment_request_form),
) -> ShipawTemplateResponse:
    log_obj(shipment_request, 'ShipmentRequest received at shipaw/order_summary:')
    context = {'shipment_request': shipment_request}

    alerts = await maybe_alert_phone_number(shipment_request.shipment.remote_full_contact.contact.mobile_phone)
    alerts += await maybe_alert_apc(shipment_request)

    return ShipawTemplateResponse(
        template=ShipawTemplate(template_path='/order_summary.html', context=context),
        alerts=alerts,
    )


@router.post('/order_results', response_model=ShipawTemplateResponse)
async def order_results_api(
    request: Request,
    shipment_request: ShipmentRequest = Depends(shipment_request_form_json),
) -> ShipawTemplateResponse:
    shipment_response = await try_book_shipment(shipment_request)
    await try_get_write_label(shipment_request, shipment_response)

    if shipment_response.alerts.errors:
        return await errored_shipment(shipment_response)

    log_obj(shipment_response, 'Shipment Booked')
    await try_get_write_label(shipment_request, shipment_response)

    if hasattr(request.app, 'callback'):
        await request.app.callback(shipment_request, shipment_response)

    shipment_response.template = ShipawTemplate(
        template_path='/order_results.html',
        context={'shipment_request': shipment_request, 'response': shipment_response},
    )
    return ShipawTemplateResponse.model_validate(shipment_response, from_attributes=True)


async def errored_shipment(shipment_response):
    log_obj(shipment_response.alerts, 'Errors booking shipment:')
    alerts = shipment_response.alerts
    shipment_response.template = ShipawTemplate(
        template_path='/alerts.html',
        context={'alerts': alerts},
    )
    return ShipawTemplateResponse.model_validate(shipment_response, from_attributes=True)


@router.post('/addr_choices', response_model=list[AddressChoiceAgnost], response_class=JSONResponse)
async def get_addr_choices_api(
    request: Request,
    body: AddressRequest = Body(...),
) -> list[AddressChoiceAgnost]:
    """Fetch candidate address choices for a postcode, optionally scored by closeness to provided address.
    Hardcoded to use Parcelforce provider for now - APC does not provide address lookup.

    Args:
        request: Request - FastAPI request object
        body: Address - request body containing postcode and optional address
    """
    p: ParcelforceShippingProvider = cast(
        ParcelforceShippingProvider, PROVIDER_TYPE_REGISTER['PARCELFORCE'].from_env_settings()
    )
    client = p.client
    postcode = body.postcode
    address_agnost = body.address
    pf_address = address_from_agnostic(address_agnost) if address_agnost else None
    # log_obj(pf_address, 'Address received at /cand:')

    try:
        res_pf = client.get_choices(postcode=postcode, address=pf_address)
        res = [await convert_choice(_) for _ in res_pf]
        return res

    except BackendError as e:
        alert = Alert(
            message=f'Error fetching candidates: {e}',
            type=AlertType.ERROR,
        )
        request.app.alerts += alert
        logger.warning(f'Error fetching candidates: {e}')
        addr = Address(address_lines=['ERROR:', str(e)], town='Error', postcode='Error', business_name='Error')
        chc = AddressChoiceAgnost(address=addr, score=0)
        return [chc]


