# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    l10n_latam_check_reject_state = fields.Selection([
        ('no_rejected', 'Normal (No Rechazado)'),
        ('rejected', 'Rechazado por un proveedor'),
        ('rejected_bank', 'Rechazado por el banco'),
        ('reclaimed', 'Reclamado'),
    ],
    default='no_rejected',
    string="Estado del rechazo",
    tracking=True,
    required=True,
    )

    # first_partner_id = fields.Many2one(
    #     'res.partner',
    #     compute='_compute_partners',
    #     string='Empresa de primera operación',
    #     readonly=True,
    #     store=True,
    # )

    # @api.depends('l10n_latam_check_operation_ids.partner_id')
    # def _compute_partners(self):
    #     for rec in self:
    #         if not rec.l10n_latam_check_operation_ids:
    #             # rec.partner_id = False
    #             rec.first_partner_id = rec.partner_id
    #             continue
    #         # operations = rec.l10n_latam_check_operation_ids.sorted()
    #         # import pdb; pdb.set_trace()
    #         # rec.first_partner_id = operations[0].partner_id
    #         # rec.partner_id = operations[0].partner_id

    def _get_operation(self, operation, partner_required=False):
        self.ensure_one()
        op = self.l10n_latam_check_operation_ids.filtered(lambda x: x.state == 'posted' and x.payment_type == 'outbound')        
        # if partner_required:
        #     if not op.partner_id:
        #         raise ValidationError(_(
        #             'The %s (id %s) operation has no partner linked.'
        #             'You will need to do it manually.') % (operation, op.id))
        return op

    def name_get(self):
        """ Add check number to display_name on check_id m2o field """
        res_names = super().name_get()
        for i, (res_name, rec) in enumerate(zip(res_names, self)):
            # import pdb; pdb.set_trace()
            if rec.check_number and rec.payment_method_line_id.code == 'new_third_party_checks':
                # import pdb; pdb.set_trace()
                res_names[i] = (res_name[0], "%s %s" % (res_name[1], _("(Fecha Pago: %s - %s %.2f)", rec.l10n_latam_check_payment_date, rec.currency_id.symbol, rec.amount)))
                
        return res_names

    def reject(self):
        self.ensure_one()
        # obtiene la ultima operación del flujo del cheque de tercero 
        operation = self._get_operation(self.state, True)
        if not operation:
            raise ValidationError("El estado actual del cheque no es válido para esta operación")
        
        self.l10n_latam_check_reject_state = 'rejected'
        return self.action_create_debit_note(
                'rejected', 'supplier', operation.partner_id)

    def reject_bank(self):
        self.ensure_one()
        operation = self._get_operation(self.state, True)
        if not operation:
            raise ValidationError("El estado actual del cheque no es válido para esta operación")
        self.l10n_latam_check_reject_state = 'rejected_bank'
        return

    def claim(self):
        self.ensure_one()
        # if self.state in ['rejected'] and self.type == 'third_check':
        if self.l10n_latam_check_reject_state in ['rejected','rejected_bank']:
            self.l10n_latam_check_reject_state = 'reclaimed'
            # anulamos la operación en la que lo recibimos
            return self.action_create_debit_note(
                'reclaimed', 'customer', self.partner_id)
    
    def action_create_debit_note(
            self, operation, partner_type, partner):
        self.ensure_one()
        action_date = self._context.get('action_date')

        product_id = self.company_id._get_check_product('rejected')

        if partner_type == 'supplier':
            invoice_type = 'in_invoice'
            journal_type = 'purchase'
            tax_ids = [(6, 0, product_id.supplier_taxes_id.ids)]
        else:
            invoice_type = 'out_invoice'
            journal_type = 'sale'
            tax_ids = [(6, 0, product_id.taxes_id.ids)]

        journal = self.env['account.journal'].search([
            ('company_id', '=', self.company_id.id),
            ('type', '=', journal_type),
        ], limit=1)

        # si pedimos rejected o reclamo, devolvemos mensaje de rechazo y cuenta
        # de rechazo
        if operation in ['rejected', 'reclaimed']:
            name = 'Rechazo cheque "%s"' % (self.name)
        else:
            raise ValidationError(_(
                'Debit note for operation %s not implemented!' % (
                    operation)))

        inv_line_vals = {
            'product_id': product_id.id,         
            'price_unit': self.amount,
            'tax_ids': tax_ids,
        }

        inv_vals = {
            # this is the reference that goes on account.move.line of debt line
            # 'name': name,
            # this is the reference that goes on account.move
            'rejected_check_id': self.id,
            'ref': name,
            'invoice_date': action_date,
            'invoice_origin': _('Check nbr (id): %s (%s)') % (self.name, self.id),
            'journal_id': journal.id,
            # this is done on muticompany fix
            # 'company_id': journal.company_id.id,
            'partner_id': partner.id,
            'move_type': invoice_type,
            'invoice_line_ids': [(0, 0, inv_line_vals)],
        }
        if self.currency_id:
            inv_vals['currency_id'] = self.currency_id.id
        # import pdb; pdb.set_trace()
        # we send internal_type for compatibility with account_document
        invoice = self.env['account.move'].with_context(
            company_id=journal.company_id.id, force_company=journal.company_id.id,
            internal_type='debit_note').create(inv_vals)        
        self._add_operation(operation, invoice, partner, date=action_date)

        return {
            'name': name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
        }

    def _add_operation(
            self, operation, origin, partner=None, date=False):
        for rec in self:
            # rec._check_state_change(operation)
            # agregamos validacion de fechas
            date = date or fields.Datetime.now()

        if operation == 'rejected':
            body = ('Nota de débito por rechazo de cheque. Proveedor: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>') % (origin.id, partner.name)
        # elif operation == 'rejected_bank':
        #     body = ('Nota de débito por rechazo de cheque. Proveedor: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>') % (origin.id, partner.name)
        elif operation == 'reclaimed':
            body = ('Nota de débito por reclamo de cheque. Cliente: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>') % (origin.id, partner.name)
        else:
            raise ValidationError("Operación no permitida")
        
        rec.message_post(body=body)
