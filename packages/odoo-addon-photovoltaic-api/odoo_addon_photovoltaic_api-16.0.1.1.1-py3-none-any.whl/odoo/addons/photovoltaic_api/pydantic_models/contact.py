from . import OrmModel
from pydantic import BaseModel, Field


class Contact(OrmModel):
    id:                   int | None = None
    firstname:            str | None = None
    lastname:             str | None = None
    street:               str | None = None
    street2:              str | None = Field(None, alias='additional_street')
    zip:                  str | None = None
    city:                 str | None = None
    state:                str | None = None
    country:              str | None = None
    email:                str | None = None
    phone:                str | None = None
    mobile:               str | None = None
    alias:                str | None = None
    vat:                  str | None = None
    gender_partner:       str | None = Field(None, alias='gender')
    birthday:             str | None = None
    participation_reason: str | None = None
    about_us:             str | None = None
    comment:              str | None = None
    is_chalet:            bool | None = None
    personal_data_policy: bool | None = None
    promotions:           bool | None = None
    message_notes:        str | None = None  # Notes
    tags:                 list[str] | None = None
    minor:                bool | None = Field(None, alias='is_minor')
    tutor:                int | None = None
