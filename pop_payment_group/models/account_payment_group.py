# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class AccountPaymentGroup(models.Model):
    _inherit = 'account.payment.group'

    pop_id = fields.Many2one('pop.config',
        string='Caja',
        ondelete='Restrict',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    pop_session_id = fields.Many2one('pop.session',
        string='Sesión de caja',
        ondelete='Restrict',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    # para mostrar los renglones de caja asociados en el recibo
    pop_session_journal_line_ids = fields.One2many(related='payment_ids.pop_session_journal_line_ids', string='Renglones de caja')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res['pop_id'] = self.env.user.get_selected_pop_id().id
        res['pop_session_id'] = self.env.user.get_selected_pop_id().current_session_id.id
        return res
