import uuid
from typing import Annotated

from pydantic import StringConstraints

from shipaw.models.address import Address, Contact
from shipaw.models.base import ShipawBaseModel
from shipaw.models.shipment import Shipment
from shipaw.providers.provider_abc import ShippingProvider
from shipaw.providers.registry import PROVIDER_TYPE_REGISTER


class Authentication(ShipawBaseModel):
    # todo SecretStr!!!!
    user_name: Annotated[str, StringConstraints(max_length=80)]
    password: Annotated[str, StringConstraints(max_length=80)]


class ShipmentRequest(ShipawBaseModel):
    id: uuid.UUID = uuid.uuid4()
    shipment: Shipment
    provider_name: str

    @property
    def provider(self) -> ShippingProvider:
        if not self.provider_name:
            raise ValueError('Provider name is not set')
        if self.provider_name not in PROVIDER_TYPE_REGISTER:
            raise ValueError(f'Unknown provider: {self.provider_name}')
        return PROVIDER_TYPE_REGISTER[self.provider_name].from_env_settings()


class AddressRequest(ShipawBaseModel):
    postcode: str
    address: Address | None = None
    contact: Contact | None = None
