import os
from functools import wraps
from pathlib import Path
from urllib.parse import unquote

from fastapi import APIRouter, Body, Form
from fastapi.params import Depends
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from shipaw.config import ShipawSettings
from shipaw.fapi.alerts import Alerts
from shipaw.fapi.emailer import send_label_email
from shipaw.fapi.form_data import shipment_request_form, shipment_request_form_json
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipawTemplateResponse
from shipaw.fapi.routes_api import (
    order_results_api as order_confirm_json,
    order_summary_api as order_review_json,
    shipping_form_api as ship_form_json,
)
from shipaw.models.shipment import Shipment, sample_shipment

router = APIRouter()


def render_template_response(request: Request, resp: ShipawTemplateResponse) -> HTMLResponse:
    context = resp.template.context
    context['alerts'] = context.get('alerts', Alerts.empty()) + resp.alerts
    if resp.alerts.errors:
        return ShipawSettings.from_env().templates.TemplateResponse(
            request=request,
            name='alerts.html',
            context=context,
        )

    return ShipawSettings.from_env().templates.TemplateResponse(
        request=request,
        name=resp.template.template_path,
        context=context,
    )


def html_from_json(json_endpoint):
    @wraps(json_endpoint)
    async def wrapper(request: Request, *args, **kwargs):
        resp = await json_endpoint(request, *args, **kwargs)

        return ShipawSettings.from_env().templates.TemplateResponse(
            request=request, name=resp.template_path, context=resp.context
        )

    return wrapper


@router.post('/shipping_form', response_class=HTMLResponse)
async def shipping_form(request: Request, shipment: Shipment = Body(...)) -> HTMLResponse:
    res = await ship_form_json(request, shipment)
    return render_template_response(request, res)


@router.post('/order_summary', response_class=HTMLResponse)
async def order_summary(
    request: Request,
    shipment_request: ShipmentRequest = Depends(shipment_request_form),
) -> HTMLResponse:
    res = await order_review_json(request, shipment_request)
    return render_template_response(request, res)


@router.post('/order_results', response_class=HTMLResponse)
async def order_results(
    request: Request,
    shipment_request: ShipmentRequest = Depends(shipment_request_form_json),
) -> HTMLResponse:
    template_response = await order_confirm_json(request, shipment_request)
    return render_template_response(request, template_response)


@router.get('/test', response_class=HTMLResponse)
async def ship(request: Request) -> HTMLResponse:
    shipment = sample_shipment()
    res = await ship_form_json(request, shipment)
    return render_template_response(request, res)


@router.get('/home_mobile_phone', response_class=HTMLResponse)
async def home_mobile_phone():
    mobile_phone = ShipawSettings.from_env().mobile_phone
    return f"""
    <input type="tel" id="mobile_phone" name="mobile_phone" value="{mobile_phone}" required>
    """


@router.get('/open-file/{filepath}', response_class=HTMLResponse)
async def open_file(filepath: str):
    os.startfile(filepath)
    return HTMLResponse(content=f'<span>Re</span>')


@router.get('/print-file/{filepath}', response_class=HTMLResponse)
async def print_file(filepath: str):
    os.startfile(filepath, 'print')
    return HTMLResponse(content=f'<span>Re</span>')


@router.post('/email-label', response_class=HTMLResponse)
async def email_label(
    label_path: str = Form(...), shipment_request: ShipmentRequest = Depends(shipment_request_form_json)
):
    label_path = Path(unquote(label_path))
    logger.info(f'Emailing {label_path=} to {shipment_request.shipment.remote_full_contact.contact.email_address}')
    await send_label_email(shipment_request, label_path)
    return HTMLResponse(content=f'<span>Re</span>')
