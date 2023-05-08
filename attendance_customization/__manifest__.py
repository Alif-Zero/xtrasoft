# -*- coding: utf-8 -*-

{
    'name': 'Attendance Customization',
    'sequence': 1222,
    'version': '1.0',
    'depends': ['mail', 'base', 'hr_payroll', 'product', 'sale', 'hr','hr_holidays'],
    'category': 'sale', 'crm'
                        'summary': 'Handle lunch orders of your employees',
    'description': """
The base module to manage lunch.
================================
Cost sheet from CRM, Generate Quotation
    """,
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/view.xml',
        'views/leave.xml',
        'views/hr_emp.xml',
        'views/import_data.xml',
        'views/hr_emp_define.xml',
        'wizard/invalid_attend_wiz.xml',

        'wizard/daily_attendence.xml',
        # 'report/emp_cost_report.xml',
        'report/attendance_summery.xml',
        'wizard/attend_summery_wiz.xml',
        'report/empcsotxls.xml',

        'wizard/create_attend_wiz.xml',
        'views/sick_leave.xml',
        'wizard/valid_attend_wiz.xml',
        'views/view_logs.xml',
        'wizard/ot_monthly_report.xml',

        'report/department_wise_attendence_report.xml',
        'wizard/dept_wise_attend_wiz.xml'

    ],
    'installable': True,
    'application': True,
}
