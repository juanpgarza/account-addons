# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_credit_card = fields.Boolean('Es tarjeta de credito',related='journal_id.is_credit_card')
    plan_tarjeta_id = fields.Many2one('account.payment.plan.tarjeta',string='Plan Tarjeta', ondelete='Restrict')
    nro_lote = fields.Char('N° Lote')
    nro_cupon = fields.Char('N° Cupon')

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

class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_ids = fields.One2many('account.payment', 'move_id')

    @api.depends('payment_ids.journal_id', 'payment_ids.plan_tarjeta_id', 'payment_ids.nro_lote')
    def _compute_ref(self):
        for record in self:
            refs = []
            for payment in record.payment_ids:
                ref_parts = [payment.journal_id.name]
                if payment.plan_tarjeta_id.name:
                    ref_parts.append(payment.plan_tarjeta_id.name)
                if payment.nro_lote:
                    ref_parts.append(f"Lote {payment.nro_lote}")
                refs.append(", ".join(ref_parts))
            record.ref = ", ".join(refs)

    ref = fields.Char(compute='_compute_ref', store=True)







