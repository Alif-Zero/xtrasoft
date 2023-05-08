# -*- coding: utf-8 -*-
{
    'name': "odoo_hr",

    'summary': """Mcmaster""",

    'description': """
        Mcmaster module
    """,

    'author': "Waqar",
    'category': "HR",
    'website': "http://www.yourcompany.com",
    'version': '0.1',
    'application': True,
    'installable': True,
    'auto_install': False,
    'depends': ['base',
                'hr',
                'hr_payroll',
                'account',
                'hr_payroll_account',
                'ohrms_overtime'
                ],
    # always loaded
    'data': [
         # HR
        'security/security_groups.xml',
        'security/ir.model.access.csv',

        'hr/hr_loan_views.xml',
        'hr/hr_payroll_views.xml',

        
    ],
    # only loaded in demonstrat,ion mode
    'demo': [

    ],
    'qweb': [
#         'static/src/xml/activity.xml',
    ],
}