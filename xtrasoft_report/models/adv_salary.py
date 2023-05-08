from odoo import api, models, fields, _
from odoo.exceptions import ValidationError





class advanceSalaray(models.Model):
    _name = 'adv.salary.form'

    name = fields.Many2one('hr.employee' )
    adv_salary_form = fields.Many2one('adv.salary.form.main')
    department_name = fields.Many2one('hr.department', string="Department")
    adv_salary = fields.Integer(string="Advance Amount")
    # user_id = fields.Many2one('hr.department', string='User', track_visibility='onchange', readonly=True,
    #                           default=lambda self: self.env.department)

#
class advanceSalarayMain(models.Model):
    _name = 'adv.salary.form.main'



    adv_salary_form_main = fields.One2many('adv.salary.form', 'adv_salary_form' , string='Advance Salary Form')

