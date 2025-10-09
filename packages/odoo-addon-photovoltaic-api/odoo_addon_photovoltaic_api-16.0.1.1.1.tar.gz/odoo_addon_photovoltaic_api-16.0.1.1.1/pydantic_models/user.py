from pydantic import Field
from .bank_account import BankAccountOut
from .info import Country, State
from . import OrmModel


class UserShort(OrmModel):
    id:        int | None = None
    firstname: str | None = None
    lastname:  str | None = None
    vat:       str | None = None
    gender:    str | None = Field(None, alias='gender_partner')
    birthday:  str | None = None
    alias:     str | None = None

class UserIn(OrmModel):
    person_type:    int | None = Field(None, alias='person_type_id')
    firstname:      str | None = None
    lastname:       str | None = None
    street:         str | None = None
    street2:        str | None = Field(None, alias='additional_street')
    zip:            str | None = None
    city:           str | None = None
    state_id:       int | None = None
    country_id:     int | None = None
    email:          str | None = None
    phone:          str | None = None
    mobile:         str | None = None
    alias:          str | None = None
    vat:            str | None = None
    gender_partner: str | None = Field(None, alias='gender')
    birthday:       str | None = None
    representative: UserShort | None = None
    about_us:       str | None = None
    interests:      list[str] | None = None

class UserOut(OrmModel):
    id:                int
    person_type:       str
    firstname:         str
    lastname:          str
    street:            str
    additional_street: str | None = None
    zip:               str
    city:              str
    state:             State | None = None
    country:           Country | None = None
    email:             str
    phone:             str | None = None
    mobile:            str | None = None
    alias:             str | None = None
    vat:               str
    gender:            str | None = None
    birthday:          str | None = None
    bank_accounts:     list[BankAccountOut]
    representative:    UserShort | None = None
    about_us:          str | None = None
    interests:         list[str]
    promotional_code:  str | None = None
    friend_ids:        list[bool] | None = None
