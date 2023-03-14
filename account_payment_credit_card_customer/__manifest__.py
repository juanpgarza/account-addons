# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Credit Card Customer",
    "summary": "",
    "version": "15.0.1.0.0",
    "category": "Account",
    "website": "https://github.com/juanpgarza/account-addons",
    "author": "juanpgarza",
    "license": "AGPL-3",
    "depends": [
        "account",
        "account_payment_group",
        ],
    "data": [
        # 'data/account_payment_method_data.xml',
        'security/ir.model.access.csv',
        'views/account_journal_views.xml',
        'views/account_payment_views.xml',
        'views/account_payment_plan_tarjeta_views.xml',        
        ],
    "installable": True,
}
