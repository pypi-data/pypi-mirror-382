from apc_hypaship.models.request.address import Address, Contact
from apc_hypaship.models.request.shipment import Shipment as ShipmentAPC
from shipaw.models.address import Address as AddressAgnost, Contact as ContactAgnost, FullContact
from shipaw.models.services import Services
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment as ShipmentAgnost

APC_SERVICES = Services(
    NEXT_DAY='ND16',
    NEXT_DAY_12='ND12',
    NEXT_DAY_9='ND09',
)


def address_from_agnostic_fc[addr_type: Address](cls: type[addr_type], full_contact: FullContact) -> addr_type:
    lines_ = [_ for _ in full_contact.address.address_lines[1:] if _]
    lines = ', '.join(lines_)
    return cls(
        company_name=full_contact.address.business_name,
        address_line_1=full_contact.address.address_lines[0],
        address_line_2=lines,
        city=full_contact.address.town,
        postal_code=full_contact.address.postcode,
        country_code=full_contact.address.country,
        contact=Contact(
            person_name=full_contact.contact.contact_name,
            email=full_contact.contact.email_address,
            mobile_number=full_contact.contact.mobile_phone,
            phone_number=full_contact.contact.phone_number or full_contact.contact.mobile_phone,
        ),
    )


def contact_from_agnostic_fc[contact_type: Contact](cls: type[contact_type], full_contact: FullContact) -> contact_type:
    return cls(
        person_name=full_contact.contact.contact_name,
        email=full_contact.contact.email_address,
        mobile_number=full_contact.contact.mobile_phone,
        phone_number=full_contact.contact.phone_number,
    )


def full_contact_from_apc_contact_address(contact: Contact, address: Address) -> FullContact:
    return FullContact(
        address=AddressAgnost(
            business_name=address.company_name,
            address_lines=[line for line in [address.address_line_1, address.address_line_2] if line],
            town=address.city,
            postcode=address.postal_code,
            country=address.country_code,
        ),
        contact=ContactAgnost(
            contact_name=contact.person_name,
            email_address=contact.email,
            mobile_phone=contact.mobile_number,
            phone_number=contact.phone_number or contact.mobile_number,
        ),
    )

