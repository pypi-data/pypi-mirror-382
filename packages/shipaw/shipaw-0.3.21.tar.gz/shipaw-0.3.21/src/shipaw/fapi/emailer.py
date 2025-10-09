from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

import pythoncom
from loguru import logger
from win32com.client import Dispatch

from shipaw.config import ShipawSettings
from shipaw.fapi.requests import ShipmentRequest
from shipaw.models.shipment import Shipment


@dataclass
class Email:
    to_address: str
    subject: str
    body: str
    attachment_paths: list[Path] | None = None

    def __post_init__(self):
        if self.attachment_paths is None:
            self.attachment_paths = []

    def send(self, sender: OutlookHandler) -> None:
        sender.create_open_email(self)


class OutlookHandler:
    """
    Email handler for Outlook (ripped from pawsupport where it has a superclass and siblings for Gmail etc)
    """

    @staticmethod
    def create_open_email(email: Email, html: bool = False):
        """
        Send email via Outlook

        :param email: Email object
        :param html: format email from html input
        :return: None
        """
        try:
            pythoncom.CoInitialize()

            outlook = Dispatch('outlook.application')
            mail = outlook.CreateItem(0)
            mail.To = email.to_address
            mail.Subject = email.subject
            if html:
                mail.HtmlBody = email.body
            else:
                mail.Body = email.body

            for att_path in email.attachment_paths:
                mail.Attachments.Add(str(att_path))
                print('Added attachment')
            mail.Display()
        except Exception as e:
            logger.exception(f'Failed to send email with error: {e}')
            raise ValueError(f'{e.args[0]}')
        finally:
            pythoncom.CoUninitialize()


async def subject(*, invoice_num: str | None = None, missing: bool = False, label: bool = False):
    return (
        f'Amherst Radios'
        f'{f"- Invoice {invoice_num} Attached" if invoice_num else ""} '
        f'{"- We Are Missing Kit" if missing else ""} '
        f'{"- Shipping Label Attached" if label else ""}'
    )


async def send_label_email(shipment_request: ShipmentRequest, label_path: Path):
    body = (
        ShipawSettings.from_env()
        .templates.get_template('email_snips/label_email.html')
        .render(label=label_path, shipment_request=shipment_request, home_business_name=ShipawSettings.from_env().business_name)
    )
    email = Email(
        to_address=shipment_request.shipment.remote_full_contact.contact.email_address,
        subject=f'Amherst Radios Shipping - Shipping Label Attached',
        body=body,
        attachment_paths=[label_path],
    )

    OutlookHandler.create_open_email(email, html=True)


