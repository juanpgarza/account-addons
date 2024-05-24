# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    account_outcome_category_1 = fields.Many2one('account.outcome.category1', string="Categoría 1",)

    account_outcome_category_2 = fields.Many2one('account.outcome.category2', string="Categoría 2",)

    account_outcome_category_multiple = fields.Selection(selection=[('no', 'No'), ('yes', 'Si'), ], string="Múltiples categorías?",)

    def write(self, values):
        super(AccountMove,self).write(values)
        for line in self.invoice_line_ids:
            line.account_outcome_category_1 = self.account_outcome_category_1
            line.account_outcome_category_2 = self.account_outcome_category_2
