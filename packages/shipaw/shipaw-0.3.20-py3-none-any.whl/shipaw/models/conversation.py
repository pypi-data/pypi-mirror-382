from typing import TYPE_CHECKING

from shipaw.models.base import ShipawBaseModel

if TYPE_CHECKING:
    ...
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentBookingResponse


class ShipmentConversation(ShipawBaseModel):
    request: 'ShipmentRequest'
    response: 'ShipmentBookingResponse'
