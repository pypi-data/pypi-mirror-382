from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.exceptions import AccessError, MissingError
from pydantic import TypeAdapter
from datetime import date
from ..pydantic_models import false_to_none
from ..pydantic_models.contract import Contract, ContractIn
from ..pydantic_models.list_response import ListResponse
import logging

_logger = logging.getLogger(__name__)


class ContractService(Component):
    _inherit = 'base.rest.service'
    _name = 'contracts.service'
    _usage = 'contracts'
    _collection = 'photovoltaic_api.services'

    @restapi.method(
        [(['/<int:_id>'], 'GET')],
        output_param=restapi.PydanticModel(Contract)
    )
    def get(self, _id):
        try:
            contract = self.env['contract.participation'].browse(_id)
            return self._to_pydantic(contract)

        except AccessError:
            # Return 404 even if it is from a different user
            # to not leak information
            raise MissingError('Access error')

    @restapi.method(
        [(['/'], 'GET')],
        input_param=restapi.CerberusValidator('_validator_search'),
        output_param=restapi.PydanticModel(ListResponse[Contract])
    )
    def search(self, offset=0, limit=None):
        try:
            contracts = self.env['contract.participation'].search(
                [
                    ('partner_id', '=', self.env.user.partner_id.id),
                    ('photovoltaic_power_station_id.name', '!=', 'GUARDABOSQUES'),
                    ('product_mode_id.name', '!=', 'Comunero')
                ], limit, offset)
            return self._list_to_pydantic(contracts)

        except AccessError:
            # Return 404 even if it is from a different user
            # to not leak information
            raise MissingError('Access error')

    @restapi.method(
        [(['/'], 'POST')],
        input_param=restapi.PydanticModel(ContractIn),
        output_param=restapi.PydanticModel(Contract)
    )
    def create(self, contract):
        discount = contract.discount
        if (discount):
            if (discount > 3):
                discounted_amount = contract.investment * 0,97
            else:
                discounted_amount = contract.investment - (contract.investment * (discount/100)) 
        else:
            discounted_amount = contract.investment

        power_station = self.env['photovoltaic.power.station'].sudo().browse(
            contract.power_plant)

        products = self.env['product.template'].sudo().with_context(lang='es_ES').search([('photovoltaic_power_station_id', '=', power_station.id),
                                                              ('name', 'ilike', self._compose_product_search_string(contract.product_mode, contract.investment))],
                                                              order='create_date desc', limit=1)

        if not products:
            raise MissingError('Product not found')

        contract = self.env['contract.participation'].sudo().create([{
            'name': self._compose_contract_name(power_station),
            'partner_id': self.env.user.partner_id.id,
            'inversion': contract.investment,
            'photovoltaic_power_station_id': contract.power_plant,
            'contract_date': date.today()
        }])

        contract_line = self.env['contract.participation.line'].sudo().create(
            [{'contract_id': contract.id, 'product_id': products[-1].id}])
        contract.write({'contract_lines': [(6, 0, [contract_line.id])]})
        contract.message_post(body=f'Importe pagado: {discounted_amount}')
       
        #   Update user used friends 
        if discount != 0: 
            friends = self.env.user.partner_id.friend_ids
            index = 0
            for record in friends:
                if record.used == False:
                    record.used = True 
                    index = index + 1
                if index > 2:
                    break  
        

        # Send email to contacto@ecooo.es to inform of the new contract
        template = self.env.ref("photovoltaic_api.new_contract").sudo()
        if template:
            # Created a copy of the template to edit the recipient without
            # editing the template itself
            template_copy = template.copy()
            template_copy.email_from = "contacto@ecooo.es"
            template_copy.email_to = "comunidad@ecooo.es"
            template_copy.send_mail(contract.id, force_send=True)
            template_copy.unlink()
        return self._to_pydantic(contract)

    @restapi.method(
        [(['/<int:_id>'], 'PUT')],
        input_param=restapi.CerberusValidator('_validator_update'),
        output_param=restapi.PydanticModel(Contract)
    )
    def update(self, _id, **params):
        contract = self.env['contract.participation'].search(
            [('id', '=', _id), ('partner_id', '=', self.env.user.partner_id.id)])
        bank_acc = self.env['res.partner.bank'].browse(
            params['bank_account_id'])

        try:
            bank_acc.read(['id'])  # Check access permission
            contract.sudo().write({'bank_account_id': bank_acc.id})
            return self._to_pydantic(contract)
        except AccessError:
            # Return 404 even if it is from a different user
            # to not leak information
            raise MissingError('Access error')

    @restapi.method(
        [(['/'], 'PUT')],
        input_param=restapi.CerberusValidator('_validator_update_some'),
        output_param=restapi.PydanticModel(ListResponse[Contract])
    )
    def update_some(self, **params):
        '''
        Modify bank_account_id for some contracts
        '''
        contracts = self.env['contract.participation'].search(
            [('id', 'in', params['ids']), ('partner_id', '=', self.env.user.partner_id.id)])
        bank_acc = self.env['res.partner.bank'].browse(
            params['bank_account_id'])

        try:
            bank_acc.read(['id'])  # Check access permission
            contracts.sudo().write({'bank_account_id': bank_acc.id})
            return self._list_to_pydantic(contracts)
        except AccessError:
            # Return 404 even if it is from a different user
            # to not leak information
            raise MissingError('Access error')

    # Private methods

    def _calculate_production_data(self, contract):
        generated_power = 0
        tn_co2_avoided = 0
        eq_family_consumption = 0
        for contract_production in contract.contract_production_ids:
            generated_power += contract_production.energy_generated_contract
            tn_co2_avoided += contract_production.tn_co2_avoided_contract
            eq_family_consumption += contract_production.eq_family_consum_contract
        return generated_power, tn_co2_avoided, eq_family_consumption

    def _compose_product_search_string(self, product_mode, investment):
        product_search = ''
        if (product_mode == 'short_term'):
            product_search += 'CORTO%'
        else:
            product_search += 'LARGO%'
            if (investment < 1000):
                product_search += 'MENOS1000'
            else:
                product_search += 'M_S1000'
        return product_search

    def _compose_contract_name(self, power_station):
        return f'🎀 NUEVO - {power_station.name} - {self._get_next_contract_number(power_station.contract_ids)}'

    def _get_next_contract_number(self, contracts):
        contract_numbers = self._get_contract_numbers(contracts)
        if len(contract_numbers) > 0:
            return max(contract_numbers) + 1
        return 1

    def _get_contract_numbers(self, contracts):
        contract_numbers = []
        for contract in contracts:
            contract_number_as_str = contract.name.split('-')[-1]
            try:
                contract_number = int(contract_number_as_str)
                contract_numbers.append(contract_number)
            except ValueError:
                _logger.error(f'Contract {contract.name} has non numeric end')
        return contract_numbers

    def _to_pydantic(self, contract):
        generated_power, tn_co2_avoided, eq_family_consumption = self._calculate_production_data(contract)
        return Contract.model_validate({
            'id': contract.id,
            'name': contract.name,
            'date': str(contract.contract_date),
            'investment': contract.inversion,
            'power_plant': {
                'id': contract.photovoltaic_power_station_id.id,
                'name': contract.photovoltaic_power_station_id.name,
                'display_name': false_to_none(contract.photovoltaic_power_station_id, 'name_display'),
                'province': contract.photovoltaic_power_station_id.province,
                'city': contract.photovoltaic_power_station_id.city
            },
            'bank_account': false_to_none(contract.bank_account_id, 'acc_number'),
            'peak_power': contract.peak_power,
            'stage': contract.stage_id.name,
            'generated_power': generated_power,
            'tn_co2_avoided': tn_co2_avoided,
            'eq_family_consumption': eq_family_consumption,
            'sent_state': false_to_none(contract, 'sent_state'),
            'product_mode': contract.product_mode_id.name,
            'payment_period': false_to_none(contract.payment_period_id, 'name'),
            'percentage_invested': contract.percentage,
            'crece_solar_activated': contract.crece_active
        })

    def _list_to_pydantic(self, contracts):
        return TypeAdapter(ListResponse[Contract]).validate_python({
            'total': len(contracts),
            'rows': [self._to_pydantic(c) for c in contracts]
        })

    def _validator_search(self):
        return {
            'offset': {'type': 'integer'},
            'limit':  {'type': 'integer'}
        }

    def _validator_update(self):
        return {
            'bank_account_id': {'type': 'integer'}
        }

    def _validator_update_some(self):
        return {
            'bank_account_id': {'type': 'integer'},
            'ids':             {'type': 'list', 'schema': {'type': 'integer'}}
        }
