# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    default_pop_id = fields.Many2one(
        'pop.config',
        string='Caja por defecto',
        help="Caja por defecto para el usuario.")

    selected_pop_id = fields.Many2one(
        'pop.config',
        string='Caja seleccionada',
        help="Caja con la que está actualmente operando el usuario.")

    def get_selected_pop_id(self):
        if self.selected_pop_id:
            return self.selected_pop_id
        else:
            raise UserError("Debe seleccionar una caja")
