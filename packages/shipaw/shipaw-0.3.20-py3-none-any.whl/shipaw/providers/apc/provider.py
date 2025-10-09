from base64 import b64decode
from typing import ClassVar, override

from apc_hypaship.apc_client import APCClient
from apc_hypaship.config import APCSettings
from apc_hypaship.models.request.address import Address
from apc_hypaship.models.request.shipment import GoodsInfo, Order, Orders, Shipment as ShipmentAPC, ShipmentDetails
from apc_hypaship.models.response.common import APCException
from apc_hypaship.models.response.resp import BookingResponse

from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.logging import log_obj
from shipaw.models.services import Services
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment as ShipmentAgnost
from shipaw.providers.apc.provider_funcs import (
    APC_SERVICES,
    address_from_agnostic_fc,
    full_contact_from_apc_contact_address,
)
from shipaw.providers.apc.response import errored_booking
from shipaw.providers.provider_abc import ShippingProvider


# @dataclass
# @register_provider
class APCShippingProvider(ShippingProvider):
    name = 'APC'
    services: ClassVar[Services] = APC_SERVICES
    settings_type: ClassVar[APCSettings] = APCSettings
    settings: APCSettings
    client_: APCClient | None = None

    @property
    def client(self) -> APCClient:
        if self.client_ is None:
            if self.settings is None:
                raise ValueError('Settings must be set before using the client')
            self.client_ = APCClient(settings=self.settings)
        return self.client_

    @override
    def is_sandbox(self) -> bool:
        return 'training' in self.settings.base_url.lower()

    @override
    def agnostic_shipment(self, shipment: ShipmentAPC) -> ShipmentAgnost:
        """Takes APC Shipment object, returns agnostic Shipment object"""
        order = shipment.orders.order
        del_fc = full_contact_from_apc_contact_address(order.delivery.contact, order.delivery)
        send_fc = (
            full_contact_from_apc_contact_address(order.collection.contact, order.collection)
            if order.collection
            else None
        )
        service = APC_SERVICES.reverse_lookup(order.product_code)
        return ShipmentAgnost(
            service=service,
            shipping_date=order.collection_date,
            reference=order.reference,
            recipient=del_fc,
            sender=send_fc,
            boxes=order.shipment_details.number_of_pieces,
            direction=ShipDirection.INBOUND if order.collection is not None else ShipDirection.OUTBOUND,
            collect_ready=order.ready_at,
            collect_closed=order.closed_at,
        )

    @override
    def provider_shipment(self, shipment: ShipmentAgnost) -> ShipmentAPC:
        order = Order(
            ready_at=shipment.collect_ready,
            closed_at=shipment.collect_closed,
            collection_date=shipment.shipping_date,
            product_code=APC_SERVICES.lookup(shipment.service),
            reference=shipment.reference,
            delivery=address_from_agnostic_fc(Address, shipment.recipient),
            collection=address_from_agnostic_fc(Address, shipment.sender) if shipment.sender else None,
            goods_info=GoodsInfo(),
            shipment_details=ShipmentDetails(number_of_pieces=shipment.boxes),
        )
        return ShipmentAPC(orders=Orders(order=order))

    @override
    def book_shipment(self, shipment: ShipmentAgnost) -> ShipmentBookingResponse:
        """Takes provider ShipmnentDict, or ShipmentAgnost object"""
        # request_json = self.build_request_json(shipment)
        apc_ship = self.provider_shipment(shipment)
        log_obj(apc_ship, 'APC Shipment Request')
        try:
            apc_response: BookingResponse = self.client.fetch_book_shipment(apc_ship)
        except APCException as e:
            return errored_booking(shipment, e)
        response = self.build_response(apc_response, shipment)
        response.label_data = self.wait_fetch_label(response.shipment_num)
        return response

    @override
    def fetch_label_content(self, shipment_num: str) -> bytes:
        labl = self.client.fetch_label(shipment_num)
        content = labl.content
        return b64decode(content)

    @staticmethod
    def build_response(resp: BookingResponse, shipment: ShipmentAgnost):
        orders = resp.orders
        order = orders.order
        return ShipmentBookingResponse(
            shipment=shipment,
            shipment_num=order.order_number,
            tracking_link=r'https://apc.hypaship.com/app/shared/customerordersoverview/index#search_form',
            data=resp.model_dump(mode='json'),
            status=(str(orders.messages.code)),
            success=(orders.messages.code == 'SUCCESS'),
        )


