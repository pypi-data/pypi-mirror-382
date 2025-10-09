from . import OrmModel


class PowerStationProduction(OrmModel):
    date: str
    energy_generated: float
