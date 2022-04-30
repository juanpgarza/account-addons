# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PopSessionCashIn(models.TransientModel):
    _name = 'pop.session.cash.in'
    _description = 'Ingreso de efectivo'

    # WARNING mig-pop odoo.fields: Field pop.session.cash_register_balance_end: unknown parameter 'digits', 
    # if this is an actual parameter you may want to override the method _valid_field_parameter on the relevant model in order to allow it
    amount = fields.Float(string='Amount', required=True)

    pop_session_id = fields.Many2one('pop.session',string='Sesión')

    description = fields.Char(string='Motivo')

    @api.model
    def default_get(self, field_names):
        defaults = super(
            PopSessionCashIn, self).default_get(field_names)
        defaults['pop_session_id'] = self.env.context['active_id']
        return defaults

    def do_cash_in(self):
        pop_session_journal_id = self.env['pop.session.journal'].search(['&',('pop_session_id','=',self.pop_session_id.id),('journal_id','=',self.pop_session_id.cash_journal_id.id)])

        vals = {
            'ref': self.description, 
            'amount': self.amount,
            'pop_session_journal_id': pop_session_journal_id.id
        }

        self.env['pop.session.journal.line'].create(vals)        

class PopSessionCashOpen(models.TransientModel):
    _name = 'pop.session.cash.open'
    _description = 'Informar saldo inicial'

    def saldo_anterior(self):
        return self.env['pop.session'].browse(self.env.context['active_id']).pop_id.last_closed_session_id.cash_register_balance_end_real

    amount = fields.Float(string='Amount', required=True,default=saldo_anterior)

    pop_session_id = fields.Many2one('pop.session',string='Sesión')

    description = fields.Char(string='Motivo')

    @api.model
    def default_get(self, field_names):
        defaults = super(
            PopSessionCashOpen, self).default_get(field_names)
        defaults['pop_session_id'] = self.env.context['active_id']
        return defaults

    def do_pop_open(self):
        pop_session_journal_id = self.env['pop.session.journal'].search(['&',('pop_session_id','=',self.pop_session_id.id),('journal_id','=',self.pop_session_id.cash_journal_id.id)]).id

        self.env['pop.session.journal'].search([('id','=',pop_session_journal_id)]).write({'balance_start':self.amount})

        return


class PopSessionCashOut(models.TransientModel):
    _name = 'pop.session.cash.out'
    _description = 'Retiro de efectivo'

    amount = fields.Float(string='Amount', required=True)

    pop_session_id = fields.Many2one('pop.session',string='Sesión')

    description = fields.Char(string='Motivo')

    @api.model
    def default_get(self, field_names):
        defaults = super(
            PopSessionCashOut, self).default_get(field_names)
        defaults['pop_session_id'] = self.env.context['active_id']
        return defaults

    def do_cash_out(self):
        pop_session_journal_id = self.env['pop.session.journal'].search(['&',('pop_session_id','=',self.pop_session_id.id),('journal_id','=',self.pop_session_id.cash_journal_id.id)])

        vals = {
            'ref': self.description, 
            'amount': - self.amount, 
            'pop_session_journal_id': pop_session_journal_id.id
        }

        self.env['pop.session.journal.line'].create(vals)
    
class PopSessionCashClose(models.TransientModel):
    _name = 'pop.session.cash.close'
    _description = 'Informar saldo final'

    amount = fields.Float(string='Amount', required=True)

    pop_session_id = fields.Many2one('pop.session',string='Sesión')

    description = fields.Char(string='Motivo')

    @api.model
    def default_get(self, field_names):
        defaults = super(
            PopSessionCashClose, self).default_get(field_names)
        defaults['pop_session_id'] = self.env.context['active_id']
        return defaults

    def do_pop_close(self):
        pop_session_journal_id = self.env['pop.session.journal'].search(['&',('pop_session_id','=',self.pop_session_id.id),('journal_id','=',self.pop_session_id.cash_journal_id.id)]).id

        self.env['pop.session.journal'].search([('id','=',pop_session_journal_id)]).write({'balance_end_real':self.amount})