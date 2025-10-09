from pydantic import BaseModel
from .allocation import AllocationByYear
from . import OrmModel
from .power_station_production import PowerStationProduction


class PowerStation(OrmModel):
    id: int
    name: str
    display_name: str | None = None
    image: str | None = None
    province: str
    city: str
    link_google_maps: str
    peak_power: float
    rated_power: float
    start_date: str
    monit_link: str | None = None
    monit_user: str | None = None
    monit_pass: str | None = None
    tecnical_memory_link: str | None = None
    annual_report_link: str | None = None
    energy_generated: float
    tn_co2_avoided: float
    reservation: float
    contracts_count: int
    eq_family_consumption: float
    production: list[PowerStationProduction]
    allocations_by_year: list[AllocationByYear]

class PowerStationPublic(OrmModel):
    id: int
    name: str
    display_name: str | None = None
    image: str | None = None 
    province: str
    city: str
    link_google_maps: str
    peak_power: float
    rated_power: float
    start_date: str
    energy_generated: float
    tn_co2_avoided: float
    reservation: float
    contracts_count: int
    eq_family_consumption: float

class PowerStationShort(BaseModel):
    id: int
    name: str
    display_name: str | None = None
    province: str
    city: str
