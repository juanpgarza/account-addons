from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_vat_contained_amount(self):
        """ Calcula el total de IVA contenido en la factura """
        self.ensure_one()
        vat_taxes = self.line_ids.filtered(lambda l: l.tax_line_id and l.tax_line_id.tax_group_id.l10n_ar_vat_afip_code)
        amount = sum(vat_taxes.mapped('balance')) * -1

        # Usar el tipo de cambio guardado en la factura si aplica
        if self.currency_id != self.company_id.currency_id and self.l10n_ar_currency_rate:
            amount = amount / self.l10n_ar_currency_rate

        return amount

    def _get_other_indirect_taxes(self):
        """ Calcula el total de otros impuestos nacionales indirectos en la factura """
        self.ensure_one()
        other_taxes = self.line_ids.filtered(lambda l: l.tax_line_id and l.tax_line_id.tax_group_id.l10n_ar_tribute_afip_code == '99')
        amount = sum(other_taxes.mapped('balance')) * -1

        # Usar el tipo de cambio guardado en la factura si aplica
        if self.currency_id != self.company_id.currency_id and self.l10n_ar_currency_rate:
            amount = amount / self.l10n_ar_currency_rate

        return amount
