# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "l10n_latam_check_ux",
    "summary": "",
    "version": "15.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/juanpgarza/account-addons",
    "author": "juanpgarza",
    "license": "AGPL-3",
    "depends": [
        "l10n_latam_check",
        ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/account_check_action_wizard_view.xml',
        'views/account_payment_view.xml',
        'views/company.xml',
        ],
    "installable": True,
}
