from __future__ import annotations

import json
from datetime import date, time

from fastapi import Depends, Form
from loguru import logger

# from pawdantic.paw_types import VALID_POSTCODE
from pydantic import EmailStr

from shipaw.models.address import Address, Contact, FullContact
from shipaw.config import ShipawSettings
from shipaw.fapi.requests import ShipmentRequest
from shipaw.models.ship_types import ShipDirection, VALID_POSTCODE
from shipaw.models.shipment import Shipment


async def full_contact_form(
    address_line1: str = Form(...),
    address_line2: str = Form(''),
    address_line3: str = Form(''),
    town: str = Form(...),
    postcode: VALID_POSTCODE = Form(...),
    contact_name: str = Form(...),
    email_address: EmailStr = Form(...),
    business_name: str = Form(...),
    mobile_phone: str = Form(...),
) -> FullContact:
    return FullContact(
        address=Address(
            address_lines=[address_line1, address_line2, address_line3],
            town=town,
            postcode=postcode,
            business_name=business_name,
        ),
        contact=Contact(
            contact_name=contact_name,
            email_address=email_address,
            mobile_phone=mobile_phone.strip().replace(' ', ''),
        ),
    )


async def shipment_f_form(
    full_contact: FullContact = Depends(full_contact_form),
    shipping_date: date = Form(...),
    boxes: int = Form(...),
    service: str = Form(...),
    direction: ShipDirection = Form(...),
    reference: str = Form(...),
    context_json: str = Form(...),
    collect_ready: int = Form(...),
    collect_closed: int = Form(...),
    own_label: bool = Form(True),
) -> Shipment:
    collect_ready = time(hour=collect_ready)
    collect_closed = time(hour=collect_closed)
    context = json.loads(context_json)
    logger.info('Creating Shipment Request from form')

    if direction == ShipDirection.OUTBOUND:
        sender = None
        recipient = full_contact
        own_label = None
    elif direction in {ShipDirection.INBOUND, ShipDirection.DROPOFF}:
        sender = full_contact
        recipient = ShipawSettings.from_env().full_contact
        own_label = own_label
    else:
        raise ValueError(f'Unknown direction: {direction}')

    shipment = Shipment(
        recipient=recipient,
        sender=sender,
        boxes=boxes,
        shipping_date=shipping_date,
        direction=direction,
        reference=reference,
        service=service,
        context=context,
        collect_ready=collect_ready,
        collect_closed=collect_closed,
        own_label=own_label,
    )
    return shipment


async def shipment_request_form(
    shipment: Shipment = Depends(shipment_f_form),
    provider_name: str = Form(...),
) -> ShipmentRequest:
    return ShipmentRequest(
        shipment=shipment,
        provider_name=provider_name,
    )


async def shipment_form_json(shipment_json: str = Form(...)) -> Shipment:
    shipy = Shipment.model_validate_json(shipment_json)
    return shipy


async def shipment_request_form_json(shipment_request_json: str = Form(...)) -> ShipmentRequest:
    shipy = ShipmentRequest.model_validate_json(shipment_request_json)
    return shipy


async def context_form_json(context_json: str = Form(...)) -> dict:
    context = json.loads(context_json)
    return context