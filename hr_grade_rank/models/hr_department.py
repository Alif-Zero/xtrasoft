from odoo import models, api, fields, _ 




class HRDepartment(models.Model):
    _inherit = 'hr.department'

    total_capicity = fields.Integer(string="Capicity")
    total_employee = fields.Integer(string="Employees", compute="_compute_employee_count")
    required_employee = fields.Integer(string="Required Employees", compute="_compute_employee_count")


    def _compute_employee_count(self):
        for rec in self:
            employee = self.env['hr.employee'].search_count([('department_id', '=', rec.id)])
            rec.total_employee = employee
            rec.required_employee = rec.total_capicity - employee