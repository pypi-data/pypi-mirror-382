from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.exceptions import AccessError, MissingError

from ..pydantic_models import false_to_none
from ..pydantic_models.allocation import AllocationByYear
from ..pydantic_models.power_station import PowerStation, PowerStationPublic
from ..pydantic_models.power_station_production import PowerStationProduction


class PowerStationService(Component):
    _inherit = 'base.rest.service'
    _name = 'powerstation.service'
    _usage = 'powerstation'
    _collection = 'photovoltaic_api.services'


    @restapi.method(
        [(['/<int:_id>'], 'GET')],
        output_param=restapi.PydanticModel(PowerStation)
    )
    def get(self, _id):
        station = self.env['photovoltaic.power.station'].browse(_id)
        try:
            return self._to_pydantic(station)

        except AccessError:
            # Return 404 even if it is from a different user
            # to not leak information
            raise MissingError('Access error')

    @restapi.method(
        [(['/'], 'GET')],
        input_param=restapi.CerberusValidator('_validator_search'),
        output_param=restapi.PydanticModelList(PowerStationPublic),
        auth='api_key'
    )
    def get_open_plants(self, **params):
        if (params['type'] == 'short_term'):
            field = 'short_term_investment'
        else:
            field = 'long_term_investment'

        stations = self.env['photovoltaic.power.station'].search([(field, '=', True)])
        return [self._public_to_pydantic(s) for s in stations]

    # Private methods
    def _to_pydantic(self, station):

        allocations_by_year = self.env["account.allocation"].sudo().read_group(
            [("photovoltaic_power_station_id", "=", station.id)], 
            ['end_period_date', 'total:sum'], 
            ['end_period_date:year'], 0, None, 'end_period_date')

        allocations = []
        for allocation in allocations_by_year:
            allocations.append(self._allocation_to_pydantic(allocation))

        return PowerStation.model_validate({
            'id': station.id,
            'name': station.name,
            'display_name': false_to_none(station, 'name_display'),
            'image': station.station_image_url,
            'province': station.province,
            'city': station.city,
            'link_google_maps': station.link_google_maps,
            'peak_power': station.peak_power,
            'rated_power': station.rated_power,
            'start_date': str(station.start_date),
            'monit_link': false_to_none(station, 'monit_link'),
            'monit_user': false_to_none(station, 'monit_user'),
            'monit_pass': false_to_none(station, 'monit_pass'),
            'tecnical_memory_link': false_to_none(station, 'tecnical_memory_link'),
            'annual_report_link': false_to_none(station, 'annual_report_link'),
            'energy_generated': station.energy_generated,
            'tn_co2_avoided': station.co2,
            'reservation': station.reservation,
            'contracts_count': station.contracts_count,
            'eq_family_consumption': station.eq_family_consumption,
            'production': station.photovoltaic_power_energy_ids.filtered(lambda prod: prod.energy_generated > 0).sorted('start_date', False).mapped(lambda prod: self._production_to_pydantic(prod)),
            'allocations_by_year': allocations
        })

    def _public_to_pydantic(self, station):
        return PowerStationPublic.model_validate({
            'id': station.id,
            'name': station.name,
            'display_name': false_to_none(station, 'name_display'),
            'image': station.station_image_url,
            'province': station.province,
            'city': station.city,
            'link_google_maps': station.link_google_maps,
            'peak_power': station.peak_power,
            'rated_power': station.rated_power,
            'start_date': str(station.start_date),
            'annual_report_link': false_to_none(station, 'annual_report_link'),
            'energy_generated': station.energy_generated,
            'tn_co2_avoided': station.co2,
            'reservation': station.reservation,
            'contracts_count': station.contracts_count,
            'eq_family_consumption': station.eq_family_consumption
        })

    def _production_to_pydantic(self, production):
        return PowerStationProduction.model_validate({
            'date': str(production.start_date),
            'energy_generated': production.energy_generated
        })

    def _allocation_to_pydantic(self, allocation):
        return AllocationByYear.model_validate({
            'year': allocation['end_period_date:year'],
            'amount': allocation['total']
        })

    def _validator_search(self):
        return {
            'type': {'type': 'string', 'allowed': ['short_term', 'long_term'], 'required': True}
        }
    
