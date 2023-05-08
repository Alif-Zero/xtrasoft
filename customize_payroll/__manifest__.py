# -*- coding: utf-8 -*-


{
    'name': 'Customize Payroll',
    'version': '14.0.1.0.0',
    'author': "Ali",
    'category': 'Payroll',
    'depends': ['to_attendance_device', 'hr_payroll','odoo_hr'],
    'data': [
        'views/hr_payslip.xml',
        'views/reporting_views.xml',
        'security/ir.model.access.csv',
#         'data/salary_rule.xml'
#         'data/cron.xml',
#         'data/salary_rule.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
