from __future__ import annotations

import functools
import os
from pathlib import Path
from urllib.parse import quote

import pydantic as _p
from fastapi.encoders import jsonable_encoder
from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.templating import Jinja2Templates

from shipaw.fapi.ui_funcs import get_ui, ordinal_dt, sanitise_id
from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.base import ShipawBaseModel
from shipaw.models.ship_types import ShipDirection


def get_path_from_environment(env_key: str) -> Path:
    env = os.getenv(env_key)
    if not env:
        raise ValueError(f'{env_key} not set')
    env_path = Path(env)
    if not env_path.exists():
        raise FileNotFoundError(f'{env_key} file {env_path} does not exist')
    return env_path


class ProviderEnv(ShipawBaseModel):
    name: str
    env_file: Path


class ShipawSettings(BaseSettings):
    # toggles
    shipper_live: bool = False
    log_level: str = 'DEBUG'

    # dirs
    label_dir: Path
    log_dir: Path
    ui_dir: Path = Field(default_factory=get_ui)

    # Provider env file dict (json string in .env)
    provider_env_dict: dict

    # auto dirs
    static_dir: Path | None = None
    template_dir: Path | None = None
    templates: Jinja2Templates | None = None

    # sender details
    address_line1: str
    address_line2: str | None = None
    address_line3: str | None = None
    town: str
    postcode: str
    country: str = 'GB'
    business_name: str
    contact_name: str
    email: str
    phone: str | None = None
    mobile_phone: str

    model_config = SettingsConfigDict()

    @classmethod
    @functools.lru_cache
    def from_env(cls, env_key='SHIPAW_ENV') -> ShipawSettings:
        return cls(_env_file=get_path_from_environment(env_key))

    ## SET UI/TEMPLATE DIRS ##
    @model_validator(mode='after')
    def set_ui(self):
        self.static_dir = self.static_dir or self.ui_dir / 'static'
        self.template_dir = self.template_dir or self.ui_dir / 'templates'
        self.templates = self.templates or Jinja2Templates(directory=self.template_dir)
        self.templates.env.filters['jsonable'] = jsonable_encoder
        self.templates.env.filters['urlencode'] = lambda value: quote(str(value))
        self.templates.env.filters['sanitise_id'] = sanitise_id
        self.templates.env.filters['ordinal_dt'] = ordinal_dt
        return self

    ## SET LOGGING & LABELS ##
    @computed_field
    @property
    def log_file(self) -> Path:
        return self.log_dir / 'shipaw.log'

    @computed_field
    @property
    def ndjson_log_file(self) -> Path:
        return self.log_dir / 'shipaw.ndjson'

    @_p.model_validator(mode='after')
    def create_log_files(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        for v in (self.log_file, self.ndjson_log_file):
            v.touch()
        return self

    @_p.field_validator('label_dir', mode='after')
    def create_label_dirs(cls, v, values):
        # todo bad path crashes progqram - try/except + fallback label path?
        directions = [_ for _ in ShipDirection]
        try:
            make_label_dirs(directions, v)
        except FileNotFoundError as e:
            v = Path.home() / 'Shipping Labels'
            make_label_dirs(directions, v)
        return v

    # SET ADDRESS/CONTACT OBJECTS #
    @property
    def contact(self):
        return Contact(
            contact_name=self.contact_name,
            email_address=self.email,
            mobile_phone=self.mobile_phone,
        )

    @property
    def address(self):
        return Address(
            address_lines=[_ for _ in [self.address_line1, self.address_line2, self.address_line3] if _],
            town=self.town,
            postcode=self.postcode,
            country=self.country,
            business_name=self.business_name,
        )

    @property
    def full_contact(self) -> FullContact:
        return FullContact(
            address=self.address,
            contact=self.contact,
        )


def make_label_dirs(directions, v):
    for direction in directions:
        apath = v / direction
        if not apath.exists():
            apath.mkdir(parents=True, exist_ok=True)
