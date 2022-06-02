# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
class PopSessionJournalLine(models.Model):
    _name = 'pop.session.journal.line'
    _description = 'pop session journal line'

    def _compute_currency(self):
        self.currency_id = self.pop_session_journal_id.journal_id.currency_id or self.company_id.currency_id

    name = fields.Char(string='Motivo', copy=False, readonly=True)
    ref = fields.Char(string='Descripción')

    account_payment_id = fields.Many2one(
        'account.payment', string='Pago asociado',
        help=".",
        index=True)

    pop_session_journal_id = fields.Many2one(
        'pop.session.journal', string='Diario de la sesión',
        help=".",
        required=True,
        index=True)

    date = fields.Date(string='Fecha',required=True, default=lambda self: self._context.get('date', fields.Date.context_today(self)))

    amount = fields.Monetary(string='Monto')
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', string="Currency")
    partner_id = fields.Many2one('res.partner', string='Socio')

    company_id = fields.Many2one('res.company', related='pop_session_journal_id.journal_id.company_id', string='Company', store=True, readonly=True)

    anulado = fields.Boolean('Anulado',default=False)
    pop_session_name = fields.Char(related="pop_session_journal_id.pop_session_id.name", string="Sesión de caja")

    reason_id = fields.Many2one(comodel_name="box.session.cash.move.reason", string= 'Motivo de movimiento')
