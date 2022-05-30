# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Point of payment",
    "summary": "Introduces concept of point of payment and accounting journal sessions",
    "version": "15.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/juanpgarza/account-addons",
    "author": "juanpgarza",
    "license": "AGPL-3",
    "depends": [
        "account",
        ],
    "data": [
        'security/pop_security.xml',
        'security/ir.model.access.csv',
        'views/account_payment_views.xml',
        'views/pop_config_views.xml',
        'views/pop_session_journal_line_views.xml',
        'views/pop_session_journal_views.xml',
        'views/pop_session_views.xml',
        'views/res_users_views.xml',
        'views/templates.xml',
        'wizards/pop_session_cash.xml',
        'views/menus.xml',
        ],
    "development_status": "Production/Stable",
    "installable": True,
}
