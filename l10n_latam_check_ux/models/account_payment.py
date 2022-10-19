# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def name_get(self):
        """ Add check number to display_name on check_id m2o field """
        res_names = super().name_get()
        for i, (res_name, rec) in enumerate(zip(res_names, self)):
            # import pdb; pdb.set_trace()
            if rec.check_number and rec.payment_method_line_id.code == 'new_third_party_checks':
                # import pdb; pdb.set_trace()
                res_names[i] = (res_name[0], "%s %s" % (res_name[1], _("(Fecha Pago: %s - %s %.2f)", rec.l10n_latam_check_payment_date, rec.currency_id.symbol, rec.amount)))
                
        return res_names

