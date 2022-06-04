# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dataclasses import field
from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class AccountPaymentGroup(models.Model):
    _inherit = 'account.payment.group'

    partner_id = fields.Many2one(
        domain="[('parent_id','=',False)]",
    )

    show_contacts = fields.Boolean("Mostrar Contactos/Direcciones", default=False)

