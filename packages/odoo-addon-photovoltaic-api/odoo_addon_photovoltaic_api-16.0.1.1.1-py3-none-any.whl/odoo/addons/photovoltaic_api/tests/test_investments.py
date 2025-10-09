from odoo.tests.common import tagged
from odoo.tools import mute_logger
from odoo.tools.translate import load_language
from .common import CommonCase
from faker import Faker
from faker.providers import ssn
from datetime import date

fake = Faker('es_ES')
fake.add_provider(ssn)

def get_form_data(person_type='individual', promotional_code=None):
    data = {
        'type': person_type,

        'name': fake.first_name(),
        'surname': fake.last_name(),
        'vat': fake.nif(),
        'gender': fake.random.choice(['male', 'female', 'other']),
        'birthdate': fake.date(),

        'email': fake.email(),
        'phone': fake.phone_number(),

        'street': fake.street_address(),
        'street2': fake.random.choice([fake.secondary_address(), None]),
        'city': fake.city(),
        'state': fake.state(),
        'zip': fake.postcode().lstrip('0'),
        'country': 'España',

        'project': fake.sentence(2),
        'inversion': fake.random.randint(1, 10) * 1000,
        'promotional_code': promotional_code,

        'about_us': fake.random.choice(['Redes Sociales', 'Prensa', 'Búsqueda de internet', 'Amigo/Familia', 'Charla/Evento', 'Otro', None]),
        'participation_reason': fake.random.choice([None, fake.sentence()]),

        'personal_data_policy': fake.boolean(),
        'promotions': fake.boolean(),

        'tags': None
    }

    if person_type != 'individual':
        data.update({
            'name2': fake.first_name(),
            'surname2': fake.last_name(),
            'vat2': fake.nif(),
            'gender2': fake.random.choice(['male', 'female', 'other']),
            'birthdate2': fake.date(),
        })

        if person_type == 'partnership':
            data.update({
                'surname': None,
                'gender': None,
                'birthday': None,
            })

    return data


@tagged('post_install', '-at_install')
class TestInvestment(CommonCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        load_language(cls.cr, 'es_ES')

        cls.env['res.partner.type'].create({
            'name': 'Persona física'
        })


    @mute_logger('odoo.addons.base_rest.http')
    def test_investment_individual(self):
        form_data = get_form_data()

        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat'])]), 0)

        request = self.http(
            'POST',
            '/api/investments',
            form_data,
            { 'api_key': self.api_key }
        )
        self.assertEqual(request.status_code, 200)

        partner = self.env['res.partner'].search([('vat', '=', form_data['vat'])])
        self.assertEqual(len(partner), 1)

        country = self.env['res.country'].with_context(lang='es_ES').search([
            ('name', 'ilike', form_data['country'])
        ]).ensure_one()
        state = self.env['res.country.state'].with_context(lang='es_ES').search([
            ('name', 'ilike', form_data['state']),
            ('country_id', '=', country.id)
        ]).ensure_one()
        self.assertRecordValues(partner, [{
            'firstname':            form_data['name'],
            'lastname':             form_data['surname'],
            'vat':                  form_data['vat'],
            'gender_partner':       form_data['gender'],
            'birthday':             form_data['birthdate'],

            'email':                form_data['email'],
            'phone':                form_data['phone'],

            'street':               form_data['street'],
            'street2':              form_data['street2'],
            'city':                 form_data['city'],
            'state_id':             state.id,
            'zip':                  form_data['zip'],
            'country_id':           country.id,

            'about_us':             form_data['about_us'],
            'participation_reason': form_data['participation_reason'],

            'personal_data_policy': form_data['personal_data_policy'],
            'promotions':           form_data['promotions'],

            'participant':          True,
            'person_type':          self.env['res.partner.type'].search([('name', '=', 'Persona física')]).id,

            'company_type':         'person'
        }])

        self.assertEqual(partner.partner_mail_ids[0].mail, partner.email)
        self.assertEqual(partner.partner_phone_ids[0].phone, partner.phone)

        contract = self.env['contract.participation'].search([('partner_id', '=', partner.id)])
        self.assertRecordValues(contract, [{
            'name': 'Notificación Participación',
            'partner_id': partner.id,
            'inversion': form_data['inversion'],
            'contract_date': date.today(),
            'partner_relation': form_data['type'],
            'partner_id2': False,
        }])
