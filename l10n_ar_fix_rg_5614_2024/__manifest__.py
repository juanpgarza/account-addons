# -*- coding: utf-8 -*-
{
    'name': 'Fix RG 5614/2024 - Discriminación de Impuestos',
    'version': "15.0.1.0.0",
    'summary': 'Extensión para cumplir con la RG 5614/2024, discriminando siempre los impuestos en los reportes.',
    'author': 'Franco Nicolau',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'depends': ['account', 'l10n_ar', 'l10n_ar_ux'],
    'data': [
        'views/report_invoice.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
