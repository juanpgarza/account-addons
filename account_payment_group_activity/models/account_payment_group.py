from odoo import models

class AccountPaymentGroup(models.Model):
    _name = 'account.payment.group'
    _inherit = ['account.payment.group', 'mail.activity.mixin']


