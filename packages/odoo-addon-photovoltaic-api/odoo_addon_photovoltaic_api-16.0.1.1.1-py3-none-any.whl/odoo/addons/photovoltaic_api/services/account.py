import secrets
from datetime import datetime, timedelta

import jwt
from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.exceptions import AccessDenied, MissingError, UserError


class AccountService(Component):
    _inherit = 'base.rest.service'
    _name = 'account.service'
    _usage = 'account'
    _collection = 'photovoltaic_api.services'


    @restapi.method(
        [(['/signup_request'], 'POST')],
        input_param=restapi.CerberusValidator('_validator_signup_request'),
        auth='api_key'
    )
    def signup_request(self, **params):
        '''
        Request to create a user from a partner
        :param vat: VAT
        :return: Signup token
        '''
        partner = self.env['res.partner'].search([('vat', '=ilike', params.get('vat').replace('%','')), ('participant', '=', True)])
        if len(partner) < 1:
            raise MissingError('Missing error')
        elif len(partner) > 1:
            raise UserError('Bad request')
            
        expiration = datetime.now() + timedelta(hours=1)
        partner.signup_prepare(expiration=expiration)
        return {
            'token': partner.signup_token,
            'email': partner.email,
            'name':  partner.name
        }

    @restapi.method(
        [(['/signup'], 'POST')],
        input_param=restapi.CerberusValidator('_validator_signup'),
        auth='api_key'
    )
    def signup(self, **params):
        '''
        Confirm signup with a signup token
        :param token: Signup token from signup_request
        :param password: Password
        :return: {VAT, JWT Token}
        '''
        token = params.get('token')
        password = params.get('password')
        if not password:
            raise UserError('Bad request')

        partner = []
        for p in self.env['res.partner'].search([]):
            if p.signup_token == token:
                partner = p
                break

        if len(partner) != 1:
            raise MissingError('Missing error')

        user = self.env['res.users'].search([('partner_id', '=', partner.id)])

        if len(user) == 0:
            firstname = partner.firstname
            lastname = partner.lastname
            self.env['res.users'].signup({
                'login': partner.vat,
                'email': partner.email,
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                'password': password
            }, token)
            user = self.env['res.users'].search([('login', '=', partner.vat)])
            partner.write({'firstname': firstname, 'lastname': lastname})
        else:
            self.env['res.users'].signup({
                'password': password
            }, token)

        return {
            'login': partner.vat,
            'jwt_token': self._get_token(user),
            'email': partner.email,
            'name':  partner.name
        }

    @restapi.method(
        [(['/login'], 'POST')],
        input_param=restapi.CerberusValidator('_validator_login'),
        auth='api_key'
    )
    def login(self, **params):
        '''
        Get JWT Token with login credentials
        :param vat: VAT
        :param password: Password
        :return: JWT Token
        '''
        try:
            user_id = self.env['res.users'].authenticate(
                '',
                params.get('vat'),
                params.get('password'),
                {'interactive': False})
        except AccessDenied:
            partner = self.env['res.partner'].search([('vat', '=ilike', params.get('vat').replace('%',''))])
            user_id = self.env['res.users'].authenticate(
                '',
                partner.email,
                params.get('password'),
                {'interactive': False})

        return self._get_token(self.env['res.users'].browse(user_id))


    # Private methods
    def _get_token(self, user):
        validator = self.env['auth.jwt.validator'].search([('name', '=', 'validator')])
        jwt_token = jwt.encode(
            {
                'aud': validator.audience,
                'iss': validator.issuer,
                'exp': datetime.now() + timedelta(weeks=4),
                'user_id': user.id
            },
            key=validator.secret_key,
            algorithm=validator.secret_algorithm,
        )
        return jwt_token

    def _validator_signup_request(self):
        return {
            'vat':      {'type': 'string'}
        }

    def _validator_signup(self):
        return {
            'token':    {'type': 'string'},
            'password': {'type': 'string', 'regex': r'^(?=.*\d)(?=.*[a-zA-Z]).{8,}$'}
        }

    def _validator_login(self):
        return {
            'vat':      {'type': 'string'},
            'password': {'type': 'string'}
        }
