# -*- coding: utf-8 -*-
{
    'name': "Basic Salary Mass Update",

    'summary': """
       Basic Salary Mass Update""",

    'description': """
        Basic Salary Mass Update, Update Contracts Wage Quickly, Employees Update Basic salary
    """,

    'author': "Kaizen Principles",
    'website': "https://erp-software.odoo-saudi.com/discount/",

    'category': 'HR',
    'version': '.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract.xml',
        'wizard/salary_update_wizard.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,

}
