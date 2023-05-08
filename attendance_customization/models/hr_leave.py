from collections import defaultdict

import pytz
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict
from datetime import datetime, date, time, timedelta
from datetime import date, datetime
from dateutil.relativedelta import relativedelta



class hr_leav_alolcatiin(models.Model):
    _inherit = 'hr.leave.allocation'

    sick_ref=fields.Many2one('hr.sick.leave',string="Ref")

class hr_calendar_leave(models.Model):
    _name = 'hr.calendar.leave'
    _rec_name = 'name'

    name = fields.Char(String="Name")
    follow = fields.Boolean(default=False, string="Active Calender?", help="Only one calender can be active at a time")
    leave = fields.One2many('hr.leave.lineitem', 'new_id_second', String="Leave")

    @api.onchange('follow')
    def _onchange_follow(self):
        if self.follow:
            chk = self.search([('follow', '=', True)])
            if len(chk) >= 1:
                raise UserError(
                    _(
                        'Can only follow one Public holiday calender at a time, Please unfollow the other Calender to activate this.'))


class line_item_two(models.Model):
    _name = 'hr.leave.lineitem'

    new_id_second = fields.Many2one('hr.calendar.leave', string="Type ID")
    leave_name = fields.Char(string="Leave name")
    leave_date = fields.Date(string="Date")


class hr_calendar_leave(models.Model):
    _name = 'hr.sick.leave'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    date_from = fields.Date(required=True, string="Date from")
    date_to = fields.Date(required=True, string="Date To")
    applied = fields.Boolean(default=False)
    state = fields.Selection([
        ('draft', 'draft'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ], string="state", track_visibility='onchange', copy=False, default='draft')

    holiday_status_id = fields.Many2one(
        "hr.leave.type", string="Time Off Type", required=True,
        domain=[('valid', '=', True), ('allocation_type', '!=', 'no')])

    def approve_leave(self):
        if self.employee_id and self.date_from and self.date_to:
            get_attendace = self.env['attendance.custom'].search([('employee_id', '=', self.employee_id.id),
                                                                  ('attendance_date', '>=', self.date_from),
                                                                  ('attendance_date', '<=', self.date_to)])
            if get_attendace:
                for rec in get_attendace:
                    rec.sick_leave = True
                    rec.sick_from=self.date_from
                    rec.sick_to=self.date_to
                    rec.absent=False
                    rec.valid=True
                    rec.state='Validated'
        self.applied = True
        self.state = 'Approved'
        self.create_leave(self.employee_id,self.date_from,self.date_to)


    def create_leave(self, employee,date_from=None, date_to=None):
        date_from = date_from
        date_to = date_to
        days = (date_to - date_from).days
        allocation_values=[]
        if employee and days>0:
            allocation_values.append({
                'name': _('Paid Time Off Allocation'),
                'holiday_status_id': self.holiday_status_id.id,
                'employee_id': self.employee_id.id,
                'number_of_days': days,
                'state':'confirm',
                'sick_ref':self.id
            })
            allocations = self.env['hr.leave.allocation'].create(allocation_values)
            allocations.action_validate()
            # allocations.action_approve()



    def reset_draft(self):
        self.with_context(rjk=True).reject_leave()
        self.state='draft'


    def reject_leave(self):
        if self.employee_id and self.date_from and self.date_to:
            get_attendace = self.env['attendance.custom'].search([('employee_id', '=', self.employee_id.id),
                                                                  ('attendance_date', '>=', self.date_from),
                                                                  ('attendance_date', '<=', self.date_to)])
            if get_attendace:
                for rec in get_attendace:
                    rec.sick_leave = False
                    rec.sick_from = None
                    rec.sick_to = None
                    # rec.absent = True

        self.applied = False
        self.unlink_leave()
        if not self._context.get('rjk'):
           self.state = 'Rejected'

    def unlink_leave(self):
        rec = self.env['hr.leave.allocation'].sudo().search(
            [('employee_id', '=', self.employee_id.id),('sick_ref','=',self.id)])
        for res in rec:
            res.action_refuse()



