##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    rejected_check_produc_id = fields.Many2one(
        'product.product',
        'Servicio para cheques rechazados',
    )

    def _get_check_product(self, check_type):
        self.ensure_one()
        if check_type == 'rejected':
            # account = self.rejected_check_account_id
            if not self.rejected_check_produc_id:
                raise ValidationError("Debe informar el servicio (Concepto) a utilizar en el Rechazo de Cheques de Terceros (Parámetro de la companía) ")
            product = self.rejected_check_produc_id
        return product