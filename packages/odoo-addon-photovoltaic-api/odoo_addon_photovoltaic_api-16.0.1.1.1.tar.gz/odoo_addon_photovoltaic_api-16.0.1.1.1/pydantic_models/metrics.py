from . import OrmModel

class Metrics(OrmModel):
    tn_co2_avoided: float
    installed_power: float
    energy_generated: float
    plant_participants: float
    plants_with_reservation: float
    total_installations: float
    total_inversion: float
    total_benefits: float
    total_investors: float
