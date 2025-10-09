{
    'name': 'Photovoltaic API',
    'version': '16.0.1.1.1',
    'depends': [
        'base_rest',
        'auth_api_key',
        'auth_jwt',
        'base_rest_pydantic',
        'pydantic',
        'photovoltaic_mgmt',
        'photovoltaic_mgmt_extended',
        'photovoltaic_participant_liquidations',
        'photovoltaic_participant_activities',
        'res_partner_custom',
        'partner_phone_mail_list',
        'portal',
        'base_vat'
    ],
    "external_dependencies": {
        "python": [
            "pydantic[email]",
            "pyjwt"
        ]
    },
    'author': 'Librecoop',
    'license': 'LGPL-3',
    'author_email': 'librecoop@protonmail.com',
    'category': 'Sales',
    'description': '''
    This module provides a REST API to interact with various modules of the
    photovoltaic suite developed by Domatix and Librecoop
    ''',
    'installable': True,
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'data/contract.xml',
        'data/data.xml'
    ]
}
