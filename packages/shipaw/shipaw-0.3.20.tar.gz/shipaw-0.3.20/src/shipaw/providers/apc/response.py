from apc_hypaship.models.response.resp import BookingResponse

from shipaw.fapi.alerts import Alerts, Alert
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.shipment import Shipment as ShipmentAgnost


def errored_booking(shipment: ShipmentAgnost, response: BookingResponse):
    messages = response.orders.order.messages
    fieldname, message = strip_apc_error_msgs(messages)
    return errored_response(fieldname, message, shipment, response.model_dump())


def strip_apc_error_msgs(messages):
    fieldname = messages.error_fields.error_field.field_name
    message = messages.error_fields.error_field.error_message
    return fieldname, message


def errored_response(fieldname: str, message: str, shipment: ShipmentAgnost, data: dict):
    alerts = Alerts(alert=[Alert(message=f'Error booking shipment: {fieldname}: {message}')])
    return ShipmentBookingResponse(
        alerts=alerts,
        shipment=shipment,
        shipment_num='FAILED TO BOOK',
        tracking_link='FAILED TO BOOK',
        data=data,
        success=False,
    )

