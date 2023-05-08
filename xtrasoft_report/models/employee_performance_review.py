from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
# from libsaas.services.trello import checklists


class employeePerformanceReview(models.Model):
    _name = 'employee.performance.review'

    name = fields.Many2one('hr.employee', string="Name", required=True)

    # job_title = fields.Char(related='employee_id.job_title', readonly=False)
    # employee_cars_count = fields.Integer(related='employee_id.employee_cars_count')
    # progress = fields.Integer(string='progress')
    progress = fields.Integer(string='Progress',compute='GetNumber')
    department_progress = fields.Integer(string='Department Progress',compute="_cal_department_progress")
    hr_progress = fields.Integer(string='HR Progress',compute="_cal_hr_progress")
    misc_progress = fields.Integer(string='Misc. Progress',compute="_cal_misc_progress")


    # name = fields.Many2one('faculty_id.profile', string="Faculty Name", required=True)
    job_title = fields.Char(string='Job Title', store=True, )
    department = fields.Char(string="Department: ", store=True, )

    #
    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.job_title = self.name.job_title
            self.department = self.name.department_id.name

    month_selection = fields.Selection(string='For The Month Of',
                                       selection=[('january', 'January'), ('february', 'February'), ('march', 'March'),
                                                  ('april', 'April'), ('may', 'May'), ('june', 'June'),
                                                  ('july', 'July'), ('august', 'August'), ('september', 'September'),
                                                  ('october', 'October'), ('november', 'November'),
                                                  ('december', 'December')])
    review_period = fields.Date(string="Review Period")
    date_today = fields.Date('Date of Attendance', default=fields.Date.today, readonly=True)
    department_checklist_ids=fields.One2many('quality.checklist','department_review_id','Department Incharge')
    hr_checklist_ids=fields.One2many('quality.checklist','hr_review_id','HR Section')
    misc_checklist_ids=fields.One2many('quality.checklist','misc_review_id','Misc. Section')
    
    @api.depends('department_checklist_ids')
    def _cal_department_progress(self):
        for each in self:
            total_points=0
            for rec in each.department_checklist_ids:
                total_points+=int(rec.decision)
            if each.department_checklist_ids:
                each.department_progress=total_points/len(each.department_checklist_ids)
            else:
                each.department_progress=0
    
    @api.depends('hr_checklist_ids')
    def _cal_hr_progress(self):
        for each in self:
            total_points=0
            for rec in each.hr_checklist_ids:
                total_points+=int(rec.decision)
            if each.hr_checklist_ids:
                each.hr_progress=total_points/len(each.hr_checklist_ids)
            else:
                each.hr_progress=0
    
    @api.depends('misc_checklist_ids')
    def _cal_misc_progress(self):
        for each in self:
            total_points=0
            for rec in each.misc_checklist_ids:
                total_points+=int(rec.decision)
            if each.misc_checklist_ids:
                each.misc_progress=total_points/len(each.misc_checklist_ids)
            else:
                each.misc_progress=0
                
    @api.onchange('date_today')
    def _get_department_checklist(self):
        if self.date_today:
            if not self.department_checklist_ids:
                checklist_obj=self.env['quality.checklist.criteria'].search([('section','=','Department Incharge')])
                for checklist in checklist_obj:
                    checklist_vals={
                                    'criteria_id':checklist.id,
                                    'department_review_id':self.id,
                                    'section':'Department Incharge'}
                    self.env['quality.checklist'].sudo().create(checklist_vals)
    
    @api.onchange('date_today')
    def _get_hr_checklist(self):
        if self.date_today:
            if not self.hr_checklist_ids:
                checklist_obj=self.env['quality.checklist.criteria'].search([('section','=','HR Section')])
                for checklist in checklist_obj:
                    checklist_vals={
                                    'criteria_id':checklist.id,
                                    'hr_review_id':self.id,
                                    'section':'HR Section'}
                    self.env['quality.checklist'].sudo().create(checklist_vals)
    
    @api.onchange('date_today')
    def _get_misc_checklist(self):
        if self.date_today:
            if not self.misc_checklist_ids:
                checklist_obj=self.env['quality.checklist.criteria'].search([('section','=','Other Options')])
                for checklist in checklist_obj:
                    checklist_vals = {
                                    'criteria_id':checklist.id,
                                    'misc_review_id':self.id,
                                    'section':'Other Options'}
                    self.env['quality.checklist'].sudo().create(checklist_vals)
    
    job_knowledge = fields.Selection(string='Job Knowledge',
                                     selection=[('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'),
                                                ('excellent', 'Excellent')])

    job_knowledge_comment = fields.Char(string="Comments")

    work_quality = fields.Selection(string='Work Quality',
                                    selection=[('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'),
                                               ('excellent', 'Excellent')])
    work_quality_comment = fields.Char(string="Comments")

    attendance = fields.Selection(string='Attendance/Punctuality',
                                  selection=[('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'),
                                             ('excellent', 'Excellent')])
    attendance_comment = fields.Char(string="Comments")

    reporting = fields.Selection(string='Reporting',
                                 selection=[('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'),
                                            ('excellent', 'Excellent')])
    reporting_comment = fields.Char(string="Comments")

    communication = fields.Selection(string='Communication/Listening Skills',
                                     selection=[('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'),
                                                ('excellent', 'Excellent')])
    communication_comment = fields.Char(string="Comments")

    response = fields.Selection(string='Response',
                                selection=[('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'),
                                           ('excellent', 'Excellent')])
    response_comment = fields.Char(string="Comments")

    overall_rating = fields.Selection(string='Overall Rating',
                                      selection=[('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'),
                                                 ('excellent', 'Excellent')])
    additional_comment = fields.Char(string="Comments")

    @api.depends('department_progress','hr_progress','misc_progress')
    def GetNumber(self):
        for each in self:
            each.progress = (each.department_progress+each.hr_progress+each.misc_progress)/3
            

        # if self.job_knowledge_comment == 'poor':
        #     self.progress = 25
        # if self.job_knowledge_comment == 'fair':
        #     self.progress = 50
        # if self.job_knowledge_comment == 'good':
        #     self.progress = 75
        # if self.job_knowledge_comment == 'excellent':
        #     self.progress = 100


        # self.progress = 10
class QualityChecklistCategory(models.Model):
    _name='quality.checklist.category'
    name=fields.Char('Category',required=True)
    
class QualityChecklistCriteria(models.Model):
    _name='quality.checklist.criteria'
    name=fields.Char('Criteria',required=True)
    section=fields.Selection([('Department Incharge','Department Incharge'),('HR Section','HR Section'),('Other Options','Other Options')],'Section',required=True)
    
    _sql_constraints = [
        ('unique_criteria', 'unique (name,section)', 'Name and section should be unique !'),
    ]
class QualityChecklist(models.Model):
    _name='quality.checklist'
#     category_id=fields.Many2one('quality.checklist.category','Category',required=True)
    criteria_id=fields.Many2one('quality.checklist.criteria','Criteria')
    decision=fields.Selection(selection=[('25', 'Poor'), ('50', 'Fair'), ('75', 'Good'),
                                                ('100', 'Excellent')],string='Decision')
    comments=fields.Char('Comments')
    section=fields.Selection([('Department Incharge','Department Incharge'),('HR Section','HR Section'),('Other Options','Other Options')],'Section')
    department_review_id=fields.Many2one('employee.performance.review','Department Review')
    hr_review_id=fields.Many2one('employee.performance.review','HR Review')
    misc_review_id=fields.Many2one('employee.performance.review','Misc. Review')
