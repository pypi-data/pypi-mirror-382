from pathlib import Path
from typing import TYPE_CHECKING
import re

from loguru import logger

from shipaw.config import ShipawSettings
from shipaw.models.ship_types import ShipDirection

if TYPE_CHECKING:
    from shipaw.models.shipment import Shipment


def make_filename_safe(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)


def get_label_folder(direction: ShipDirection):
    return ShipawSettings.from_env().label_dir / direction


def get_label_stem(shipment: 'Shipment'):
    label_name = (
        f'Shipping Label'
        f'{f'-FROM {shipment.sender.address.business_name} | ' if shipment.sender else ''}'
        f'-TO {shipment.recipient.address.business_name} | '
        f'-ON {shipment.shipping_date}'
    )
    return make_filename_safe(label_name)


def unused_path(filepath: Path):
    def numbered_filepath(number: int):
        return filepath if not number else filepath.with_stem(f'{filepath.stem}_{number}')

    incremented = 0
    lpath = numbered_filepath(incremented)
    while lpath.exists():
        incremented += 1
        logger.warning(f'FilePath {lpath} already exists')
        lpath = numbered_filepath(incremented)
    logger.debug(f'Using FilePath={lpath}')
    return lpath


# def get_shipment_label_path(shipment: 'Shipment') -> Path:
#     folder = get_label_folder(shipment.direction)
#     label_stem = get_label_stem(shipment)
#     label_filepath = (folder / label_stem).with_suffix('.pdf')
#     label_filepath = unused_path(label_filepath)
#     return label_filepath
