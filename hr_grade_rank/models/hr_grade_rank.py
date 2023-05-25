# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class RankRank(models.Model):
    _name = "rank.rank"
    _description = "Rank"

    name = fields.Char("Position")
    description = fields.Text("Description")
    salary_range = fields.Text("Salary Range")
    grade_id = fields.Many2one("grade.grade", "Grade")


class GradeGrade(models.Model):
    _name = "grade.grade"
    _description = "Grade"

    name = fields.Char("Grade")
    description = fields.Text("Description")
    rank_ids = fields.One2many("rank.rank", "grade_id", "Ranks")
    job_position = fields.Many2many('hr.job')
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
    # Promotion 
    promotion_id = fields.One2many('hr.grade.promotion', 'grade_id')
    struct_id = fields.Many2one('hr.payroll.structure', string="Salary Structure")


class HRContract(models.Model):
    _inherit='hr.contract'
    
    struct_id = fields.Many2one('hr.payroll.structure', string="Salary Structure")
    grade_id = fields.Many2one('grade.grade', string="Grade")
    rank_id = fields.Many2one('rank.rank', string="Rank")
    attend_allowance = fields.Float(string="Attenance Allowance")
    
    @api.onchange('employee_id')
    def _onchange_employee_gr(self):
        for rec in self:
            rec.grade_id = rec.employee_id.grade_id.id
            rec.rank_id = rec.employee_id.rank_id.id
    
    @api.onchange('grade_id')
    def _onchange_grade_id(self):
        for rec in self:
            rec.struct_id = rec.grade_id.struct_id.id
            rec.attend_allowance = rec.grade_id.attend_allowance
class HrEmployee(models.Model):
    _inherit = "hr.employee"

    grade_id = fields.Many2one("grade.grade", "Grade")
    rank_id = fields.Many2one("rank.rank", "Rank")

    @api.onchange("grade_id")
    def onchange_grade(self):
        res = {}
        if self.grade_id:
            self.rank_id = False
            res["domain"] = {"rank_id": [
                ("id", "in", self.grade_id.rank_ids.ids)]}
        return res

class HrGradePromotion(models.Model):
    _name = 'hr.grade.promotion'
    _rec_name = 'department_id'
    name = fields.Char()
    department_id = fields.Many2one('hr.department')
    job_id = fields.Many2one('hr.job',string="Designation")
    min_exp = fields.Char(string="MIN. EXPERIENCE")
    xs_exp = fields.Char(string="XTRASOFT EXPERIENCE")
    rel_ind_exp = fields.Char(string="RELEVENT INDUSTRY")
    other_ind_exp = fields.Char(string="OTHER INDUSTRY")
    min_edu = fields.Char(string="MIN. EDUCATION")
    grade_id = fields.Many2one('grade.grade')