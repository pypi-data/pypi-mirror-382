from __future__ import annotations

from base64 import b64decode, b64encode
from pathlib import Path

from loguru import logger
from pawdf.array_pdf.array_p import on_a4
from pydantic import ConfigDict, Field, model_validator

from shipaw.config import ShipawSettings
from shipaw.models.base import ShipawBaseModel
from shipaw.fapi.alerts import Alerts
from shipaw.models.label_file import get_label_folder, get_label_stem, unused_path
from shipaw.models.shipment import Shipment


class ShipawTemplate(ShipawBaseModel):
    template_path: str
    context: dict = Field(default_factory=dict)

    def render_template(self, request):
        if not self.template_path:
            raise ValueError('No template_path set')
        return ShipawSettings.from_env().templates.TemplateResponse(
            request=request, name=self.template_path, context=self.context
        )


class BaseResponse(ShipawBaseModel):
    alerts: Alerts = Alerts.empty()
    data: dict | None = None
    success: bool | None = None
    status: str | None = None
    template: ShipawTemplate | None = None


class ShipmentBookingResponse(BaseResponse):
    shipment: Shipment
    shipment_num: str | None = None
    tracking_link: str | None = None
    label_data: bytes | None = None
    label_path: Path | None = None

    model_config = ConfigDict(json_encoders={bytes: lambda v: b64encode(v).decode('utf-8') if v else None})

    @model_validator(mode='after')
    def get_label_path(self):
        if self.label_path is None:
            folder = get_label_folder(self.shipment.direction)
            label_stem = get_label_stem(self.shipment)
            label_filepath = (folder / label_stem).with_suffix('.pdf')
            self.label_path = unused_path(label_filepath)
        return self

    async def write_label_file(self):
        try:
            label_content = self.label_data
        except Exception as e:
            logger.error(f'Error getting label content: {e}')
            raise
        label_path = self.label_path
        unsize = label_path.parent / 'original_size' / label_path.name
        unsize.parent.mkdir(parents=True, exist_ok=True)
        unsize.write_bytes(label_content)
        on_a4(input_file=unsize, output_file=label_path)
        logger.info(f'Wrote label to {label_path}')


class ShipawTemplateResponse(BaseResponse):
    template: ShipawTemplate
