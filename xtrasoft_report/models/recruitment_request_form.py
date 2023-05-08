from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class recruitmentRequestForm(models.Model):
    _name = 'recruitment.request.form'

    name = fields.Many2one('hr.department', string="Department")
    supervisor_and_title = fields.Char(string="Supervisor And Title")
    date_of_request = fields.Date(string="Date of Request")
    desire_hire_date = fields.Date(string="Desire Hire Date")
    replacement_for = fields.Many2one('hr.employee' ,string="Replacement for")

    # ================ staff ====================



    staff_position = fields.Selection(string='Position',
                                      selection=[('administrative', 'Administrative/Support'),
                                                 ('manager', 'Manager/Supervisor'), ('labor', 'Labor/Helper'),
                                                 ('operation', 'Operation Support'),('finance', 'Finance'),('other', 'Other')])
    proposed_job_type = fields.Char(string="Proposed Job Type")
    department_selection = fields.Many2one('hr.department', string="Department Selection")

    participant_name = fields.Char(string="Participant Name")
    supervisor_name = fields.Char(string="Supervisor")
    alternate = fields.Char(string="Alternate")

    job_description = fields.Text(string="Job Description")

    # ========  fixed term =======

    fixed_term_duration = fields.Char(string='Fixed Term Duration')
    fixed_term_supervisor = fields.Char(string='Fixed Term Supervisor')
    fixed_term_start_date = fields.Date(string="Start Date")
    fixed_term_end_date = fields.Date(string="End Date")
    fixed_term_salary_range = fields.Char(string="Salary Range")
    fixed_term_other = fields.Char(string="Other")


    # ============ Temporary Term ==========

    number_of_days = fields.Integer(string="Number Of Days")
    number_of_weeks = fields.Integer(string="Number Of Weeks")
    number_of_months = fields.Integer(string="Number Of Months")
    temporary_term_start_date = fields.Date(string="Start Date")
    temporary_term_end_date = fields.Date(string="End Date")
    temporary_term_salary_range = fields.Char(string="Salary Range")
    temporary_term_other = fields.Char(string="Other")


    #================  education ================


    education_skills = fields.Text(string="Education/ Skills/ Experience")





