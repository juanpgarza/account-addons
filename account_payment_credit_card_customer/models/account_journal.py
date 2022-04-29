# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_credit_card = fields.Boolean('Tarjeta de Credito')

