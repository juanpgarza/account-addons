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
        default=_get_default_pop_id,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    pop_session_id = fields.Many2one('pop.session', 
        string='Sesión de caja', 
        ondelete='Restrict',
        domain="['&',('pop_id','=',pop_id),('state','=','opened')]",
        readonly=True,
        states={'draft': [('readonly', False)]},        
    )

    pop_session_journal_line_ids = fields.One2many('pop.session.journal.line', 'account_payment_id', string='Renglones de caja')

    pop_session_journal_ids = fields.Many2many(related='pop_session_id.journal_ids')

    journal_id = fields.Many2one('account.journal', domain="[('id','in',pop_session_journal_ids)]")

    # @api.onchange('pop_id','pop_session_id')
    # def onchange_pop_session_id(self):
    #     if self.payment_type != 'transfer':
    #         import pdb; pdb.set_trace()
    #         self.journal_id = self.pop_session_id.journal_ids

    @api.onchange('pop_id')
    def _onchange_pop_id(self):
        # si el usuario cambia la caja, que cargue la sesion activa para esa caja
        self.pop_session_id = self.env['pop.session'].search(['&',('pop_id','=',self.pop_id.id),('state','=','opened')])

    def action_post(self):
        super(AccountPayment,self).action_post()

        for rec in self:
            pop_session_journal_id = self.env['pop.session.journal'].search(['&',('pop_session_id','=',rec.pop_session_id.id),('journal_id','=',rec.journal_id.id)])

            ref = ''
            if rec.payment_type == 'inbound':
                amount = rec.amount
            else:
                amount = - rec.amount
                if rec.partner_type == 'supplier':
                    ref = 'pago a proveedor'

            inbound_payment_method_codes = rec.journal_id.inbound_payment_method_line_ids.mapped('code')

            if 'received_third_check' in inbound_payment_method_codes:
                # cheque de tercero
                if rec.check_bank_id.name and rec.check_payment_date:
                    ref = rec.check_bank_id.name + ' - ' + rec.check_payment_date.strftime("%m/%d/%Y")
            elif 'electronic' in inbound_payment_method_codes:
                # transferencia bancaria
                ref = 'Transferencia '
            elif 'withholding' in inbound_payment_method_codes:
                # retenciones
                if rec.tax_withholding_id and rec.withholding_number:
                    ref = rec.tax_withholding_id.name + ' - ' + rec.withholding_number
            elif 'inbound_credit_card' in inbound_payment_method_codes:
                # tarjeta crédito
                # if rec.nro_lote and rec.nro_cupon:
                #     ref = "Lote: " + str(rec.nro_lote) + " - " + "Cupón: " + rec.nro_cupon
                ref = ''
            elif 'outbound_debit_card' in inbound_payment_method_codes:
                # tarjeta débito
                ref = ''
            else:
                ref = ''

            # if rec.communication != '.' and rec.communication:
            #     ref = ref + ' - ' + rec.communication

            vals = {
                'name': rec.display_name, 
                'amount': amount, 
                'partner_id': self.partner_id.id,
                'ref': ref,
                'account_payment_id': rec.id,
                'pop_session_journal_id': pop_session_journal_id.id
            }

            # rec.pop_session_journal_line_id = 
            self.env['pop.session.journal.line'].create(vals)


    def cancel(self):
        super(AccountPayment,self).cancel()

        if len(self) == 1 and self.payment_type == 'transfer':
            print("nada que anular. Es una transferencia")
        else:
            default_pop_id = self.env.user.default_pop_id

            session_actual = self.env['pop.session'].search([('state','=','opened'),('pop_id','=',default_pop_id.id)])

            if not session_actual:            
                raise UserError(_("Debe iniciar una sesión de la caja '%s', para poder cancelar el recibo." % default_pop_id.name))
            else:

                if len(self) > 0:
                    
                    for rec in self:
                        # solo si el renglon está validado se tiene que anular en la caja
                        if (rec.payment_group_id.state == 'posted'):
                            
                            renglones = self.env['pop.session.journal.line'].search([('account_payment_id','=',rec.id), ('anulado','=',False)])

                            pop_session_journal_id = self.env['pop.session.journal'].search([('journal_id','=',rec.journal_id.id),('pop_session_id.id','=',session_actual.id)])

                            if not pop_session_journal_id:
                                raise UserError(_("El medio de pago '%s', no está habilitado para la caja actual '%s'." % (rec.journal_id.name,default_pop_id.name)))

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