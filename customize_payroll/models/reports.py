# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models

class DepartmentSalaryCosting(models.Model):
    _name = "department.salary.costing"
    _description = "Department Salary Costing"
    _auto = False
    date_from=fields.Date('Date From')
    date_to=fields.Date('Date To')
    month=fields.Char('Month')
    department_id=fields.Many2one('hr.department','Department')
    employee_id=fields.Many2one('hr.employee','Employee')
    category=fields.Char('Category Name')
    category_total=fields.Float('Category Total')
    total_amount=fields.Float('Total Amount')
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
            SELECT
                row_number() OVER (PARTITION BY true) AS id,
                hr_payslip.date_from,
                hr_payslip.date_to,
                TO_CHAR(hr_payslip.date_to, 'Month') as month,
                (select department_id from hr_employee where id=hr_payslip.employee_id) as department_id,
                hr_payslip.employee_id as employee_id,
                hr_payslip_line.name as category,
                hr_payslip_line.total as category_total,
                hr_payslip.total_amount as total_amount
            from 
                hr_payslip inner join hr_payslip_line on
                hr_payslip.id=hr_payslip_line.slip_id
            )''' % (self._table,)
            )