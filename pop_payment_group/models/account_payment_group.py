# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class AccountPaymentGroup(models.Model):
    _inherit = 'account.payment.group'

    def _get_default_pop_id(self):
        return self.env.user.default_pop_id.id

    pop_id = fields.Many2one('pop.config', 
        string='Caja', 
        ondelete='Restrict',
        default=_get_default_pop_id,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    pop_session_id = fields.Many2one('pop.session', 
        string='Sesión de caja', 
        ondelete='Restrict',
        domain="['&',('pop_id','=',pop_id),('state','=','opened')]",
        readonly=True,
        states={'draft': [('readonly', False)]},        
    )

    # para mostrar los renglones de caja asociados en el recibo
    pop_session_journal_line_ids = fields.One2many(related='payment_ids.pop_session_journal_line_ids', string='Renglones de caja')

    @api.onchange('pop_id')
    def _onchange_pop_id(self):
        # si el usuario cambia la caja, que cargue la sesion activa para esa caja y que blanquee la grilla de pagos
        self.pop_session_id = self.env['pop.session'].search(['&',('pop_id','=',self.pop_id.id),('state','=','opened')])
        self.payment_ids = False
