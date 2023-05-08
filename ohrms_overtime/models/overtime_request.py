# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date

from dateutil import relativedelta
import pandas as pd
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY

class InheritHRAttendance1(models.Model):
    _inherit = 'hr.attendance'

    overtime_id = fields.Many2one('hr.overtime', 'Overtime', compute='GetOverTime')
    approved_hours = fields.Float(related='overtime_id.days_no_tmp', string='Approved Hours')

    @api.onchange('overtime_id','worked_hours','check_in','check_out')
    def GetOverTime(self):
        import pytz
        for rec in self:
            recs = self.env['hr.overtime'].search([('employee_id', '=', rec.employee_id.id)])
            for rec_oveertime in recs:
                tz1 = pytz.timezone('UTC')
                tz2 = pytz.timezone('Asia/Karachi')
                dt = tz1.localize(rec_oveertime.date_from)
                dt = dt.astimezone(tz2)
                if dt.date()  == rec.attendance_date:
                    rec.overtime_id = rec_oveertime.id
                    rec.GetVariance()
            if rec.overtime_id:
                if rec.variance <= rec.overtime_id.days_no_tmp:
                    rec.overtime_id.days_no_tmp_1 = rec.variance
                else:
                    rec.overtime_id.days_no_tmp_1 = rec.overtime_id.days_no_tmp
                rec.GetVariance()
                rec.overtime_id._get_hour_amount()

class OverTimeTemplate(models.Model):
    _name='overtime.template'
    _rec_name = 'department_id'

    department_id=fields.Many2one('hr.department','Department',required=1)
    type=fields.Selection([('cash','Cash'),('leave','Leave')],required=1,default='cash')
    duration_type=fields.Selection([('hours','Hours'),('days','Days')],required=1,default='hours')
    status=fields.Selection([('Draft','Draft'),('Submitted','Submitted'),('Approved','Approved')],default='Draft')
    date=fields.Datetime(string='Date',required=1,default=date.today() )
    # overtime_type_id=fields.Many2one('overtime.type',required=1)
    overtime_ids=fields.One2many('hr.overtime','template_id')
    hours=fields.Float(string='Hours')
    
    def _default_overtime_type_id(self):
        return self.env['overtime.type'].search([('name', '=', 'cash hour')], limit=1).id

    overtime_type_id=fields.Many2one('overtime.type', index=True,required=1, default=_default_overtime_type_id)

    def GetEmployees(self):
        self.overtime_ids=False
        for line in self.env['hr.employee'].search([('department_id','=',self.department_id.id)]):
            self.env['hr.overtime'].create({'employee_id':line.id,'type':self.type,'duration_type':self.duration_type,'date_from':self.date,'overtime_type_id':self.overtime_type_id.id,'template_id':self.id,'days_no_tmp':self.hours})

    def SetConfirmed(self):
        self.status='Submitted'
        for request in self.overtime_ids.filtered(lambda x:x.overtime==False):
            request.unlink()
        if not self.overtime_ids:
            raise ValidationError('Atleast one overtime line required')
        for request in self.overtime_ids:
            request.state='f_approve'

    def SetApproved(self):
        self.status='Approved'
        for request in self.overtime_ids:
            request.state='approved'

