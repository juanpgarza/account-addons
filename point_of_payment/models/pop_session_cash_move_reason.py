# Copyright 2021 ITSur - Juan Pablo Garza <jgarza@itsur.com.ar>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class BoxSessionCashReason(models.Model):
	_name = 'box.session.cash.move.reason'
	_description = 'Motivo de movimiento de efectivo'

	name = fields.Char('Descripción')

	in_reason = fields.Boolean('Motivo ingreso')

	out_reason = fields.Boolean('Motivo egreso')
