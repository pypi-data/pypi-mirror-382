from typing import Callable, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from shipaw.fapi.requests import ShipmentRequest
    from shipaw.fapi.responses import ShipmentBookingResponse

CALLBACK_REGISTER: dict[str, Callable[['ShipmentRequest', 'ShipmentBookingResponse'], Any]] = {}