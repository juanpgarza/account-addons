# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from odoo import models, api

class AccountPaymentGroup(models.Model):
    _inherit = 'account.payment.group'

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "form":
            order_xml = etree.XML(res["arch"])
            partner_id_fields = order_xml.xpath("//field[@name='partner_id']")            
            if partner_id_fields:
                partner_id_field = partner_id_fields[1]
                domain = partner_id_field.get("domain", "[]").replace(
                    "[", "[('payment_selectable', '=', True),"
                )
                partner_id_field.attrib["domain"] = domain
                res["arch"] = etree.tostring(order_xml)
        return res

