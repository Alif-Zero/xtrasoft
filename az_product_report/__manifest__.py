# -*- coding: utf-8 -*-
{
    'name': 'Product Report',
    'version': '14.0.1.',
    'summary': 'Product Move Report',
    'description': '',
    'author': 'Muhammad Bilal',
    'company': 'Alif Zero',
    'website': 'https://alifzero.com',
    'depends': ['base', 'stock'],
    'category': 'Sale',
    'data': [
            'security/ir.model.access.csv',
            'wizard/product_report_wizard.xml',
            'report/product_report.xml',
            'report/product_report_template.xml',
        ],
    'license': 'AGPL-3',
}
