from pydantic import conlist, constr, field_validator, EmailStr, model_validator

from shipaw.models.base import ShipawBaseModel


class Contact(ShipawBaseModel):
    contact_name: str
    email_address: str | EmailStr
    mobile_phone: str
    phone_number: str | None = None

    @model_validator(mode='after')
    def phone_is_none(self):
        if not self.phone_number:
            self.phone_number = self.mobile_phone
        return self


class Address(ShipawBaseModel):
    business_name: str
    address_lines: list[str] = conlist(item_type=str, max_length=3, min_length=1)
    town: constr(max_length=25)
    postcode: constr(max_length=16)
    county: str | None = None
    country: str = 'GB'

    def get_address_lines_dict(self, prefix='address_line') -> dict[str, str]:
        return {f'{prefix}{i+1}': line for i, line in enumerate(self.address_lines) if line}

    @field_validator('address_lines', mode='after')
    def check_address_lines(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one address line is required')
        if len(v) > 3:
            v[2] = ', '.join(v[2:])
        if len(v) < 3:
            v += [''] * (3 - len(v))
        return v[:3]


class LongContact(ShipawBaseModel):
    contact_name: str
    email_address: str | EmailStr
    mobile_phone: str
    phone_number: str | None = None

    business_name: str
    address_lines: list[str] = conlist(item_type=str, max_length=3, min_length=1)
    town: constr(max_length=25)
    postcode: constr(max_length=16)
    country: str = 'GB'

    @model_validator(mode='after')
    def phone_is_none(self):
        if not self.phone_number:
            self.phone_number = self.mobile_phone
        return self

    def get_address_lines_dict(self, prefix='address_line') -> dict[str, str]:
        return {f'{prefix}{i+1}': line for i, line in enumerate(self.address_lines) if line}

    @field_validator('address_lines', mode='after')
    def check_address_lines(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one address line is required')
        if len(v) > 3:
            v[2] = ', '.join(v[2:])
        if len(v) < 3:
            v += [''] * (3 - len(v))
        return v[:3]


class FullContact(ShipawBaseModel):
    contact: Contact
    address: Address


class AddressChoice(ShipawBaseModel):
    address: Address
    score: int
