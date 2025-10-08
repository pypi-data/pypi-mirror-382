from apc_hypaship.error import apc_http_status_alerts
from httpx import HTTPStatusError
from loguru import logger
from parcelforce_expresslink.address import AddressChoice as AddressChoicePF, Contact as ContactPF

from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.fapi.alerts import Alert, Alerts, AlertType
from shipaw.models.address import AddressChoice as AddressChoiceAgnost
from shipaw.models.ship_types import ShipDirection
from shipaw.providers.parcelforce.provider_funcs import full_contact_from_provider_contact_address


async def try_book_shipment(shipment_request: ShipmentRequest) -> ShipmentBookingResponse:
    shipment_response = ShipmentBookingResponse(shipment=shipment_request.shipment)
    try:
        shipment_response = shipment_request.provider.book_shipment(shipment_request.shipment)

    except HTTPStatusError as e:
        await maybe_apc(e, shipment_request, shipment_response)

    except Exception as e:
        logger.exception(f'Error booking shipment: {e}')
        shipment_response.alerts += Alert.from_exception(e)

    return shipment_response


async def try_get_write_label(request: ShipmentRequest, response: ShipmentBookingResponse):
    if not response.label_data:
        await try_get_label_data(request, response)
    await try_write_label(response)


async def try_get_label_data(request: ShipmentRequest, response: ShipmentBookingResponse) -> None:
    try:
        if response.label_data is not None:
            logger.info('Label data already present, not fetching')
        else:
            if response.shipment_num:
                response.label_data = await request.provider.wait_fetch_label_as(response.shipment_num)
            else:
                logger.warning('No shipment number to fetch label data')

    except HTTPStatusError as e:
        await maybe_apc(e, request, response)

    except Exception as e:
        logger.exception(f'Error getting label data')
        response.alerts += Alert.from_exception(e)


async def try_write_label(response: ShipmentBookingResponse):
    try:
        await response.write_label_file()
    except Exception as e:
        logger.exception(f'Error writing label file: {e}')
        response.alerts += Alert.from_exception(e)


async def maybe_apc(e: HTTPStatusError, shipment_request, shipment_response):
    if 'APC' in shipment_request.provider_name:
        for alert in await apc_http_status_alerts(e):
            shipment_response.alerts += alert
    else:
        logger.exception(e)
        shipment_response.alerts += Alert.from_exception(e)


async def maybe_alert_apc(shipment_request):
    alerts = Alerts.empty()
    if shipment_request.provider_name == 'APC' and shipment_request.shipment.direction == ShipDirection.DROPOFF:
        alerts += Alert(
            message='APC does not support drop-off shipments - please select Outbound or Inbound Collection',
            type=AlertType.ERROR,
        )
    return alerts


async def convert_choice(choice: AddressChoicePF) -> AddressChoiceAgnost:
    fc = full_contact_from_provider_contact_address(contact=ContactPF.empty(), address=choice.address)
    return AddressChoiceAgnost(address=fc.address, score=choice.score)
