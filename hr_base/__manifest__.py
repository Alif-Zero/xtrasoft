# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "HR Base",
    'summary': """ HR Base
    
    Added two new fields in employee form view Joining Date & Leaving Date.
    HR Admin
employee
employee admin
employee management
human resource admin
hr
hr manager
hr administration
human resource
admin
admnistration
admin manager
Employee grade
job position
hrm
grade
payslip
salary
timesheet
calendar
Attendance
Appraisal
Employee Letter
Passport Management
Payroll
assessments employees
employees assessments
designation
key area
strength
review
development
evolution
assessment
monitor timeline
employee expense
expense
reimbursement
employee expense reimbursement
employee travel bill reimbursement
register employee expense
employee expense on payslip
Amount refunded for costs incurred
payroll manager
monthly salary
Employee Expense Reimburse
Expense Manager
Post Journal Entries
Payslip Calculation
reimburse
airfare reimbursement
flight ticket
flight ticket reimbursement
airfare allowance
    
    
    """,
    'description': """Joining Date and Leaving date For Employee""",
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr','hr_payroll','hr_holidays'],
    'data': [
        'views/hr_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'demo': [],
    'images': [
        'static/description/main_screen.jpg'
    ],
    'installable': True,
    'auto_install': False,
}
