import datetime
from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import format_date

class ResCurrency(models.Model):
    _inherit = "res.currency"

    # se sobre-escribe
    # def l10n_ar_action_get_afip_ws_currency_rate(self):
    #     res = super(ResCurrency,self).l10n_ar_action_get_afip_ws_currency_rate()

    # commit e73
    def l10n_ar_action_get_afip_ws_currency_rate(self):
        date, rate = self._get_last_business_day_rate()
        raise UserError(_('Last Business Day') + ': %s' % date + '\n' + _('Rate:') + ' %s' % rate)

    # se sobre-escribe
    # def _l10n_ar_get_afip_ws_currency_rate(self, afip_ws='wsfe'):
    #     res = super(ResCurrency,self)._l10n_ar_get_afip_ws_currency_rate(afip_ws)

    # commit e73
    def _l10n_ar_get_afip_ws_currency_rate(self, afip_ws='wsfe', date_rate=None):
            """ Return the date and rate for a given currency
            This is only for the user so that he can quickly check the last rate on afip por a currency.
            This is really useful. There is a NTH for the future to integrate this with the automtaic currency rates """
            self.ensure_one()
            if not self.l10n_ar_afip_code:
                raise UserError(_('No AFIP code for currency %s. Please configure the AFIP code consulting information in AFIP page', self.name))
            if self.l10n_ar_afip_code == 'PES':
                raise UserError(_('No rate for ARS (is the base currency for AFIP)'))

            connection = self.env.company._l10n_ar_get_connection(afip_ws)
            client, auth = connection._get_client()
            if afip_ws == 'wsfe':
                req_data = {"MonId": self.l10n_ar_afip_code}
                if date_rate:
                    req_data["FchCotiz"] = date_rate.strftime("%Y%m%d")

                response = client.service.FEParamGetCotizacion(auth, **req_data)
                if response.Errors:
                    if response.Errors.Err[0].Code == 602:  # Not found rate for the given date
                        return date_rate, False
                    raise UserError(_('The was an error obtaining the rate:\n\n * Code %s -  %s',
                                    response.Errors.Err[0].Code, response.Errors.Err[0].Msg))

                # Events None
                date = response.ResultGet.FchCotiz
                rate = response.ResultGet.MonCotiz
            elif afip_ws == 'wsfex':
                req_data = {"Mon_id": self.l10n_ar_afip_code}
                if date_rate:
                    req_data["FchCotiz"] = date_rate.strftime("%Y-%m-%d")

                response = client.service.FEXGetPARAM_Ctz(auth, **req_data)
                if response.FEXErr.ErrCode != 0:  # ErrCode is always send, if == 0 everything is ok
                    if response.FEXErr.ErrCode == 1800:  # Not found rate for the given date
                        return date_rate, False

    # es nuevo
    def _get_last_business_day_rate(self, afip_ws='wsfe', from_date=None):
        """ Get last business rate from a given date """
        # Last  ultimo dia habil
        arca_rate = False
        arca_date = False
        max_tries = try_count = 15
        while not arca_rate and try_count:
            arca_date, arca_rate = self._l10n_ar_get_afip_ws_currency_rate(afip_ws, date_rate=from_date)
            if not arca_rate:
                from_date = from_date - relativedelta(days=1)
            try_count -= 1

        if try_count == 0:
            raise UserError(_('Did not find any rate last %s days before the given date (%s)',
                              max_tries, from_date or fields.Date.context_today(self)))

        arca_date = format_date(
            self.env, datetime.datetime.strptime(arca_date, '%Y%m%d'), date_format='EEEE, dd MMMM YYYY')
        return arca_date, arca_rate