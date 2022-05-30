# Copyright 2022 juanpgarza - Juan Pablo Garza <juanp@juanpgarza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Integrate point of payment with payment group (by adhoc)",
    "summary": "",
    "version": "15.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/juanpgarza/account-addons",
    "author": "juanpgarza",
    "license": "AGPL-3",
    "depends": [
        "point_of_payment",
        "account_payment_group",
        ],
    "data": [
        'views/account_payment_group_views.xml',
        ],
    "installable": True,
}
