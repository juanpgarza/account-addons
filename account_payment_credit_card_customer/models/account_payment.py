# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import ValidationError

   
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_credit_card = fields.Boolean('Es tarjeta de credito',related='journal_id.is_credit_card')
    nro_cupon = fields.Char('Nro Cupon')
    nro_tarjeta = fields.Char('Nro Tarjeta')
    cant_cuotas = fields.Integer('Cuotas')
    plan_tarjeta_id = fields.Many2one('account.payment.plan.tarjeta',string='Plan Tarjeta', ondelete='Restrict')
    nro_lote = fields.Integer('Nro lote')

    @api.constrains('nro_cupon','nro_lote')
    def _check_pago_tarjeta(self):
        for rec in self:
            if rec.is_credit_card:
                if (not rec.nro_cupon) or (not rec.nro_lote) or (not rec.plan_tarjeta_id):
                    raise ValidationError("Debe ingresar los datos de pago de tarjeta")

    @api.onchange('journal_id')
    def _journal_id_onchange(self):
        res = {}
        res['domain']={'plan_tarjeta_id':[('journal_id', '=', self.journal_id.id)]}
        return res