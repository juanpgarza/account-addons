##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, _
from odoo.exceptions import ValidationError


class AccountPaymentLatamCheckWizard(models.TransientModel):
    _name = 'account.payment.latam.check.wizard'
    _description = 'Asistente de rechazo de cheques de terceros'

    date = fields.Date(
        default=fields.Date.context_today,
        required=True,
    )
    action_type = fields.Char(
        'Action type passed on the context',
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()
        if self.action_type not in [
                'claim', 'reject_bank', 'reject']:
            raise ValidationError(_(
                'Action %s not supported on checks') % self.action_type)
        checks = self.env['account.payment'].browse(
            self._context.get('active_ids'))
        for check in checks:
            # if check.l10n_latam_check_current_journal_id.inbound_payment_method_line_ids.payment_method_id.code != 'in_third_party_checks':
            #     raise ValidationError("Operación no válida para cheques en mano")
            res = getattr(
                check.with_context(action_date=self.date), self.action_type)()
        if len(checks) == 1:
            return res
        else:
            return True
