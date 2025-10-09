import logging
import datetime

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.exceptions import UserError, MissingError

from ..pydantic_models import false_to_none
from ..pydantic_models.bank_account import BankAccountOut
from ..pydantic_models.info import Country, PersonType, State
from ..pydantic_models.user import UserIn, UserOut, UserShort
from .info import state_to_pydantic

_logger = logging.getLogger(__name__)


class UserService(Component):
    _inherit = 'base.rest.service'
    _name = 'user.service'
    _usage = 'user'
    _collection = 'photovoltaic_api.services'


    @restapi.method(
        [(['/'], 'GET')],
        output_param=restapi.PydanticModel(UserOut)
    )
    def get(self):
        return self._to_pydantic(self.env.user.partner_id)

    @restapi.method(
        [(['/'], 'PUT')],
        input_param=restapi.PydanticModel(UserIn),
        output_param=restapi.PydanticModel(UserOut)
    )
    def update(self, user_in):
        duplicated_vat_partners = self.env['res.partner'].sudo().search([('vat', '=', user_in.vat), ('participant', '=', True)])
        if user_in.vat and len(duplicated_vat_partners) > 0 and duplicated_vat_partners[0]['id'] != self.env.user.partner_id.id:
            raise UserError('vat already exists')

        user_dict = user_in.model_dump(exclude_unset=True, exclude={'representative', 'interests'})
        if (user_in.zip or user_in.state_id or user_in.country_id):
            user_dict['zip_id'] = None

        partner = self.env.user.partner_id
        is_login_vat = (partner.vat == self.env.user.login)
        partner.write(user_dict)

        if (partner.company_type == 'company' and partner.child_ids and user_in.representative):
            representative = partner.child_ids[0]
            representative.write(user_in.representative.dict(exclude_unset=True))

        if (user_in.interests):
            interest_ids = [self.env['res.partner.interest'].name_search(i)[0][0] for i in user_in.interests]
            partner.write({'interest_ids': [(6, 0, interest_ids)]})

        if is_login_vat:
            self.env.user.sudo().write({'login': partner.vat})

        return self._to_pydantic(partner)

    @restapi.method(
        [(['/allow_promotions'], 'POST')],
        input_param=restapi.CerberusValidator('_validator_promotions'),
        auth='api_key'
    )
    def allow_promotions(self, **params):
        user = self.env['res.partner'].browse([params.get('id')])
        if len(user) < 1:
            raise MissingError('No user with provided id')
        update = { 'promotions': params.get('allow_promotions') }
        if params.get('allow_promotions'):
            update['personal_data_policy'] = True
        user.message_post(body=f'Política de protección de datos aceptada el {datetime.datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")}')
        user[0].write(update)
        return user[0].email

    @restapi.method(
        [(['/mailchimp_sync'], 'POST')],
        input_param=restapi.CerberusValidator('_validator_mailchimp'),
        auth='api_key'
    )
    def mailchimp_sync(self, **params):
        allow = False
        if params.get('type') == 'subscribe':
            allow = True
        elif params.get('type') != 'unsubscribe':
            raise UserError('Unknown event type')
        email = params.get("data[email]")
        if not email:
            raise UserError('Bad email provided')
        # This is a bit hacky but mailchimp doesn't make things easy
        users = self.env['res.partner'].sudo().search([['email', '=', email]])
        if users:
            for user in users:
                user.write({ 'promotions': allow })
            return 'Sync successful'
        raise MissingError('No contacts with the provided email')


    #Private methods
    def _to_pydantic(self, user):

        representative = None
        if (user.company_type == 'company' and user.child_ids):
            representative = UserShort.model_validate(user.child_ids[0])
        
        return UserOut.model_validate({
            'id': user.id,
            'person_type': user.company_type,
            'firstname': user.firstname if user.company_type != 'company' else user.name,
            'lastname': user.lastname if user.company_type != 'company' else '',
            'street': user.street,
            'additional_street': false_to_none(user, 'street2'),
            'zip': user.zip,
            'city': user.city,
            'state': state_to_pydantic(user.state_id) if user.state_id else None,
            'country': Country.model_validate(user.country_id) if user.country_id else None,
            'email': user.email,
            'phone': false_to_none(user, 'phone'),
            'mobile': false_to_none(user, 'mobile'),
            'alias': false_to_none(user, 'alias'),
            'vat': user.vat,
            'gender': false_to_none(user, 'gender_partner'),
            'birthday': false_to_none(user, 'birthday'),
            # Omit dummy accounts with acc_number 'CRECE SOLAR' since they are for internal use
            'bank_accounts': [BankAccountOut.model_validate(a) for a in user.bank_ids if 'CRECE SOLAR' not in a.acc_number] if user.bank_ids else [],
            'representative': representative,
            'about_us': false_to_none(user, 'about_us'),
            'interests': user.interest_ids.mapped(lambda i: i.name) if user.interest_ids else [],
            'promotional_code': false_to_none(user, 'promotional_code'),
            'friend_ids': user.friend_ids.mapped(lambda i: i.used) if user.friend_ids else []
        })

    def _validator_promotions(self):
        return {
            'id':{'type': 'integer'},
            'allow_promotions': {'type': 'boolean'}
        }

    def _validator_mailchimp(self):
        return {
            'type': {'type': 'string'},
            "data[email]": {'type': 'string'}
        }
