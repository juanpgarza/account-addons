##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_repr, float_round
from odoo.tools.float_utils import float_compare

class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ar_payment_foreign_currency = fields.Char("Pago en USD?")

    # self.env['account.move'].browse(162923).l10n_ar_check_rate()

    # se modifica
    @api.model
    def wsfe_get_cae_request(self, client=None):
        res = super(AccountMove,self).wsfe_get_cae_request(client)
        res['FeDetReq'][0]['FECAEDetRequest']['CondicionIVAReceptorId'] = self.partner_id.l10n_ar_afip_responsibility_type_id.code

        # hardcode. Las facturas en dolares se pagan siempre en pesos
        # porque si se paga en dolares es más complejo (tengo que informar la cot oficial del USD)
        # uso el mismo nombre de variable que usan en v16,v17, etc
        self.l10n_ar_payment_foreign_currency = "N"
        if res['FeDetReq'][0]['FECAEDetRequest']['MonId'] and res['FeDetReq'][0]['FECAEDetRequest']['MonId'] != 'PES': # WSFE 10241
            res['FeDetReq'][0]['FECAEDetRequest']['CanMisMonExt'] = self.l10n_ar_payment_foreign_currency

        # import pdb; pdb.set_trace()
        # res['FeDetReq'][0]['FECAEDetRequest']['MonCotiz']        
        return res

    # nuevo
    # commit e73
    def l10n_ar_check_rate(self):
        """ If the user indicates that the payment will be done in foreign currency (option YES) then ARCA force that
        the rate used is exactly the same as the last business day (if date in future then do not report the rate)
        We alert the user and show them the correct rate and date so they can fixed in the currency config to continue
        with the invoice validation """
        self.ensure_one()
        afip_ws = self.journal_id.l10n_ar_afip_ws
        if self.currency_id != self.company_currency_id and self.l10n_ar_payment_foreign_currency == "S":
            # import pdb; pdb.set_trace()
            arca_date, arca_rate = self.currency_id._get_last_business_day_rate(afip_ws, self.invoice_date)

            # WSFE 10119 / WSFEX 1667: Extra Show that the rates are out of allowed margin
            min_rate = arca_rate - (arca_rate * 0.02)
            max_rate = arca_rate * 400
            if self.l10n_ar_currency_rate < min_rate or self.l10n_ar_currency_rate > max_rate:
                raise UserError(_(
                    "The currency rate to be reported (%s) is not valid. It must be between 2%% and 400%% of"
                    " the official quote (%s - %s)", float_repr(self.l10n_ar_currency_rate, precision_digits=3),
                    float_repr(min_rate, precision_digits=3), float_repr(max_rate, precision_digits=3)))
            # WSFE 10038 / WSFEX 1604
            if self.l10n_ar_payment_foreign_currency == "S" and float_compare(
               self.l10n_ar_currency_rate, arca_rate, precision_digits=3) != 0:
                raise UserError(_(
                    "The rate to be reported (%s) differs from that of ARCA Remember that if you pay"
                    " in foreign currency you must use the same rate of the last business day of ARCA (%s - %s)",
                    float_repr(self.l10n_ar_currency_rate, precision_digits=3), arca_rate, arca_date))
