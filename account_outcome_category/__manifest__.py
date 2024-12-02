# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Clasificación de facturas de compras",
    "version": "15.0.1.1.0",
    "category": "Accounting",
    "website": "https://github.com/juanpgarza/account-addons",
    "author": "juanpgarza",
    "license": "AGPL-3",
    "depends": 
        [
            "account",
        ],
    "data": 
        [
            "views/account_move_view.xml",
            "views/account_outcome_category_views.xml",
            'security/ir.model.access.csv',
        ],
    "installable": False,
}
