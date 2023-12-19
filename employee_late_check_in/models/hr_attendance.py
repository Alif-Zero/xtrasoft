# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from pytz import timezone, UTC
import pytz
from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    #
    # late_check_in = fields.Integer(string="Late Check-in(Minutes)")
    # early_check_out = fields.Integer(string="Early Check-out(Minutes)")

    late_check_in = fields.Integer(string="Late Check-in(Minutes)", compute="get_late_minutes")
    early_check_out = fields.Integer(string="Early Check-out(Minutes)", compute="get_early_minutes")

    @api.onchange('check_in', 'status')
    def get_late_minutes(self):
        for rec in self:
            rec.late_check_in = 0.0
            if rec.check_in and rec.status!='Holiday':
                week_day = rec.sudo().check_in.weekday()
                if rec.employee_id.contract_id:
                    work_schedule = rec.sudo().employee_id.contract_id.resource_calendar_id
                    for schedule in work_schedule.sudo().attendance_ids:
                        if schedule.dayofweek == str(week_day) and schedule.day_period == 'morning':
                            work_from = schedule.hour_from
                            if rec.time_start:
                                work_from = rec.time_start
                            else:
                                rec.time_start = schedule.hour_from
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))
    
                            user_tz = self.env.user.tz
                            dt = rec.check_in
    
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                            str_time = dt.strftime("%H:%M")
                            check_in_date = datetime.strptime(str_time, "%H:%M").time()
                            start_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                            t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                            if check_in_date > start_date:
                                final = t1 - t2
                                rec.sudo().late_check_in = final.total_seconds() / 60
    
    @api.onchange('check_out','status')
    def get_early_minutes(self):
        for rec in self:
            rec.early_check_out = 0.0
            if rec.check_out and rec.status!='Holiday':
                week_day = rec.sudo().check_out.weekday()
                if rec.employee_id.contract_id:
                    work_schedule = rec.sudo().employee_id.contract_id.resource_calendar_id
                    for schedule in work_schedule.sudo().attendance_ids:
                        if schedule.dayofweek == str(week_day) and schedule.day_period == 'afternoon':
                            work_to = schedule.hour_to
                            if rec.time_end:
                                work_to = rec.time_end
                            else:
                                rec.time_end = schedule.hour_to
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_to * 60, 60))
                            user_tz = self.env.user.tz
                            dt = rec.check_out
    
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                            str_time = dt.strftime("%H:%M")
                            check_out_date = datetime.strptime(str_time, "%H:%M").time()
                            end_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_out_date.hour, minutes=check_out_date.minute)
                            t2 = timedelta(hours=end_date.hour, minutes=end_date.minute)
                            if check_out_date < end_date:
                                final = t2 - t1
                                rec.sudo().early_check_out = final.total_seconds() / 60
                            

    def late_check_in_records(self):
        self.env['late.check_in'].sudo().search([]).unlink()
        existing_records = self.env['late.check_in'].sudo().search([]).attendance_id.ids
        minutes_after = int(self.env['ir.config_parameter'].sudo().get_param('late_check_in_after')) or 0
        late_check_in_ids = self.sudo().search([('status','=','Present')])
        for rec in late_check_in_ids:
            if rec.late_check_in > minutes_after:
                self.env['late.check_in'].sudo().create({
                    'employee_id': rec.employee_id.id,
                    'late_minutes': rec.late_check_in,
                    'date': rec.check_in.date(),
                    'attendance_id': rec.id,
                })
    
    def early_check_out_records(self):
        self.env['early.check_out'].sudo().search([]).unlink()
        existing_records = self.env['early.check_out'].sudo().search([]).attendance_id.ids
        minutes_after = int(self.env['ir.config_parameter'].sudo().get_param('early_check_out_before')) or 0
        early_check_out_ids = self.sudo().search([('status','=','Present')])
        for rec in early_check_out_ids:
            early_check_out = rec.sudo().early_check_out
            if rec.early_check_out > minutes_after:
                self.env['early.check_out'].sudo().create({
                    'employee_id': rec.employee_id.id,
                    'early_minutes': rec.early_check_out,
                    'date': rec.check_in.date(),
                    'attendance_id': rec.id,
                })
                


