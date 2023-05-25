# -*- coding: utf-8 -*-
{
    'name': "Contract Approval",

    'summary': """
    """,

    'description': """

    """,
    'author': "Muhammad Bilal",

    'website': "https://alifzero.com",

    'category': 'HR',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/activity_data.xml',
        'views/hr_contract_view.xml',
        'views/email.xml',
        'wizards/contract_approval_wizard.xml',
    ],
}
