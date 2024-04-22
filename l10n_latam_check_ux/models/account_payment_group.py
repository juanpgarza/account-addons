from odoo import models
from odoo.exceptions import UserError, ValidationError

class AccountPaymentGroup(models.Model):
    _inherit = 'account.payment.group'

    def post(self):

        if self.partner_type == 'supplier':
            # solo hago el control en OP
            
            for aj in self.payment_ids.filtered(lambda x: x.payment_method_line_id.code == 'check_printing').mapped('journal_id'):
                # CONTROL DENTRO DE LA MISMA OP
                # el set te elimina los duplicados, entonces si se informó el mismo número de cheque, el tamaño no coincide
                len1 = len(set(self.payment_ids.filtered(lambda x: x.journal_id == aj).mapped('check_number')))

                len2 = len(self.payment_ids.filtered(lambda x: x.journal_id == aj).mapped('check_number'))
                
                if len1 and len and len1 != len2:
                    raise ValidationError("No es posible validar. La OP incluye cheques con numeración duplicada.")
            
            for ap in self.payment_ids.filtered(lambda x: x.payment_method_line_id.code == 'check_printing'):
                # CONTROL CONTRA OTRAS OP
                existe_cheque = self.env['account.payment'].search([]).filtered(lambda x: x.journal_id == ap.journal_id and x.state == 'posted' and x.check_number == ap.check_number and x.id != ap.id)
                if existe_cheque:
                    raise ValidationError("No es posible validar. El cheque Nro {} ya existe en otra OP.".format(ap.check_number))

        res = super(AccountPaymentGroup,self).post()