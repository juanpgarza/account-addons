# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PopSession(models.Model):
    _name = 'pop.session'
    _order = 'id desc'
    _description = 'Sesiones de caja'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    POP_SESSION_STATE = [
        ('opening_control', 'CONTROL DE APERTURA'),  # method action_pop_session_open
        ('opened', 'EN PROCESO'),               # method action_pop_session_closing_control
        ('closing_control', 'CONTROL DE CIERRE'),  # method action_pop_session_close
        ('closed', 'CERRADO & PUBLICADO'),
    ]

    pop_id = fields.Many2one(
        'pop.config', string='Caja',
        help="Caja física que usará.",
        required=True,
        index=True)

    name = fields.Char(string='ID de la sesión', required=True, readonly=True, default='/')

    user_id = fields.Many2one(
        'res.users', string='Responsable',
        required=True,
        index=True,
        readonly=True,
        states={'opening_control': [('readonly', False)]},
        default=lambda self: self.env.uid)

    start_at = fields.Datetime(string='Fecha Apertura', readonly=True)
    stop_at = fields.Datetime(string='Fecha Cierre', readonly=True, copy=False)

    state = fields.Selection(
        POP_SESSION_STATE, string='Status',
        required=True, readonly=True,
        index=True, copy=False, default='opening_control',
        tracking=True,)

    journal_ids = fields.Many2many(
        'account.journal',
        related='pop_id.journal_ids',
        readonly=True,
        string='Métodos de pago disponibles')

    _sql_constraints = [('uniq_name', 'unique(name)', "El nombre de esta sesión de caja debe ser único !")]

    pop_session_journal_ids = fields.One2many('pop.session.journal', 'pop_session_id', readonly=True)

    cash_control = fields.Boolean(compute='_compute_cash_all', string='Has Cash Control',default=True,readonly=True, store=True)
    cash_journal_id = fields.Many2one('account.journal', compute='_compute_cash_all', string='Diario de efectivo', store=True)
    cash_register_id = fields.Many2one('pop.session.journal', compute='_compute_cash_all', string='Caja Registradora', store=True)

    cash_register_balance_end_real = fields.Monetary(
        related='cash_register_id.balance_end_real',
        string="Saldo final",
        help="",
        readonly=True)
    cash_register_balance_start = fields.Monetary(
        related='cash_register_id.balance_start',
        string="Saldo inicial",
        help="",
        readonly=True)
    cash_register_total_entry_encoding = fields.Monetary(
        related='cash_register_id.total_entry_encoding',
        string='Total de operaciones en efectivo',
        readonly=True,
        help="")
    cash_register_balance_end = fields.Monetary(
        related='cash_register_id.balance_end',
        # digits=0,
        string="Saldo final teórico",
        help="",
        readonly=True)
    cash_register_difference = fields.Monetary(
        related='cash_register_id.difference',
        string='Diferencia',
        help="",
        readonly=True)

    currency_id = fields.Many2one('res.currency', compute='_compute_currency', string="Currency")

    company_id = fields.Many2one('res.company', related='cash_journal_id.company_id', string='Company', store=True, readonly=True)

    usuario_actual_responsable = fields.Boolean('Usuario actual responsable de la sesión?', compute='_get_usuario_actual_responsable')

    arqueo_inicial_realizado = fields.Boolean('Arqueo realizado',default=False)

    @api.depends()
    def _get_usuario_actual_responsable(self):
        if self.user_id.id == self.env.user.id:
            self.usuario_actual_responsable = True
        else:
            self.usuario_actual_responsable = False

    def _compute_currency(self):
        self.currency_id = self.company_id.currency_id

    @api.depends('pop_id', 'pop_session_journal_ids')
    def _compute_cash_all(self):
        for session in self:
            session.cash_journal_id = session.cash_register_id = session.cash_control = False
            if session.pop_id.cash_control:
                for statement in session.pop_session_journal_ids:
                    if statement.journal_id.type == 'cash' and statement.journal_id.cash_control:
                        session.cash_control = True
                        session.cash_journal_id = statement.journal_id.id
                        session.cash_register_id = statement.id
                        break

    @api.model
    def create(self, values):
        pop_id = values.get('pop_id')
        if not pop_id:
            raise UserError(_("You should assign a Point of Sale to your session."))

        pop_config = self.env['pop.config'].browse(pop_id)
        ctx = dict(self.env.context, company_id=pop_config.company_id.id)

        if not pop_config.journal_ids:
            Journal = self.env['account.journal']
            journals = Journal.with_context(ctx).search([('type', '=', 'cash')])
            if not journals:
                journals = Journal.with_context(ctx).search([('type', '=', 'cash')])
            if not journals:
                raise ValidationError(_("No payment method configured! \nEither no Chart of Account is installed or no payment method is configured for this POS."))
            pop_config.sudo().write({'journal_ids': [(6, 0, journals.ids)]})

        session_name = pop_config.name + pop_config.sequence_id.next_by_id()

        uid = self.env.user.id

        values.update({
            'name': session_name,
            'pop_id': pop_id
        })

        # res = super(PopSession, self.with_context(ctx).sudo(uid)).create(values)
        res = super(PopSession, self.with_context(ctx).with_user(uid)).create(values)

        session_journals = []
        ABS = self.env['pop.session.journal']

        for journal in pop_config.journal_ids:
            ctx['journal_id'] = journal.id
            balance_last_session = pop_config.last_closed_session_id.get_session_journal_id(journal).balance_end_real
            st_values = {
                'journal_id': journal.id,
                'pop_session_id': res.id,
                'balance_start': balance_last_session,
            }

            # session_journals.append(ABS.with_context(ctx).sudo(uid).create(st_values).id)
            session_journals.append(ABS.with_context(ctx).with_user(uid).create(st_values).id)

        values.update({
            'pop_session_journal_ids': [(6, 0, session_journals)]
        })

        return res

    def action_pop_session_open(self):
        if self.pop_id.current_session_state != 'opening_control':
            raise UserError(_("Ya existe una sesión iniciada para esta caja"))

        for session in self.filtered(lambda session: session.state == 'opening_control'):
            # if session.cash_register_balance_start == 0:
            if not session.arqueo_inicial_realizado:
                raise UserError("El arqueo inicial está pendiente")

            values = {}
            if not session.start_at:
                values['start_at'] = fields.Datetime.now()
            values['state'] = 'opened'
            session.write(values)
        return True

    def action_pop_session_closing_control(self):

        for session in self:
            if session.cash_register_balance_end < 0:
                raise UserError(_("El saldo final no puede ser negativo."))
            session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
            if not session.pop_id.cash_control:
                session.action_pop_session_close()

    def action_box_session_back_to_opened(self):
        for session in self:
            session.write({'state': 'opened'})

    def _check_pop_session_balance(self):

        for session in self:
            if session.cash_register_balance_end < 0:
                raise UserError(_("El saldo final no puede ser negativo."))
            if session.cash_register_balance_end != session.cash_register_balance_end_real:
                raise UserError(_("El saldo final teórico debe coincidir con el real. Informe correctamente el saldo real o haga el ajuste correspondiente."))

    def action_pop_session_validate(self):
        self._check_pop_session_balance()
        self.action_pop_session_close()

    def action_pop_session_close(self):
        self.write({'state': 'closed'})

        self.env['pop.config'].browse(self.pop_id.id).write({'last_closed_session_id': self.id})

        return {
            'type': 'ir.actions.client',
            'name': 'Menu Caja',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('point_of_payment.menu_pop_root').id},
        }

    def pop_cash_in(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ingresar Efectivo',
            'view_mode': 'form',
            'res_model': 'pop.session.cash.in',
            'target': 'new'
        }

    def pop_cash_out(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Retirar Efectivo',
            'view_mode': 'form',
            'res_model': 'pop.session.cash.out',
            'target': 'new'
        }

    def pop_cash_open(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Abrir caja',
            'view_mode': 'form',
            'res_model': 'pop.session.cash.open',
            'target': 'new'
        }

    def pop_cash_close(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cerrar caja',
            'view_mode': 'form',
            'res_model': 'pop.session.cash.close',
            'target': 'new'
        }

    def pop_cash_expense(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gastos',
            'view_mode': 'form',
            'res_model': 'pop.session.cash.expense',
            'target': 'new'
        }

    def get_session_journal_id(self, journal_id):
        return self.pop_session_journal_ids.filtered(lambda x: x.journal_id.id == journal_id.id)
