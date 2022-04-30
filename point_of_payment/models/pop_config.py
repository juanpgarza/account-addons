# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

from odoo.osv import expression
from odoo.tools import float_is_zero, pycompat
from odoo.tools import float_compare, float_round, float_repr
from odoo.tools.misc import formatLang, format_date

import time
import math

class PopConfig(models.Model):
    _name = 'pop.config'
    _description = 'Caja'

    name = fields.Char(string='Descripción', index=True, required=True, help="Una descripción interna de la caja.")
    journal_ids = fields.Many2many(
        'account.journal', 'pop_journal_rel',
        'pop_id', 'journal_id', string='Métodos de pago disponibles',
        domain="[('type', 'in', ['bank', 'cash'])]",)

    session_ids = fields.One2many('pop.session', 'pop_id', string='Sesiones')

    current_session_id = fields.Many2one('pop.session', compute='_compute_current_session', string="Current Session")
    current_session_state = fields.Char(compute='_compute_current_session')
    pop_session_username = fields.Char(compute='_compute_current_session_user')
    pop_session_state = fields.Char(compute='_compute_current_session_user')
    pop_session_duration = fields.Char(compute='_compute_current_session_user')

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    cash_control = fields.Boolean(string='Has Cash Control',default=True,readonly=True)

    sequence_id = fields.Many2one('ir.sequence', string='Secuencia de sesiones', required=True,
        help="Numeración de las sesiones de caja.", copy=False)

    last_closed_session_id = fields.Many2one('pop.session', string='Ultima sesión cerrada')

    @api.depends('session_ids')
    def _compute_current_session_user(self):
        for pop in self:
            session = pop.session_ids.filtered(lambda s: s.state in ['opening_control', 'opened', 'closing_control'])
            if session:
                pop.pop_session_username = session[0].user_id.sudo().name
                pop.pop_session_state = session[0].state
                pop.pop_session_duration = (
                    datetime.now() - session[0].start_at
                ).days if session[0].start_at else 0
            else:
                pop.pop_session_username = False
                pop.pop_session_state = False
                pop.pop_session_duration = 0
    
    @api.depends('session_ids')
    def _compute_current_session(self):
        for pop in self:
            session = pop.session_ids.filtered(lambda r: r.user_id.id == self.env.uid and \
                not r.state == 'closed')
            # sessions ordered by id desc
            pop.current_session_id = session and session[0].id or False
            pop.current_session_state = session and session[0].state or False

    def open_session_cb(self):
        """ new session button

        create one if none exist
        access cash control interface if enabled or start a session
        """
        self.ensure_one()
        sesiones_sin_cerrar = self.env['pop.session'].search([('pop_id','=',self.id),('state','!=','closed')])
        if len(sesiones_sin_cerrar) > 0:
            raise UserError(_("Existe una sesion sin cerrar. Refresque la página."))
        else:
            if not self.current_session_id:
                self.current_session_id = self.env['pop.session'].create({
                    'user_id': self.env.uid,
                    'pop_id': self.id
                })
                if self.current_session_id.state == 'opened':
                    return self.open_ui()
                return self._open_session(self.current_session_id.id)
            return self._open_session(self.current_session_id.id)

    def open_existing_session_cb(self):
        """ close session button

        access session form to validate entries
        """
        self.ensure_one()
        return self._open_session(self.current_session_id.id)

    def _open_session(self, session_id):
        return {
            'name': ('Session'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'pop.session',
            'res_id': session_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    @api.model
    def create(self, vals):
        res = super(PopConfig, self).create(vals)
        if not res["journal_ids"].filtered(lambda x: x.type == 'cash'):
            raise ValidationError("Debe informar un diario de tipo 'Efectivo'")
        return res

    def write(self, vals):
        res = super(PopConfig, self).write(vals)
        for rec in self:
            if not rec.journal_ids.filtered(lambda x: x.type == 'cash'):
                raise ValidationError("Debe informar un diario de tipo 'Efectivo'")
        
        return res