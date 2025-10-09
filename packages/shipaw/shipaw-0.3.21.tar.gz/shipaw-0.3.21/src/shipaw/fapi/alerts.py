from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from shipaw.models.base import ShipawBaseModel


class AlertType(StrEnum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    NOTIFICATION = 'NOTIFICATION'


class Alert(ShipawBaseModel):
    code: int | None = None
    message: str
    type: AlertType = AlertType.NOTIFICATION

    def __eq__(self, other):
        if not isinstance(other, Alert):
            return NotImplemented
        return (self.code, self.message, self.type) == (other.code, other.message, other.type)

    def __hash__(self):
        return hash((self.code, self.message, self.type))

    @classmethod
    def from_exception(cls, e: Exception):
        return cls(message=str(e), type=AlertType.ERROR)


class Alerts(ShipawBaseModel):
    alert: list[Alert] = Field(default_factory=list[Alert])

    @property
    def errors(self):
        return [a for a in self.alert if a.type == AlertType.ERROR]

    @property
    def warnings(self):
        return [a for a in self.alert if a.type == AlertType.WARNING]

    @property
    def notifications(self):
        return [a for a in self.alert if a.type == AlertType.NOTIFICATION]

    def __bool__(self):
        return bool(self.alert)

    def __add__(self, other: Alerts | Alert):
        if not isinstance(other, Alerts) and not isinstance(other, Alert):
            raise TypeError(f'Expected Alerts or Alert instance, got {type(other)}')
        if isinstance(other, Alert):
            other = Alerts(alert=[other])
        combined = set(self.alert) | set(other.alert)
        return Alerts(alert=list(combined))

    def __iadd__(self, other: Alerts | Alert):
        if not isinstance(other, Alerts) and not isinstance(other, Alert):
            raise TypeError(f'Expected Alerts or Alert instance, got {type(other)}')
        if isinstance(other, Alert):
            other = Alerts(alert=[other])
        self.alert = list(set(self.alert) | set(other.alert))
        return self

    def __sub__(self, other: Alerts | Alert):
        if not isinstance(other, Alerts) and not isinstance(other, Alert):
            raise TypeError(f'Expected Alerts or Alert instance, got {type(other)}')
        if isinstance(other, Alert):
            other = Alerts(alert=[other])
        diff = set(self.alert) - set(other.alert)
        return Alerts(alert=list(diff))

    def __contains__(self, alert: Alert):
        return alert in set(self.alert)

    @classmethod
    def empty(cls):
        return cls(alert=[])


async def maybe_alert_phone_number(phone_num: str):
    """Alert if phone number is not 11 digits or does not start with 01, 02 or 07. (parcelforce requirement)"""
    alerts = Alerts.empty()
    if len(phone_num) != 11 or not phone_num[0:2] == '07':
        alerts += Alert(
            type=AlertType.ERROR,
            message=f'The Mobile phone number ({phone_num}) must be 11 digits and begin with 07. Unable to send with no phone number (try "Use Home Base Mobile").',
        )
    return alerts
