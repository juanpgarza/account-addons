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
        domain="['&',('pop_id','=',pop_id),('state','=','opened')]",        
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    # para mostrar los renglones de caja asociados en el recibo
    pop_session_journal_line_ids = fields.One2many(related='payment_ids.pop_session_journal_line_ids', string='Renglones de caja')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        pop_id = self.env.user.get_selected_pop_id()
        if pop_id.current_session_state != 'opened':
            raise UserError("Debe iniciar una sesión de la caja '{}' para continuar (o seleccionar otra caja)".format(pop_id.name))        
        res['pop_id'] = pop_id.id
        res['pop_session_id'] = pop_id.current_session_id.id
        return res

    def post(self):
        # import pdb; pdb.set_trace()
        res = super().post()
        user_pop_id = self.env.user.get_selected_pop_id()
        
        # controlo que la caja informada en el recibo coincida con la caja del usuario
        for rec in self:
            if rec.pop_id != user_pop_id:
                raise UserError("Ud. tiene seleccionada la caja '{}' pero el comprobante pertenece a la caja '{}'.".format(user_pop_id.name, rec.pop_id.name))

        if user_pop_id.current_session_state != 'opened':
            raise UserError("Debe iniciar una sesión de la caja '{}' para continuar.".format(user_pop_id.name))
        
        # sino coincide la sesión del recibo con la sesión abierta. ACTUALIZO el recibo
        for rec in self:
            if rec.pop_session_id != rec.pop_id.current_session_id:
                rec.pop_session_id = rec.pop_id.current_session_id
                for payment in rec.payment_ids:
                    payment.pop_session_id = rec.pop_id.current_session_id

    def cancel(self):
        # import pdb; pdb.set_trace()
        # raise UserError("")
        res = super().cancel()
        user_pop_id = self.env.user.get_selected_pop_id()
        
        for rec in self:
            if rec.pop_id != user_pop_id:
                raise UserError("Ud. tiene seleccionada la caja '{}' pero el comprobante pertenece a la caja '{}'.".format(user_pop_id.name, rec.pop_id.name))

        if user_pop_id.current_session_state != 'opened':
            raise UserError("Debe iniciar una sesión de la caja '{}' para continuar.".format(user_pop_id.name))

        return res