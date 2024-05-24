# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    account_outcome_category_1 = fields.Many2one('account.outcome.category1', "Categoría 1")

    account_outcome_category_2 = fields.Many2one('account.outcome.category2', "Categoría 2")


