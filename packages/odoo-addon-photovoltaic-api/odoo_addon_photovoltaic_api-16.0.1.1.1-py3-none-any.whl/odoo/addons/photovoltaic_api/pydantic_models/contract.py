from . import OrmModel
from .power_station import PowerStationShort


class Contract(OrmModel):
    id: int
    name: str
    date: str
    investment: float
    power_plant: PowerStationShort
    bank_account: str | None = None
    peak_power: float
    stage: str
    generated_power: float
    tn_co2_avoided: float
    eq_family_consumption: float
    sent_state: str | None = None
    product_mode: str
    payment_period: str | None = None
    percentage_invested: float
    crece_solar_activated: bool


class ContractIn(OrmModel):
    investment: float
    power_plant: int
    product_mode: str
    discount: int | None = None
