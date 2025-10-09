from odoo.addons.base_rest.controllers.main import RestController

class Controller(RestController):
    _root_path = '/api/'
    _collection_name = 'photovoltaic_api.services'
    _default_auth = 'jwt_validator'
    _default_type = 'json'
