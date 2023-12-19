# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HRJob(models.Model):
    _inherit = 'hr.job'
    min_salary = fields.Float(string="Minimum Salary")
    max_salary = fields.Float(string="Maximum Salary")
    description = fields.Text("Description")

    salary_range = fields.Text("Salary Range")
    grade_id = fields.Many2one("grade.grade", "Grade")
    
class RankRank(models.Model):
    _name = "rank.rank"
    _description = "Rank"
    _rec_name = 'job_id'
    name = fields.Char("Position")
    job_id = fields.Many2one('hr.job')
    min_salary = fields.Float(string="Minimum Salary")
    max_salary = fields.Float(string="Maximum Salary")
    description = fields.Text("Description")

    salary_range = fields.Text("Salary Range")
    grade_id = fields.Many2one("grade.grade", "Grade")


class GradeGrade(models.Model):
    _name = "grade.grade"
    _description = "Grade"

    name = fields.Char("Grade")
    description = fields.Text("Description")
    rank_ids = fields.One2many("rank.rank", "grade_id", "Ranks")
    job_ids = fields.Many2many('hr.job')
    criteria = fields.Char()
    
    # Benefit
    vehicle = fields.Char()
    laptop = fields.Boolean()
    mobile = fields.Boolean()
    fuel = fields.Float()
    mobile_allowance = fields.Float()
    attend_allowance = fields.Float(string="Attendance Allowance")
    leaves = fields.Char()
    other = fields.Char()
    # Promotion and config
    promotion_id = fields.One2many('hr.grade.promotion', 'grade_id')
    struct_id = fields.Many2one('hr.payroll.structure', string="Salary Structure")
    allow_late_checkin = fields.Integer(string="Allow Late Checkin")
    checking_grace_period = fields.Integer(string="Checkin Grace Period")
    checking_late_count = fields.Integer(string="Checkin Late Count")
    
    allow_early_checkout = fields.Integer(string="Allow Early Checkout")
    checkout_grace_period = fields.Integer(string="Checkout Grace Period")
    early_checkout_count = fields.Integer(string="Early Checkout Count")
    
    advance_salary_type = fields.Many2one('hr.loan.type', string="Advance Salary Type", domain=[('type','=','advance')])
    loan_salary_type = fields.Many2one('hr.loan.type', string="Employee Loan Type", domain=[('type','=','loan')])


class HRContract(models.Model):
    _inherit='hr.contract'
    
    struct_id = fields.Many2one('hr.payroll.structure', string="Salary Structure")
    grade_id = fields.Many2one('grade.grade', string="Grade")
    rank_id = fields.Many2one('rank.rank', string="Rank")
    attend_allowance = fields.Float(string="Attendance Allowance")
    allow_late_checkin = fields.Integer(string="Allow Late Checkin")
    checking_grace_period = fields.Integer(string="Checkin Grace Period")
    checking_late_count = fields.Integer(string="Checkin Late Count")
    
    allow_early_checkout = fields.Integer(string="Allow Early Checkout")
    checkout_grace_period = fields.Integer(string="Checkout Grace Period")
    early_checkout_count = fields.Integer(string="Early Checkout Count")
    advance_salary_type = fields.Many2one('hr.loan.type', string="Advance Salary Type", domain=[('type','=','advance')])
    loan_salary_type = fields.Many2one('hr.loan.type', string="Employee Loan Type", domain=[('type','=','loan')])
    
    @api.onchange('employee_id')
    def _onchange_employee_gr(self):
        for rec in self:
            rec.grade_id = rec.employee_id.grade_id.id
            rec.rank_id = rec.employee_id.rank_id.id
            rec.job_id = rec.employee_id.job_id.id
    
    @api.onchange("grade_id")
    def onchange_grade(self):
        res = {}
        if self.grade_id:
            self.job_id = False
            res["domain"] = {"job_id": [
                ("id", "in", self.grade_id.job_ids.ids)]}
        return res

    @api.onchange('grade_id')
    def _onchange_grade_id(self):
        for rec in self:
            grade_id = rec.grade_id
            rec.struct_id = grade_id.struct_id.id
            rec.attend_allowance = grade_id.attend_allowance
            rec.allow_late_checkin = grade_id.allow_late_checkin
            rec.checking_grace_period =grade_id.checking_grace_period
            rec.checking_late_count = grade_id.checking_late_count
            rec.allow_early_checkout = grade_id.allow_early_checkout
            rec.checkout_grace_period =grade_id.checkout_grace_period
            rec.early_checkout_count = grade_id.early_checkout_count
            rec.advance_salary_type = rec.grade_id.advance_salary_type
            rec.loan_salary_type = rec.grade_id.loan_salary_type

    def _check_grade_validation(self):
        pass
    @api.model
    def create(self, vals):
        request = super().create(vals)
        if vals.get("wage"):
            pass
        return request

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if not rec.job_id:
                raise UserError(
                    _("Please select Rank.")
                )
            if rec.wage > rec.job_id.max_salary or rec.wage < rec.job_id.min_salary:
                raise UserError(
                    _("Employee wage should be between salary range.")
                )
        return res


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    grade_id = fields.Many2one("grade.grade", "Grade")
    rank_id = fields.Many2one("rank.rank", "Rank")

    @api.onchange("grade_id")
    def onchange_grade(self):
        res = {}
        if self.grade_id:
            self.job_id = False
            res["domain"] = {"job_id": [
                ("id", "in", self.grade_id.job_ids.ids)]}
        return res

class HrGradePromotion(models.Model):
    _name = 'hr.grade.promotion'
    _rec_name = 'name'
    name = fields.Char(required=True)
    department_id = fields.Many2one('hr.department')
    job_id = fields.Many2one('hr.job',string="Designation")
    min_exp = fields.Char(string="MIN. EXPERIENCE")
    xs_exp = fields.Char(string="XTRASOFT EXPERIENCE")
    rel_ind_exp = fields.Char(string="RELEVENT INDUSTRY")
    other_ind_exp = fields.Char(string="OTHER INDUSTRY")
    min_edu = fields.Char(string="MIN. EDUCATION")
    grade_id = fields.Many2one('grade.grade')