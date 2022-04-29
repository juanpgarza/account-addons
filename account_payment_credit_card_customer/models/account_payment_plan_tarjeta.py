# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountPaymentPlanTarjeta(models.Model):
    _name = 'account.payment.plan.tarjeta'
    _description = 'Plan de tarjeta de credito'

    name = fields.Char('Nombre')    
    journal_id = fields.Many2one('account.journal',string='Tarjeta',domain="[('is_credit_card','=',True)]")
    active = fields.Boolean(default=True)

