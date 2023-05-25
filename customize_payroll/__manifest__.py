# -*- coding: utf-8 -*-


{
    'name': 'Customize Payroll',
    'version': '14.0.1.0.0',
    'author': "Ali",
    'category': 'Payroll',
    'depends': ['to_attendance_device', 'hr_payroll','odoo_hr', 'hr_grade_rank'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip.xml',
        'views/reporting_views.xml',
        'views/payslip_period_views.xml',
        'views/hr_payslip_run_views.xml',
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
