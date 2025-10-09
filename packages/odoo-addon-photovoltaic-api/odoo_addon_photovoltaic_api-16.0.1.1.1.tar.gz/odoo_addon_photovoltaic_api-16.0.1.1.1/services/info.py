from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo import tools

from ..pydantic_models.info import PersonType, Country, State, Interest
from ..pydantic_models.metrics import Metrics


def state_to_pydantic(state):
    return State.model_validate({
        'id': state.id,
        'name': state.name,
        'country_id': state.country_id.id
    })


class InfoService(Component):
    _inherit = 'base.rest.service'
    _name = 'info.service'
    _usage = 'info'
    _collection = 'photovoltaic_api.services'


    @restapi.method(
        [(['/person_types'], 'GET')],
        output_param=restapi.PydanticModelList(PersonType)
    )
    def person_types(self):
        '''
        Gets the list of person type ID and name
        '''
        types = self.env['res.partner.type'].search([])
        return [Country.model_validate(t) for t in types]

    @restapi.method(
        [(['/countries'], 'GET')],
        output_param=restapi.PydanticModelList(Country)
    )
    def countries(self):
        '''
        Gets the list of countries ID and name
        '''
        countries = self.env['res.country'].with_context(lang="es_ES").search([])
        return [Country.model_validate(c) for c in countries]

    @restapi.method(
        [(['/states'], 'GET')],
        output_param=restapi.PydanticModelList(State)
    )
    def states(self):
        '''
        Gets the list of all states ID and name
        '''
        states = self.env['res.country.state'].search([])
        return [state_to_pydantic(s) for s in states]

    @restapi.method(
        [(['/states_by_country/<int:_id>'], 'GET')],
        output_param=restapi.PydanticModelList(State)
    )
    def states_by_country(self, _id):
        '''
        Gets the list of states ID and name for that country_id
        '''
        states = self.env['res.country.state'].search([('country_id', '=', _id)])
        return [state_to_pydantic(s) for s in states]

    @restapi.method(
        [(['/interests'], 'GET')],
        output_param=restapi.PydanticModelList(Interest)
    )
    def interests(self):
        '''
        Gets the list of existing interests
        '''
        interests = self.env['res.partner.interest'].search([])
        return [Interest.model_validate(i) for i in interests]

    @restapi.method(
        [(['/metrics'], 'GET')],
        output_param=restapi.PydanticModel(Metrics),
        auth='api_key'
    )
    def metrics(self):
        return Metrics.model_validate({
            'tn_co2_avoided': self._get_tn_co2_avoided(),
            'installed_power': self._get_installed_power(),
            'energy_generated': self._get_energy_generated(),
            'plant_participants': self._get_plant_participants(),
            'plants_with_reservation': self._get_plants_with_reservation(),
            'total_installations': self._get_total_installations(),
            'total_inversion': self._get_total_inversion(),
            'total_benefits': self._get_total_benefits(),
            'total_investors': self._get_total_investors()
        })

    def _get_tn_co2_avoided(self):
        return self.env['photovoltaic.power.energy']._compute_total_tn_co2_avoided()

    def _get_installed_power(self):
        return self.env['photovoltaic.power.station']._compute_installed_power()

    def _get_energy_generated(self):
        return self.env['photovoltaic.power.energy']._compute_energy_generated()

    def _get_plant_participants(self):
        return self.env['res.partner']._compute_plant_participants()

    def _get_plants_with_reservation(self):
        return self.env['photovoltaic.power.station']._compute_plants_with_reservation()

    def _get_total_installations(self):
        total_installations = int(self.env['ir.config_parameter'].sudo().get_param('photovoltaic_mgmt.total_installations'))
        return total_installations

    def _get_total_inversion(self):
        return self.env['contract.participation']._compute_total_inversion()

    def _get_total_benefits(self):
        return self.env['account.allocation']._compute_total_benefits()

    def _get_total_investors(self):
        return self.env['contract.participation']._compute_total_investors()
