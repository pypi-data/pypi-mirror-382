from odoo.tests.common import tagged
from odoo.tools import mute_logger
from .common import CommonCase
from faker import Faker
from faker.providers import ssn

fake = Faker('es_ES')
fake.add_provider(ssn)
NAME = fake.name()
VAT = fake.nif()
EMAIL = fake.email()
PASSWORD = fake.password(special_chars=False)
PASSWORD2 = fake.password(special_chars=False)

@tagged('post_install', '-at_install')
class TestSignupRequest(CommonCase):

    @mute_logger('odoo.addons.base_rest.http')
    def test_signup_request_no_partner(self):
        request = self.http('POST', '/api/account/signup_request', { 'vat': VAT }, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 404)


    @mute_logger('odoo.addons.base_rest.http')
    def test_signup_request_not_participant(self):
        self.env['res.partner'].create({
            'name': NAME,
            'vat': VAT
        })

        self.assertEqual(len(self.env['res.partner'].search([('vat', '=', VAT)])), 1)
        self.assertEqual(self.env['res.partner'].search([('vat', '=', VAT)])[0].name, NAME)

        request = self.http('POST', '/api/account/signup_request', { 'vat': VAT }, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 404)


    @mute_logger('odoo.addons.base_rest.http')
    def test_signup_request_correct(self):
        self.env['res.partner'].create({
            'name': NAME,
            'vat': VAT,
            'participant': True
        })

        self.assertEqual(len(self.env['res.partner'].search([('vat', '=', VAT)])), 1)
        self.assertEqual(self.env['res.partner'].search([('vat', '=', VAT)])[0].name, NAME)

        request = self.http('POST', '/api/account/signup_request', { 'vat': VAT }, { 'api_key': self.api_key })

        self.assertTrue(request.ok)
        for partner in self.env['res.partner'].search([]):
            if partner.signup_token == request.json()['token']:
                self.assertEqual(partner.vat, VAT)
        self.assertEqual(request.json()['name'], NAME)

        self.signup_token = request.json()['token']


@tagged('post_install', '-at_install')
class TestSignup(TestSignupRequest):

    @mute_logger('odoo.addons.base_rest.http')
    def test_signup_no_token(self):
        super().test_signup_request_correct()
        request = self.http('POST', '/api/account/signup', { 'token': 'asdfasdf', 'password': PASSWORD }, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 404)


    @mute_logger('odoo.addons.base_rest.http')
    def test_signup_no_password(self):
        super().test_signup_request_correct()
        request = self.http('POST', '/api/account/signup', { 'token': self.signup_token }, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 400)


    def test_signup_correct(self):
        super().test_signup_request_correct()
        request = self.http('POST', '/api/account/signup', { 'token': self.signup_token, 'password': PASSWORD }, { 'api_key': self.api_key })

        self.assertTrue(request.ok)
        self.assertEqual(request.json()['login'], VAT)
        self.assertEqual(len(self.env['res.users'].search([('login', '=', VAT)])), 1)
        self.assertIn(self.env.ref('base.group_portal'), self.env['res.users'].search([('login', '=', VAT)]).groups_id)


    @mute_logger('odoo.addons.base_rest.http')
    def test_change_password(self):
        self.test_signup_correct()

        request = self.http('POST', '/api/account/signup_request', { 'vat': VAT }, { 'api_key': self.api_key })
        self.assertTrue(request.ok)
        signup_token = request.json()['token']

        request = self.http('POST', '/api/account/signup', { 'token': signup_token, 'password': PASSWORD2 }, { 'api_key': self.api_key })

        self.assertTrue(request.ok)
        self.assertEqual(request.json()['login'], VAT)
        self.assertEqual(len(self.env['res.users'].search([('login', '=', VAT)])), 1)
        self.assertIn(self.env.ref('base.group_portal'), self.env['res.users'].search([('login', '=', VAT)]).groups_id)

        request = self.http('POST', '/api/account/login', { 'vat': VAT, 'password': PASSWORD }, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 403)
        request = self.http('POST', '/api/account/login', { 'vat': VAT, 'password': PASSWORD2 }, { 'api_key': self.api_key })
        self.assertTrue(request.ok)


@tagged('post_install', '-at_install')
class TestLogin(TestSignup):

    @mute_logger('odoo.addons.base_rest.http')
    def test_login_wrong_password(self):
        super().test_signup_correct()
        request = self.http('POST', '/api/account/login', { 'vat': VAT, 'password': 'wrong' }, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 403)


    @mute_logger('odoo.addons.base_rest.http')
    def test_login_not_participant(self):
        super().test_signup_correct()
        request = self.http('POST', '/api/account/login', { 'vat': 'wrong', 'password': 'wrong' }, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 403)


    def test_login_email(self):
        partner = self.env['res.partner'].create({
            'name': NAME,
            'vat': VAT,
            'email': EMAIL,
            'participant': True
        })
        partner.signup_prepare()
        self.env['res.users'].signup({
            'login': EMAIL,
            'email': EMAIL,
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
            'password': PASSWORD
        }, partner.signup_token)

        request = self.http('POST', '/api/account/login', { 'vat': VAT, 'password': PASSWORD }, { 'api_key': self.api_key })
        self.assertTrue(request.ok)
        self.assertIsInstance(request.json(), str)


    def test_login_correct(self):
        super().test_signup_correct()
        request = self.http('POST', '/api/account/login', { 'vat': VAT, 'password': PASSWORD }, { 'api_key': self.api_key })
        self.assertTrue(request.ok)

        self.jwt_token = request.json()
        self.assertIsInstance(self.jwt_token, str)
