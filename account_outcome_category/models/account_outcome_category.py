from lxml import etree
from odoo import models, fields

class AccountOutcomeCategory1(models.Model):
    _name = 'account.outcome.category1'
    _description = 'Categoría de gasto 1'

    name = fields.Char('Nombre')
    active = fields.Boolean(default=True)


class AccountOutcomeCategory2(models.Model):
    _name = 'account.outcome.category2'
    _description = 'Categoría de gasto 2'

    name = fields.Char('Nombre')
    active = fields.Boolean(default=True)
