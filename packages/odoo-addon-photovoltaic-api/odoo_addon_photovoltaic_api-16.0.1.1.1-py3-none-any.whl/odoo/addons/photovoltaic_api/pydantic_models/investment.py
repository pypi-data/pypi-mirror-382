from typing import Literal
from pydantic import BaseModel, EmailStr


class InvestmentFormData(BaseModel):
    type: Literal['individual', 'minor', 'marriage', 'partnership']

    name: str
    surname: str | None = None
    vat: str
    gender: Literal['male', 'female', 'other'] | None = None
    birthdate: str | None = None

    email: EmailStr
    phone: str

    street: str
    street2: str | None = None
    city: str
    state: str
    zip: int
    country: str

    project: str
    inversion: int
    promotional_code: str | None = None

    about_us: Literal['Redes Sociales', 'Prensa', 'Búsqueda de internet', 'Amigo/Familia', 'Charla/Evento', 'Otro'] | None = None
    participation_reason: str | None = None

    personal_data_policy: bool
    promotions: bool = False

    name2: str | None = None
    surname2: str | None = None
    vat2: str | None = None
    gender2: Literal['male', 'female', 'other'] | None = None
    birthdate2: str | None = None

    tags: list[str] | None = None
