import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, Self, TYPE_CHECKING

from loguru import logger
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from shipaw.config import ShipawSettings
from shipaw.models.base import ShipawBaseModel
from shipaw.models.logging import log_obj
from shipaw.models.services import Services
from shipaw.models.shipment import Shipment

if TYPE_CHECKING:
    from shipaw.fapi.requests import ShipmentRequest
    from shipaw.fapi.responses import ShipmentBookingResponse


class ShippingProvider(ABC, ShipawBaseModel):
    name: ClassVar[str]
    services: ClassVar[Services]
    settings_type: ClassVar[type[BaseSettings]]
    settings: BaseSettings

    @abstractmethod
    def is_sandbox(self) -> bool: ...

    @classmethod
    def from_env(cls, env_file: Path) -> Self:
        settings = cls.settings_type(_env_file=env_file)
        return cls(settings=settings)

    @classmethod
    def from_env_settings(cls, shipaw_settings=None) -> Self:
        shipaw_settings = shipaw_settings or ShipawSettings.from_env('SHIPAW_ENV')
        env_file = shipaw_settings.provider_env_dict.get(cls.name)
        provider_settings = cls.settings_type(_env_file=env_file)
        return cls(settings=provider_settings)

    @staticmethod
    @abstractmethod
    def provider_shipment(shipment: Shipment) -> BaseModel:
        """Takes agnostic Shipment object and returns provider Shipment object"""
        ...

    @staticmethod
    @abstractmethod
    def agnostic_shipment(shipment: BaseModel) -> Shipment:
        """Takes provider Shipment object and returns agnostic Shipment object"""
        ...

    @staticmethod
    @abstractmethod
    def book_shipment(shipment: dict | Shipment) -> 'ShipmentBookingResponse': ...

    @staticmethod
    @abstractmethod
    def fetch_label_content(shipment_num: str) -> bytes: ...

    # @staticmethod
    # async def booking_response_callback(request: 'ShipmentRequest', response: 'ShipmentBookingResponse'):
    #     """Do after booking, e.g. log, write label file, etc."""
    #     log_obj(response, 'Shipment Booked')
    #     try:
    #         if response.label_data is None and response.shipment_num:
    #             logger.info('Fetching missing label data...')
    #             response.label_data = request.provider.fetch_label_content(response.shipment_num)
    #         await response.write_label_file()
    #     except Exception as e:
    #         logger.exception(f'Error getting or writing label data: {e}')

    def wait_fetch_label(self, shipment_num: str) -> bytes:
        for i in range(10):
            try:
                time.sleep(1)
                label_data = self.fetch_label_content(shipment_num=shipment_num)
                assert label_data is not None
                return label_data
            except AssertionError as e:
                print(f'Label not ready yet for {shipment_num}, retrying...')
        raise RuntimeError(f'Label not ready after retries for {shipment_num}')


    async def wait_fetch_label_as(self, shipment_num: str) -> bytes:
        for i in range(10):
            try:
                time.sleep(1)
                label_data = self.fetch_label_content(shipment_num=shipment_num)
                assert label_data is not None
                return label_data
            except AssertionError as e:
                print(f'Label not ready yet for {shipment_num}, retrying...')
        raise RuntimeError(f'Label not ready after retries for {shipment_num}')

