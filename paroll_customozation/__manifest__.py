# -*- coding: utf-8 -*-

{
    'name': 'Payroll Customization',
    'sequence': 1222,
    'version': '1.0',
    'depends': ['mail','base','hr'],
    'category': 'sale','crm'
    'summary': 'Handle lunch orders of your employees',
    'description': """
The base module to manage lunch.
================================
Cost sheet from CRM, Generate Quotation
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/view.xml'
    ],
    'installable': True,
    'application': True,
}
