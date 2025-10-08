from __future__ import annotations

import re
import datetime as dt
from typing import Annotated

import phonenumbers
from loguru import logger
from parcelforce_expresslink.shipment import ShipDirection
from pydantic import AfterValidator, BeforeValidator, Field, ValidationError

#
# class ShipDirection(StrEnum):
#     INBOUND = 'in'
#     OUTBOUND = 'out'
#     DROPOFF = 'dropoff'

TOD = dt.date.today()
COLLECTION_CUTOFF = dt.time(23, 59, 59)
ADVANCE_BOOKING_DAYS = 28
WEEKDAYS_IN_RANGE = [
    TOD + dt.timedelta(days=i) for i in range(ADVANCE_BOOKING_DAYS) if (TOD + dt.timedelta(days=i)).weekday() < 5
]

COLLECTION_WEEKDAYS = [i for i in WEEKDAYS_IN_RANGE if not i == TOD]


def limit_daterange_no_weekends(v: dt.date) -> dt.date:
    logger.debug(f'Validating date: {v}')
    if v:
        if isinstance(v, str):
            logger.debug(f'parsing date string assuming isoformat: {v}')
            v = dt.date.fromisoformat(v)

        if isinstance(v, dt.date):
            if v < TOD or v.weekday() > 4:
                logger.debug(f'Date {v} is a weekend or in the past - using next weekday')
                v = min(WEEKDAYS_IN_RANGE)

            if v > max(WEEKDAYS_IN_RANGE):
                logger.debug(f'Date {v} is too far in the future - using latest weekday (max 28 days in advance)')
                v = max(WEEKDAYS_IN_RANGE)

    return v


def validate_phone(v: str, values) -> str:
    logger.warning(f'Validating phone: {v}')
    phone = v.replace(' ', '')
    nummy = phonenumbers.parse(phone, 'GB')
    assert phonenumbers.is_valid_number(nummy)
    return phonenumbers.format_number(nummy, phonenumbers.PhoneNumberFormat.E164)


POSTCODE_PATTERN = re.compile(r'([A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2})')

pc_excluded = {'C', 'I', 'K', 'M', 'O', 'V'}


def validate_uk_postcode(v: str):
    if not re.match(POSTCODE_PATTERN, v) and not set(v[-2:]).intersection(pc_excluded):
        raise ValidationError('Invalid UK postcode')
    return v


VALID_POSTCODE = Annotated[
    str,
    AfterValidator(validate_uk_postcode),
    BeforeValidator(lambda s: s.strip().upper()),
    Field(..., description='A valid UK postcode'),
]


__all__ = ['ShipDirection']