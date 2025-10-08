from pydantic import BaseModel

from royal_mail_click_and_drop.models.address import AddressRequest as AddressRM, RecipientDetailsRequest as ContactRM
from royal_mail_click_and_drop.models.create_orders_request import CreateOrderRequest
from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.services import Services
from shipaw.models.shipment import Shipment
from shipaw.providers.provider_abc import ShippingProvider

# ServiceDictPlaceholder: ServiceDict = {
#     'NEXT_DAY': 'sdfdasfg',
#     'NEXT_DAY_12': 'sgsdg',
#     'NEXT_DAY_9': 'sdgsd',
# }

SERVICES_PLACEHOLDER = Services(
    NEXT_DAY='',
    NEXT_DAY_12='',
    NEXT_DAY_9='',
)


def rm_address_from_agnostic_fc(full_contact: FullContact) -> AddressRM:
    return AddressRM(
        full_name=full_contact.contact.contact_name,
        company_name=full_contact.address.business_name,
        address_line1=full_contact.address.address_lines[0],
        address_line2=full_contact.address.address_lines[1] if len(full_contact.address.address_lines) > 1 else None,
        address_line3=full_contact.address.address_lines[2] if len(full_contact.address.address_lines) > 2 else None,
        city=full_contact.address.town,
        county=full_contact.address.county,
        postcode=full_contact.address.postcode,
        country_code=full_contact.address.country,
    )


def rm_contact_from_agnostic_fc(full_contact: FullContact) -> ContactRM:
    return ContactRM(
        address=rm_address_from_agnostic_fc(full_contact),
        phone_number=full_contact.contact.mobile_phone or full_contact.contact.phone_number,
        email_address=full_contact.contact.email_address,
    )


def full_contact_from_rm(recipient: ContactRM) -> FullContact:
    return FullContact(
        contact=Contact(
            contact_name=recipient.address.full_name,
            phone_number=recipient.phone_number,
            email_address=recipient.email_address,
            mobile_phone=recipient.phone_number,
        ),
        address=Address(
            business_name=recipient.address.company_name,
            address_lines=[
                line
                for line in [
                    recipient.address.address_line1,
                    recipient.address.address_line2,
                    recipient.address.address_line3,
                ]
                if line
            ],
            town=recipient.address.city,
            county=recipient.address.county,
            postcode=recipient.address.postcode,
            country=recipient.address.country_code,
        ),
    )


def shipment_from_rm(shipment: CreateOrderRequest) -> Shipment:
    return Shipment()


class RoyalMailProvider(ShippingProvider):
    name: str = 'ROYAL_MAIL'
    services = SERVICES_PLACEHOLDER

    def provider_shipment(self, shipment: Shipment) -> BaseModel:
        pass

    def agnostic_shipment(self, shipment: BaseModel) -> Shipment:
        pass

    def book_shipment(self, shipment: dict | Shipment) -> 'ShipmentBookingResponseAgnost': ...

    def fetch_label_content(self, shipment_num: str) -> bytes: ...