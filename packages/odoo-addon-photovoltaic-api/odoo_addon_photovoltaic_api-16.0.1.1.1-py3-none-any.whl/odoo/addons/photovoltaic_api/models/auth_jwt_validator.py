from odoo import models, fields


class AuthJwtValidator(models.Model):
    _inherit = 'auth.jwt.validator'

    user_id_strategy = fields.Selection(
        selection_add=[('user_id', 'User ID')],
        required=True,
        default='user_id',
        ondelete={'user_id': 'set default'}
    )

    def _get_uid(self, payload):
        super()._get_uid(payload)

        if self.user_id_strategy == 'user_id':
            user = self.env['res.users'].browse(payload.get('user_id'))
            return user.id
