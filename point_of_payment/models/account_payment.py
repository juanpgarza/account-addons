# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_default_pop_id(self):
        return self.env.user.default_pop_id.id

    pop_id = fields.Many2one('pop.config',
        string='Caja',
        ondelete='Restrict',
        # readonly=True,
    )

    pop_session_id = fields.Many2one('pop.session',
        string='Sesión de caja',
        ondelete='Restrict',
        # readonly=True,
    )

    pop_session_journal_line_ids = fields.One2many('pop.session.journal.line', 'account_payment_id', string='Renglones de caja')

    pop_session_journal_ids = fields.Many2many(related='pop_session_id.journal_ids')

    def action_post(self):
        super(AccountPayment,self).action_post()

        for rec in self:

            pop_session_id = rec.pop_id.current_session_id

            if rec.is_internal_transfer:
                continue

            ref = ''
            if rec.payment_type == 'inbound':
                amount = rec.amount
            else:
                amount = - rec.amount
                if rec.partner_type == 'supplier':
                    ref = 'pago a proveedor'

            inbound_payment_method_codes = rec.journal_id.inbound_payment_method_line_ids.mapped('code')

            vals = {
                'name': rec.display_name,
                'amount': amount,
                'partner_id': self.partner_id.id,
                'ref': rec._get_payment_ref(ref, inbound_payment_method_codes),
                'account_payment_id': rec.id,
                'pop_session_journal_id': pop_session_id.get_session_journal_id(rec.journal_id).id
            }

            self.env['pop.session.journal.line'].create(vals)

    def _get_payment_ref(self, ref, payment_method_codes):
        if 'manual' in payment_method_codes:
            return ref

    def action_cancel(self):
        super(AccountPayment,self).action_cancel()

        if len(self) == 1 and self.payment_type == 'transfer':
            print("nada que anular. Es una transferencia")
        else:
            pop_id = self.env.user.get_selected_pop_id()
            pop_session_id = pop_id.current_session_id

            if not pop_session_id:
                # raise UserError(_("Debe iniciar una sesión de la caja '%s', para poder cancelar el recibo." % pop_id.name))
                # por ahora lo controlo en account_payment_group
                return True
            else:

                if len(self) > 0:

                    for rec in self:
                        # solo si el renglon está validado se tiene que anular en la caja
                        if (rec.payment_group_id.state == 'posted'):

                            renglones = self.env['pop.session.journal.line'].search([('account_payment_id','=',rec.id), ('anulado','=',False)])

                            pop_session_journal_id = pop_session_id.get_session_journal_id(rec.journal_id)

                            if not pop_session_journal_id:
                                raise UserError(_("El medio de pago '%s', no está habilitado para la caja actual '%s'." % (rec.journal_id.name,pop_id.name)))

                            if len(renglones) > 1:
                                raise UserError(_("Error"))

                            for renglon_caja in renglones:
                                if (renglon_caja.ref):
                                    ref = renglon_caja.ref
                                else:
                                    ref = ''

                                vals = {
                                    'name': renglon_caja.display_name,
                                    'amount': -renglon_caja.amount,
                                    'partner_id': renglon_caja.partner_id.id,
                                    'ref': ref + ' - Cancelación',
                                    'account_payment_id': renglon_caja.account_payment_id.id,
                                    'pop_session_journal_id': pop_session_journal_id.id,
                                    'anulado': True
                                }

                                self.env['pop.session.journal.line'].create(vals)

                                renglon_caja.anulado = True

                        else:
                            print("No tiene que anular en la caja 1.")

                else:
                    print("No tiene que anular en la caja 2.")


    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        pop_id = self.env.user.get_selected_pop_id()
        if pop_id.current_session_state != 'opened':
            raise UserError("Debe iniciar una sesión de la caja {} para continuar".format(pop_id.name))

        # cuando es una transferencia interna, no pasa por el payment_group
        # entonces el payment no toma los valores de pop_id y pop_session_id
        # los tengo que informar si o si porque no encuentro la forma de quitarle el dominio al journal
        # importante a tener en cuenta es que la sesión de caja tiene que tener todos los medios de pago habilitados
        # para mantener la coherencia, me está faltando filtrar el journal destino con los mp habilitados por la caja
        if "is_internal_transfer" in res and res["is_internal_transfer"]:
            res['journal_id'] = False
            res['pop_id'] = pop_id.id
            res['pop_session_id'] = pop_id.current_session_id.id
        return res