class HrOverTime(models.Model):
    _name = 'hr.overtime'
    _description = "HR Overtime"
    _inherit = ['mail.thread']


    template_id=fields.Many2one('overtime.template')

    # rule_line_ids = fields.One2many('overtime_type_id', 'type_line_id')

    # over_time_rules_ids = fields.Many2one('rule_line_ids.rule_line_ids')
    # over_time_rules_idswww = fields.Float(related='over_time_rules_ids.from_hrs')

    def _get_employee_domain(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        domain = [('id', '=', employee.id)]
        if self.env.user.has_group('hr.group_hr_user'):
            domain = []
        return domain

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.onchange('days_no_tmp')
    def _onchange_days_no_tmp(self):
        self.days_no = self.days_no_tmp

    overtime=fields.Boolean(string='Valid')
    name = fields.Char('Name', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain=_get_employee_domain, default=lambda self: self.env.user.employee_id.id,
                                  required=True)
    department_id = fields.Many2one('hr.department', string="Department",
                                    related="employee_id.department_id")
    job_id = fields.Many2one('hr.job', string="Job", related="employee_id.job_id")
    manager_id = fields.Many2one('res.users', string="Manager",
                                 related="employee_id.parent_id.user_id", store=True)
    current_user = fields.Many2one('res.users', string="Current User",
                                   related='employee_id.user_id',
                                   default=lambda self: self.env.uid,
                                   store=True)
    current_user_boolean = fields.Boolean()
    #     project_id = fields.Many2one('project.project', string="Project")
    #     project_manager_id = fields.Many2one('res.users', string="Project Manager")
    contract_id = fields.Many2one('hr.contract', string="Contract",
                                  related="employee_id.contract_id",
                                  )
    date_from = fields.Datetime('Overtime Date')
    date_to = fields.Datetime('Date to')
    #     days_no_tmp = fields.Float('Hours', compute="_get_days", store=True)
    days_no_tmp = fields.Float('Hours')
    days_no_tmp_1 = fields.Float('Hours', store=True)
    days_no = fields.Float('No. of Days')
    desc = fields.Text('Description')
    state = fields.Selection([('draft', 'Draft'),
                              ('f_approve', 'Waiting'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')], string="state",
                             default="draft")
    cancel_reason = fields.Text('Refuse Reason')
    leave_id = fields.Many2one('hr.leave.allocation',
                               string="Leave ID")
    attchd_copy = fields.Binary('Attach A File')
    attchd_copy_name = fields.Char('File Name')
    type = fields.Selection([('cash', 'Cash'), ('leave', 'leave')], default="leave", required=True, string="Type")
    overtime_type_id = fields.Many2one('overtime.type', domain="[('type','=',type),('duration_type','=', "
                                                               "duration_type)]")
    public_holiday = fields.Char(string='Public Holiday', readonly=True)
    attendance_ids = fields.Many2many('hr.attendance', string='Attendance')
    work_schedule = fields.One2many(
        related='employee_id.resource_calendar_id.attendance_ids')
    global_leaves = fields.One2many(
        related='employee_id.resource_calendar_id.global_leave_ids')
    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days')], string="Duration Type", default="hours",
                                     required=True)
    cash_hrs_amount = fields.Float(string='Overtime Amount', readonly=True)
    cash_day_amount = fields.Float(string='Overtime Amount', readonly=True)
    payslip_paid = fields.Boolean('Paid in Payslip', readonly=True)
    # rate_val = fields.Float(store=True)

    # @api.depends('current_user')
    # def check_current_user(self):
    # for i in self:
    # if self.env.user.id == self.employee_id.user_id.id:
    #     i.update({
    #         'current_user_boolean': True,
    #     })

    @api.onchange('employee_id')
    def _get_defaults(self):
        for sheet in self:
            if sheet.employee_id:
                sheet.update({
                    'department_id': sheet.employee_id.department_id.id,
                    'job_id': sheet.employee_id.job_id.id,
                    'manager_id': sheet.sudo().employee_id.parent_id.user_id.id,
                })

    #     @api.depends('project_id')
    #     def _get_project_manager(self):
    #         for sheet in self:
    #             if sheet.project_id:
    #                 sheet.update({
    #                     'project_manager_id': sheet.project_id.user_id.id,
    #                 })

    #     @api.depends('date_from', 'date_to')
    #     def _get_days(self):
    #         for recd in self:
    #             if recd.date_from and recd.date_to:
    #                 if recd.date_from > recd.date_to:
    #                     raise ValidationError('Start Date must be less than End Date')
    #         for sheet in self:
    #             if sheet.date_from and sheet.date_to:
    #                 start_dt = fields.Datetime.from_string(sheet.date_from)
    #                 finish_dt = fields.Datetime.from_string(sheet.date_to)
    #                 s = finish_dt - start_dt
    #                 difference = relativedelta.relativedelta(finish_dt, start_dt)
    #                 hours = difference.hours
    #                 minutes = difference.minutes
    #                 days_in_mins = s.days * 24 * 60
    #                 hours_in_mins = hours * 60
    #                 days_no = ((days_in_mins + hours_in_mins + minutes) / (24 * 60))
    #
    #                 diff = sheet.date_to - sheet.date_from
    #                 days, seconds = diff.days, diff.seconds
    #                 hours = days * 24 + seconds // 3600
    #                 sheet.update({
    #                     'days_no_tmp': hours if sheet.duration_type == 'hours' else days_no,
    #                 })
    @api.onchange('overtime_type_id','days_no_tmp_1')
    def _get_hour_amount(self):
        rate_val = 0

        cash_hrs_rate = self.overtime_type_id.rule_line_ids
        for rec in cash_hrs_rate:
            print(rec.from_hrs , self.days_no_tmp_1 , self.days_no_tmp_1 , rec.to_hrs)
            if self.days_no_tmp_1>0:
                if rec.from_hrs <= self.days_no_tmp_1 or self.days_no_tmp_1 >= rec.to_hrs:
                    rate_val = rec.hrs_amount
                else:
                    raise UserError(_("Please define hourly rate."))

        # print()
        if self.days_no_tmp_1>0 and self.duration_type == 'hours':
            if self.contract_id.over_hour:
                cash_amount = self.contract_id.over_hour * self.days_no_tmp_1 * rate_val
                self.cash_hrs_amount = cash_amount
            else:
                raise UserError(_("Hour Overtime Needs Hour Wage in Employee Contract."))
        elif self.days_no_tmp and self.duration_type == 'days':
            if self.contract_id.over_day:
                cash_amount = self.contract_id.over_day * self.days_no_tmp
                self.cash_day_amount = cash_amount
            else:
                raise UserError(_("Day Overtime Needs Day Wage in Employee Contract."))

    def submit_to_f(self):
        # notification to employee
        recipient_partners = [(4, self.current_user.partner_id.id)]
        body = "Your OverTime Request Waiting Finance Approve .."
        msg = _(body)
        # if self.current_user:
        #     self.message_post(body=msg, partner_ids=recipient_partners)

        # notification to finance :
        group = self.env.ref('account.group_account_invoice', False)
        recipient_partners = []
        # for recipient in group.users:
        #     recipient_partners.append((4, recipient.partner_id.id))

        body = "You Get New Time in Lieu Request From Employee : " + str(
            self.employee_id.name)
        msg = _(body)
        # self.message_post(body=msg, partner_ids=recipient_partners)
        return self.sudo().write({
            'state': 'f_approve'
        })

    # def approve(self):
    #     return self.sudo().write({
    #         'state': 'approved',
    #     })

    def approve(self):
        if self.overtime_type_id.type == 'leave':
            if self.duration_type == 'days':
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type.id,
                    'number_of_days': self.days_no_tmp,
                    'notes': self.desc,
                    'holiday_type': 'employee',
                    'employee_id': self.employee_id.id,
                    'state': 'validate',
                }
            else:
                day_hour = self.days_no_tmp / HOURS_PER_DAY
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type.id,
                    'number_of_days': day_hour,
                    'notes': self.desc,
                    'holiday_type': 'employee',
                    'employee_id': self.employee_id.id,
                    'state': 'validate',
                }
            holiday = self.env['hr.leave.allocation'].sudo().create(
                holiday_vals)
            self.leave_id = holiday.id

        # notification to employee :
        recipient_partners = [(4, self.current_user.partner_id.id)]
        body = "Your Time In Lieu Request Has been Approved ..."
        msg = _(body)
        # self.message_post(body=msg, partner_ids=recipient_partners)
        return self.sudo().write({
            'state': 'approved',

        })

        # return {
        #     'name': _('Leave Adjust'),
        #     'context': {'default_til_id': self.id},
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'leave.adjust',
        #     'view_id': self.env.ref('leave_management.leave_adjust_wizard_view',
        #                             False).id,
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'target': 'new',
        # }

    def reject(self):

        self.state = 'refused'
        # return {
        #     'name': _('Refuse Business Trip'),
        #     'context': {'default_overtime_id': self.id},
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'refuse.wzrd',
        #     'view_id': self.env.ref('leave_management.refuse_wzrd_view',
        #                             False).id,
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'target': 'new',
        # }

    @api.constrains('date_from')
    def _check_date(self):
        for req in self:
            domain = [
                ('date_from', '=', req.date_from),
                ('employee_id', '=', req.employee_id.id),
                ('id', '!=', req.id),
                ('state', 'not in', ['refused']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_(
                    'You can not have 2 Overtime requests that overlaps on same day!'))

    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('hr.overtime') or '/'
        values['name'] = seq
        return super(HrOverTime, self.sudo()).create(values)

    def unlink(self):
        for overtime in self.filtered(
                lambda overtime: overtime.state != 'draft'):
            raise UserError(
                _('You cannot delete TIL request which is not in draft state.'))
        return super(HrOverTime, self).unlink()


#     @api.onchange('date_from', 'date_to', 'employee_id')
#     def _onchange_date(self):
#         holiday = False
#         if self.contract_id and self.date_from and self.date_to:
#             for leaves in self.contract_id.resource_calendar_id.global_leave_ids:
#                 leave_dates = pd.date_range(leaves.date_from, leaves.date_to).date
#                 overtime_dates = pd.date_range(self.date_from, self.date_to).date
#                 for over_time in overtime_dates:
#                     for leave_date in leave_dates:
#                         if leave_date == over_time:
#                             holiday = True
#             if holiday:
#                 self.write({
#                     'public_holiday': 'You have Public Holidays in your Overtime request.'})
#             else:
#                 self.write({'public_holiday': ' '})
#             hr_attendance = self.env['hr.attendance'].search(
#                 [('check_in', '>=', self.date_from),
#                  ('check_in', '<=', self.date_to),
#                  ('employee_id', '=', self.employee_id.id)])
#             self.update({
#                 'attendance_ids': [(6, 0, hr_attendance.ids)]
#             })


class HrOverTimeType(models.Model):
    _name = 'overtime.type'
    _description = "HR Overtime Type"

    name = fields.Char('Name')
    type = fields.Selection([('cash', 'Cash'),
                             ('leave', 'Leave ')])

    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days')], string="Duration Type", default="hours",
                                     required=True)
    leave_type = fields.Many2one('hr.leave.type', string='Leave Type', domain="[('id', 'in', leave_compute)]")
    leave_compute = fields.Many2many('hr.leave.type', compute="_get_leave_type")
    rule_line_ids = fields.One2many('overtime.type.rule', 'type_line_id')

    @api.onchange('duration_type')
    def _get_leave_type(self):
        dur = ''
        ids = []
        if self.duration_type:
            if self.duration_type == 'days':
                dur = 'day'
            else:
                dur = 'hour'
            leave_type = self.env['hr.leave.type'].search([('request_unit', '=', dur)])
            for recd in leave_type:
                ids.append(recd.id)
            self.leave_compute = ids


class HrOverTimeTypeRule(models.Model):
    _name = 'overtime.type.rule'
    _description = "HR Overtime Type Rule"

    type_line_id = fields.Many2one('overtime.type', string='Over Time Type')
    name = fields.Char('Name', required=True)
    from_hrs = fields.Float('From', required=True)
    to_hrs = fields.Float('To', required=True)
    hrs_amount = fields.Float('Rate', required=True)
