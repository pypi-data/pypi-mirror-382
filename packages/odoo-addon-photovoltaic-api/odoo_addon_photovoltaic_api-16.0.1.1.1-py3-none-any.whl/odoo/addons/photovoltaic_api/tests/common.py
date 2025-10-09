from odoo.tests.common import HttpCase
from odoo.tools import config
import secrets
import json

HOST = '127.0.0.1'
PORT = config['http_port']

class CommonCase(HttpCase):
    def setUp(self):
        super().setUp()

        self.env.ref('photovoltaic_mgmt.photovoltaic_manager').users = [(4, self.env.ref('base.user_admin').id, 0)]

        self.api_key = self.env['auth.api.key'].create({
            'name': 'test api key',
            'key': secrets.token_hex(16),
            'user_id': self.env.ref('base.user_admin').id
        }).key

        self.env['auth.jwt.validator'].create({
             'audience': 'test',
             'issuer': 'test',
             'name': 'validator',
             'partner_id_required': False,
             'partner_id_strategy': False,
             'public_key_algorithm': 'RS256',
             'public_key_jwk_uri': False,
             'secret_algorithm': 'HS256',
             'secret_key': 'test',
             'signature_type': 'secret',
             'user_id_strategy': 'user_id'
        })

    def http(self, method, url, data=None, headers=None, timeout=10):
        self.env.flush_all()
        if url.startswith('/'):
            url = f'http://{HOST}:{PORT}{url}'

        headers['content-type'] = 'application/json'

        if method == 'GET':
            return self.opener.get(url, timeout=timeout, headers=headers)
        elif method == 'POST':
            return self.opener.post(url, data=json.dumps(data), timeout=timeout, headers=headers)
        elif method == 'PUT':
            return self.opener.put(url, data=json.dumps(data), timeout=timeout, headers=headers)
