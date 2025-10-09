from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from datetime import date
from ..pydantic_models.investment import InvestmentFormData
from odoo.fields import Command
from odoo.exceptions import ValidationError
import json


class InvestmentService(Component):
    _inherit = 'base.rest.service'
    _name = 'investments.service'
    _usage = 'investments'
    _collection = 'photovoltaic_api.services'


    @restapi.method(
        [(['/'], 'POST')],
        input_param=restapi.PydanticModel(InvestmentFormData),
        auth='api_key'
    )
    def create(self, form_data):
        form_data.vat = self._sanitize_vat(form_data.vat)
        if form_data.vat2:
            form_data.vat2 = self._sanitize_vat(form_data.vat2)

        # if minor and tutor share vat add vat suffix to avoid duplication
        if form_data.vat == form_data.vat2:
            if form_data.type == 'minor':
                form_data.vat = f'{form_data.vat}_menor_{form_data.name}'
            else:
                raise ValidationError(f'Los dos DNI/NIE no pueden ser iguales: [{form_data.vat}]')

        partner = self._get_partner(form_data)
        discount = False

        if form_data.promotional_code:
            form_data.promotional_code = form_data.promotional_code.upper()

            if self._is_new_participant(form_data.vat):
                inviter = self._partner_from_code(form_data.promotional_code)
                if inviter:
                    inviter.friend_ids = [Command.create({
                        'friend_id': partner.id
                    })]
                    discount = True

                else:
                    raise ValidationError(f'Código promocional no válido: [{form_data.promotional_code}]')

            else:
                raise ValidationError(f'Código promocional sólo válido para nuevos participantes: [{form_data.promotional_code}]')

        partner2 = None
        if form_data.type != 'individual':
            # create other partner with same values but update some
            partner2 = self._get_partner(InvestmentFormData(
                **dict(form_data) | {
                    'name': form_data.name2,
                    'surname': form_data.surname2,
                    'vat': form_data.vat2,
                    'gender': form_data.gender2,
                    'birthdate': form_data.birthdate2,
                }
            ))

            if form_data.type == 'minor':
                # tutor
                partner.write({
                    'minor': True,
                    'tutor': partner2.id
                })

            elif form_data.type == 'marriage':
                # conyuge
                partner.write({'marriage': partner2.id})
                partner2.write({'marriage': partner.id})

            elif form_data.type == 'partnership':
                # representante
                if partner2 != partner:
                    partner2.parent_id = partner


        contract = self.env['contract.participation'].create({
            'name': 'Notificación Participación',
            'partner_id': partner.id,
            'inversion': form_data.inversion,
            'contract_date': date.today(),
            'partner_relation': form_data.type,
            'partner_id2': partner2.id if partner2 else False,
        })
        contract.message_post(body=form_data)

        return {
            'detail': json.dumps({
                'code': 200,
                'message': 'Success',
                'contract_id': contract.id,
                'partner_id': partner.id,
                'partner_vat': partner.vat,
                'partner2_id': partner2.id if partner2 else False,
                'partner2_vat': partner2.vat if partner2 else False,
                'discount': discount
            })
        }


    def _get_partner(self, form_data):
        partner = self.env['res.partner'].search([('vat', '=', form_data.vat)])

        if partner:
            if not partner.participant:
                # sometimes a res.partner exists but they are not a participant,
                # for example from the contact form or other things and still
                # have to get their information updated
                self._create_or_update_partner(form_data, partner)

            # if they are already a participant don't update the values
            return partner

        else:
            return self._create_or_update_partner(form_data, None)


    def _create_or_update_partner(self, form_data, partner):
        persona_fisica = self.env['res.partner.type'].search([
                ('name', '=', 'Persona física')
        ]).ensure_one()

        try:
            country = self.env['res.country'].with_context(lang='es_ES').search([
                ('name', 'ilike', form_data.country)
            ]).ensure_one()
        except ValueError as e:
            raise ValidationError(f'País no encontrado: [{form_data.country}]') from e

        if country:
            try:
                state = self.env['res.country.state'].with_context(lang='es_ES').search([
                    ('name', 'ilike', form_data.state),
                    ('country_id', '=', country.id)
                ]).ensure_one()
            except ValueError as e:
                raise ValidationError(f'Provincia no encontrada: [{form_data.state}]') from e

        has_minor_vat = (form_data.type == 'minor' and '_menor_' in form_data.vat)
        write_data = {
            'firstname': form_data.name,
            'lastname': form_data.surname,
            'vat': form_data.vat,
            'gender_partner': form_data.gender,
            'birthday': form_data.birthdate,

            'email': form_data.email,
            'phone': form_data.phone,

            'street': form_data.street,
            'street2': form_data.street2,
            'city': form_data.city,
            'state_id': state.id,
            'zip': form_data.zip,
            'country_id': country.id,

            'about_us': form_data.about_us,
            'participation_reason': form_data.participation_reason,

            'personal_data_policy': form_data.personal_data_policy,
            'promotions': form_data.promotions,

            'participant': True,
            'person_type': persona_fisica.id,
            'company_type': 'person',
        }
        if not partner:
            partner = (self.env['res.partner']
                .with_context(no_vat_validation=has_minor_vat)
                .create(write_data))
        else:
            (partner
            .with_context(no_vat_validation=has_minor_vat)
            .write(write_data))

        partner._onchange_partner_email_list()
        partner._onchange_phone_list()

        if form_data.type == 'partnership':
            partner.write({
                'firstname': False,
                'lastname': form_data.name,
                'company_type': 'company',
            })

        return partner


    def _sanitize_vat(self, vat):
        return vat.upper().replace(' ', '').replace('-', '')


    def _is_new_participant(self, vat):
        # either no partner exists or if they exist,
        # they have 0 contracts in state Active or Payment Pending
        partner = self.env['res.partner'].search([
            ('vat', '=', vat),
            ('participant', '=', True)
        ])
        if partner:
            stage_active = (self.env['contract.participation.stage']
                .with_context(lang='en_US')
                .search([('name', '=', 'Active')]))
            stage_pending = (self.env['contract.participation.stage']
                .with_context(lang='en_US')
                .search([('name', '=', 'Payment Pending')]))

            active_contracts_count = self.env['contract.participation'].search_count([
                ('partner_id', '=', partner.id),
                '|',
                    ('stage_id', '=', stage_active.id),
                    ('stage_id', '=', stage_pending.id),
            ])
            return active_contracts_count == 0

        return True


    def _partner_from_code(self, code):
        partner = self.env['res.partner'].search([
            ('promotional_code', '=', code),
        ])
        if partner:
            active_contracts_count = self.env['contract.participation'].search_count([
                ('partner_id', '=', partner.id),
                ('stage_id', '=', self.env['contract.participation.stage'].search([('name', '=', 'Active')]).id),
            ])
            if active_contracts_count > 0:
                return partner

        return None
