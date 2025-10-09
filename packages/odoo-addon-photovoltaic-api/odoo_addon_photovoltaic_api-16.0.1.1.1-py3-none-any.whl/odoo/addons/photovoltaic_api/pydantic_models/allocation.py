from . import OrmModel

class Allocation(OrmModel):
    id: int
    amount: float
    period: int
    year: int
    state: str
    energy_generated: float
    tn_co2_avoided: float
    eq_family_consumption: float
    type: str


class AllocationByYear(OrmModel):
    amount: float
    year: int