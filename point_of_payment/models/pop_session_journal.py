# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PopSessionJournal(models.Model):
    _name = 'pop.session.journal'
    _description = 'Detalle del medio de pago'

    @api.depends('line_ids', 'balance_start', 'line_ids.amount', 'balance_end_real')
    def _end_balance(self):
        for rec in self:
            rec.total_entry_encoding = sum([line.amount for line in rec.line_ids])
            rec.balance_end = rec.balance_start + rec.total_entry_encoding
            rec.difference = rec.balance_end_real - rec.balance_end
            rec.total_entry_encoding_in = sum([line.amount for line in rec.line_ids.filtered(lambda x: x.amount > 0)])
            rec.total_entry_encoding_out = sum([line.amount for line in rec.line_ids.filtered(lambda x: x.amount < 0)])

    @api.model
    def _default_opening_balance(self):       
        return 0

    @api.depends('journal_id')
    def _compute_currency(self):
        self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
   
    name = fields.Char(string='Reference', copy=False, readonly=True)

    pop_session_id = fields.Many2one(
        'pop.session', string='Sesión',
        help=".",
        required=True,
        index=True)

    journal_id = fields.Many2one(
        'account.journal', string='Diario',
        help=".",
        required=True,
        index=True)

    line_ids = fields.One2many('pop.session.journal.line', 'pop_session_journal_id', string='Detalle movimientos', copy=True)

    balance_start = fields.Monetary(string='Saldo inicial', default=_default_opening_balance)
    balance_end = fields.Monetary('Saldo final calculado', compute='_end_balance', store=True, help='Balance as calculated based on Opening Balance and transaction lines')
    total_entry_encoding = fields.Monetary('Transacciones', compute='_end_balance', store=True, help="Total of transaction lines.")
    balance_end_real = fields.Monetary('Saldo final')
    difference = fields.Monetary(compute='_end_balance', store=True, help="Difference between the computed ending balance and the specified ending balance.")

    currency_id = fields.Many2one('res.currency', compute='_compute_currency', string="Moneda")

    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', store=True, readonly=True)

    date = fields.Date(required=True, index=True, copy=False, default=fields.Date.context_today, string="Fecha")

    total_entry_encoding_in = fields.Monetary('Ingresos', compute='_end_balance', store=True)
    total_entry_encoding_out = fields.Monetary('Egresos', compute='_end_balance', store=True)
