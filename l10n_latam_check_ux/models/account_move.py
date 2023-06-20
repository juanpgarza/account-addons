##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    rejected_check_id_ux = fields.Many2one(
        'account.payment',
        'Rejected Check',
    )

