from datetime import date
from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
from odoo.http import request
from odoo import http
from pydantic import TypeAdapter
from ..pydantic_models.allocation import Allocation
from ..pydantic_models.list_response import ListResponse
import logging

class AllocationService(Component):
    _inherit = 'base.rest.service'
    _name = 'allocations.service'
    _usage = 'allocations'
    _collection = 'photovoltaic_api.services'


    @restapi.method(
        [(['/'], 'GET')],
        input_param=restapi.CerberusValidator('_validator_get_allocations'),
        output_param=restapi.PydanticModel(ListResponse[Allocation])
    )
    def search(self, contract_id=None, offset=0, limit=None):
        domain = [('partner_id', '=', self.env.user.partner_id.id)]
        if contract_id :
            domain.append(('contract_id', '=', int(contract_id)))
        
        # Get allocations
        allocations = self.env['account.allocation'].search([*domain, ('start_period_date', '>=', '2021-01-01'), ('is_portal', '=', 'true')], limit, offset, order='start_period_date')
        total_allocations = self.env['account.allocation'].search_count([*domain, ('start_period_date', '>=', '2021-01-01')])

        # Get liquidation (legacy allocations)
        liquidations = self.env['participant.liquidations'].search(domain, limit, offset, order='period')
        total_liquidations = self.env['participant.liquidations'].search_count(domain)

        rows = []
        for allocation in allocations:
            rows.append(self._allocation_to_json(allocation))

        for liquidation in liquidations:
            rows.append(self._liquidation_to_json(liquidation))

        rows.sort(key=lambda datum: (datum['year'], datum['period']), reverse=True)
        return TypeAdapter(ListResponse[Allocation]).validate_python({'total': total_allocations+total_liquidations, 'rows': [Allocation.model_validate(r) for r in rows]})


    @restapi.method(
        [(['/<int:_id>/report'], 'GET')],
    )
    def get_allocation_report(self, _id):
        report = self.env['ir.actions.report'].sudo().search(['|', ('name', '=', 'Reparto'), ('name', '=', 'Account allocation')]) 
        pdf = report._render_qweb_pdf(report_ref=report.report_name, res_ids=[_id])[0]
        pdfhttpheaders = [  
            ("Content-Type", "application/pdf"),
            ("Content-Length", len(pdf)),
            ("Content-Disposition", http.content_disposition("report.pdf")),
        ]

        return request.make_response(pdf, headers=pdfhttpheaders)


    def _calculate_liquidation_period(self, full_period, payment_period):
        if (payment_period == 'Trimestral'):
            return int(full_period[0]), int(full_period.split(' ')[-1])
        return 0, int(full_period[len(full_period) - 4:])

    def _calculate_dates_of_period(self, period, year):
        if (period == 1):
            return date(year, 1, 1), date(year, 3, 31)
        elif (period == 2):
            return date(year, 4, 1), date(year, 6, 30)
        elif (period == 3):
            return date(year, 7, 1), date(year, 9, 30)
        elif (period == 4):
            return date(year, 10, 1), date(year, 12, 31)
        return date(year, 1, 1), date(year, 12, 31)



    def _calculate_production(self, contract_productions, start_date, end_date):
        energy_generated = 0
        tn_co2_avoided = 0
        eq_family_consumption = 0

        for production in contract_productions:
            if (production.start_date >= start_date and production.start_date <= end_date):
                energy_generated += production.energy_generated_contract
                tn_co2_avoided += production.tn_co2_avoided_contract
                eq_family_consumption += production.eq_family_consum_contract

        return energy_generated, tn_co2_avoided, eq_family_consumption

    def _allocation_to_json(self, allocation):
        energy_generated, tn_co2_avoided, eq_family_consumption = self._calculate_production(allocation.contract_id.contract_production_ids, allocation.start_period_date, allocation.end_period_date)
        return {
            'id': allocation.id,
            'amount': allocation.total,
            'period': int(allocation.end_period_date.month/3) if allocation.contract_id.payment_period_id.name == 'Trimestral' else 0,
            'year': allocation.end_period_date.year,
            'state': allocation.state,
            'energy_generated': energy_generated,
            'tn_co2_avoided': tn_co2_avoided,
            'eq_family_consumption': eq_family_consumption,
            'type': 'allocation'
        }

    def _liquidation_to_json(self, liquidation):
        period, year = self._calculate_liquidation_period(liquidation.period, liquidation.payment_period_id.name)
        start_date, end_date = self._calculate_dates_of_period(period, year)
        energy_generated, tn_co2_avoided, eq_family_consumption = self._calculate_production(liquidation.contract_id.contract_production_ids, start_date, end_date)

        return {
            'id': liquidation.id,
            'amount': liquidation.amount,
            'period': period,
            'year': year,
            'state': liquidation.state,
            'energy_generated': energy_generated,
            'tn_co2_avoided': tn_co2_avoided,
            'eq_family_consumption': eq_family_consumption,
            'type': 'liquidation'
        }

    def _validator_get_allocations(self):
        return {
            "contract_id": {'type': 'string'},
            "offset": {'type': 'integer'},
            'limit': { 'type': 'integer'}
        }
