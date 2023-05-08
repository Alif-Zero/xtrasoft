# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import datetime as dt
from datetime import datetime
from datetime import datetime, date, time, timedelta
from datetime import date, datetime
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from pytz import timezone

import datetime
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


# class UserAttendance_inherit(models.Model):
#     _inherit = 'user.attendance'
#
#     user_id = fields.Many2one('attendance.device.user', string='Device User', ondelete='cascade', index=True)
#     employee_id = fields.Many2one('hr.employee', string='Employee', index=True)
#


class department(models.Model):
    _inherit = 'hr.department'

    st_checkin = fields.Char(string='Check In')
    st_checkout = fields.Char(string='Checkout')
    grace_time = fields.Char(string='Grace Time')

    @api.onchange('st_checkin')
    def onchange_checkin(self):
        if self.st_checkin:
            try:
                datetime.datetime.strptime(self.st_checkin, '%H:%M')
            except:
                raise ValidationError(_("FFollow Correct Format 00:00"))

    @api.onchange('st_checkout')
    def onchange_checkout(self):
        if self.st_checkout:
            try:
                datetime.datetime.strptime(self.st_checkout, '%H:%M')
            except:
                raise ValidationError(_("RFollow Correct Format 00:00"))

    @api.onchange('grace_time')
    def onchange_grace_time(self):
        if self.st_checkout:
            try:
                datetime.datetime.strptime(self.grace_time, '%H:%M')
            except:
                raise ValidationError(_("VFollow Correct Format 00:00"))


class Employee(models.Model):
    _inherit = 'hr.employee'

    st_checkin = fields.Char(string='Check In')
    st_checkout = fields.Char(string='Checkout')
    grace_time = fields.Char(string='Grace Time')

    @api.onchange('st_checkin')
    def onchange_checkin(self):
        if self.st_checkin:
            try:
                datetime.datetime.strptime(self.st_checkin, '%H:%M')
            except:
                raise ValidationError(_("GFollow Correct Format 00:00"))

    @api.onchange('st_checkout')
    def onchange_checkout(self):
        if self.st_checkout:
            try:
                datetime.datetime.strptime(self.st_checkout, '%H:%M')
            except:
                raise ValidationError(_("BFollow Correct Format 00:00"))

    @api.onchange('grace_time')
    def onchange_grace_time(self):
        if self.st_checkout:
            try:
                datetime.datetime.strptime(self.grace_time, '%H:%M')
            except:
                raise ValidationError(_("NFollow Correct Format 00:00"))

    @api.onchange('department_id')
    def onchange_dept(self):
        if self.department_id:
            self.st_checkin = self.department_id.st_checkin
            self.st_checkout = self.department_id.st_checkout
            self.grace_time = self.department_id.grace_time


class checkins_all(models.Model):
    _name = 'check.ins'

    check = fields.Char(string='Check In')
    timestamp = fields.Datetime(string='Date', required=True, index=True)
    status = fields.Selection([('checkin', 'Check-in'),
                               ('checkout', 'Check-out')], string='Status', default='Check-in')
    att_cus = fields.Many2one('attendance.custom', ondelete='cascade')
    note = fields.Char(string="Note")

    def get_local_time(self, atten_time):
        if atten_time:
            atten_time = datetime.strptime(
                atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            local_tz = pytz.timezone(
                self.env.user.partner_id.tz or 'GMT')
            local_dt = local_tz.localize(atten_time, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            atten_time = datetime.strptime(
                utc_dt, "%Y-%m-%d %H:%M:%S")
            # atten_time = fields.Datetime.to_string(atten_time)
        return atten_time

    @api.onchange('timestamp')
    def onchng_timestamp(self):
        if self.timestamp:
            # utc_timestamp = self.convert_time_to_utc(self.timestamp, self.env.user.tz)
            # str_utc_timestamp = fields.Datetime.to_datetime(fields.Datetime.to_string(utc_timestamp))
            # timestamp=str_utc_timestamp
            # self.check = self.get_minute_hmformat(
            #     timestamp.second + (timestamp.hour * 60 * 60)+ timestamp.hour * 60)
            self.status = 'checkin'
            msg = _("changed the Check Ins %s") % str(self.env.user.name)
            self.att_cus.message_notify(subject="Check Ins changed", body=msg)

    # def get_minute_hmformat(self, seconds):
    #     seconds = seconds % (24 * 3600)
    #     hour = seconds // 3600
    #     seconds %= 3600
    #     minutes = seconds // 60
    #     seconds %= 60
    #
    #     return "%d:%02d" % (hour+3, minutes)


class checkouts_all(models.Model):
    _name = 'check.outs'

    check = fields.Char(string='Check out')
    timestamp = fields.Datetime(string='Date', required=True, index=True)
    status = fields.Selection([('checkin', 'Check-in'),
                               ('checkout', 'Check-out')], string='Status')
    att_cus = fields.Many2one('attendance.custom', ondelete='cascade')
    note = fields.Char(string="Note")

    def get_local_time(self, atten_time):
        if atten_time:
            atten_time = datetime.strptime(
                atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            local_tz = pytz.timezone(
                self.env.user.partner_id.tz or 'GMT')
            local_dt = local_tz.localize(atten_time, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            atten_time = datetime.strptime(
                utc_dt, "%Y-%m-%d %H:%M:%S")
            # atten_time = fields.Datetime.to_string(atten_time)
        return atten_time

    @api.onchange('timestamp')
    def onchng_timestamp(self):
        if self.timestamp:
            # utc_timestamp = self.convert_time_to_utc(self.timestamp, self.env.user.tz)
            # str_utc_timestamp = fields.Datetime.to_datetime(fields.Datetime.to_string(utc_timestamp))
            # timestamp = str_utc_timestamp
            # self.check = self.get_minute_hmformat(
            #     timestamp.second + (timestamp.hour * 60 * 60) + timestamp.hour * 60)
            self.status = 'checkout'
            msg = _("changed the Check outs %s") % str(self.env.user.name)
            self.att_cus.message_notify(subject="Check out changed", body=msg)
            # self.att_cus.message_post(body=msg)

    # def get_minute_hmformat(self, seconds):
    #     seconds = seconds % (24 * 3600)
    #     hour = seconds // 3600
    #     seconds %= 3600
    #     minutes = seconds // 60
    #     seconds %= 60
    #
    #     return "%d:%02d" % (hour+3, minutes)


class Attendance(models.Model):
    _name = 'attendance.custom'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    employee_id = fields.Many2one('hr.employee', required=True)
    roll_number = fields.Char(related='employee_id.identification_id')

    is_modif = fields.Boolean(string="Is modification")
    note = fields.Char(string="Note")

    attendance_date = fields.Date(string='Attendance Date', required=True, default=fields.Date.context_today)
    job_title = fields.Char(string='Job Title', compute='get_jobtitle')
    status = fields.Char(string='Status')
    custom_ID = fields.Char(string='ID')
    title = fields.Char(string='Title')
    a_stat = fields.Char(string='Status', default="A")

    first_check_in = fields.Char(string='Check In(1st)')
    first_check_out = fields.Char(string='Check Out(1st)')
    first_shift_total_hours = fields.Char(string='Hrs(1st)')
    working = fields.Char(string='Working', track_visibility='always')
    second_check_in = fields.Char(string='Check In(2nd)')
    second_check_out = fields.Char(string='Check Out(2nd)')
    second_shift_total_hours = fields.Char(string='Hrs(2nd)')
    job_code = fields.Char(string='JobCode')
    site = fields.Char(string='Site')
    late_in = fields.Char(string='Late In')
    early_in = fields.Char(string='Early In')
    early_out = fields.Char(string='Early Out')
    ot_125 = fields.Char(string='OT 1.25', track_visibility='always')
    ot_15 = fields.Char(string='OT 1.5', track_visibility='always')
    has_ot = fields.Boolean(default=False)
    no_attend = fields.Char(string='No Attend')
    ignored = fields.Char(string='Ingored')
    exception_approved = fields.Boolean(string='Exception Approved')
    apply_latein_deduction = fields.Boolean(string='Apply Latein deduction')
    sick_leave = fields.Boolean(string="Sick leave", default=False)
    absent = fields.Boolean(string="Absent")
    sick_from = fields.Date(string="Leave From")
    sick_to = fields.Date(string="Leave To")
    leave = fields.Boolean(string="leave", default=False)
    leave_from = fields.Date(string="Leave From")
    leave_to = fields.Date(string="Leave To")

    Emerg = fields.Boolean(string="Emergency leave", default=False)
    emerg_from = fields.Date(string="Emergency From")
    # emerg_to = fields.Date(string="Emergency To")

    Unpaid = fields.Boolean(string="un-paid leaves", default=False)
    unpaid_from = fields.Date(string="Un-paid From")
    unpaid_to = fields.Date(string="Un-paid To")

    Mater = fields.Boolean(string="Maternity Leaves", default=False)
    mater_from = fields.Date(string="Maternity From")
    mater_to = fields.Date(string="Maternity To")

    Busi = fields.Boolean(string="Buissness Leaves", default=False)
    busi_from = fields.Date(string="Buissness From")
    busi_to = fields.Date(string="buissness To")

    check_ot_lunch = fields.Boolean(default=False, string="Allow OT Lunch")
    allow_viewotf = fields.Boolean("allow", compute='chk_allowed', default=False)
    allow_viewoto = fields.Boolean("allow", compute='chk_allowed', default=False)

    check_ot_normal = fields.Boolean(default=False, string="Allow OT Normal")

    # first_shift_record = fields.Many2one('hr.attendance', string="First shift record", readonly=1, )
    # second_shift_record = fields.Many2one('hr.attendance', string="second shift record", readonly=1, )

    valid = fields.Boolean(default=True, string="Valid", track_visibility='always')

    first_check_in_input = fields.Char(string='Enter Check In(1st)')
    first_check_out_input = fields.Char(string='Enter Check Out(1st)')

    second_check_in_input = fields.Char(string='Enter Check In(2nd)')
    second_check_out_inputt = fields.Char(string='Enter Check Out(2nd)')

    check_ins = fields.One2many('check.ins', 'att_cus', string="Check ins")
    check_outs = fields.One2many('check.outs', 'att_cus', string="Check outs")
    is_bonus_day = fields.Boolean('isbonus', default=False)
    project_id=fields.Many2one('project.project',"Project")


    options = fields.Selection([
        ('Absent', 'Absent'),
        ('Apply Shift', 'Apply Shift'),
        ('New Time', 'New Time'),
    ], string="Options", track_visibility='onchange', copy=False, )

    state = fields.Selection([
        ('Modify', 'Modify'),
        ('Validated', 'Validated'),
    ], string="State", track_visibility='onchange', copy=False, )

    def send_notif(self, msg):
        for rec in self:
            if rec.env.user.id not in [1, 2]:
                allowed = rec.env.ref('attendance_customization.attendance_Modifier')
                user = rec.env['res.users'].search([('groups_id', '=', allowed.id)])
                if rec.env.user.id in user.ids:

                    purchase_user = rec.env['res.users'].search([('name', '=', 'Raouf Nasser')])
                    notification_ids = []
                    # thread_pool = rec.env['mail.thread']
                    for purchase in purchase_user:
                        # notification_ids.append((0, 0, {
                        #     'res_partner_id': purchase.partner_id.id,
                        #     'notification_type': 'inbox'}))

                        # post_vars = {'subject': "Attendance Checks Changed",
                        #              'body': str(rec.employee_id.name) + " of date " + str(
                        #                  rec.attendance_date or "N\A") + " " + msg,
                        #              'partner_ids': purchase.partner_id.ids, }
                        self.env['attendance.logs.changes'].sudo().create(
                            {
                                'timestamp': fields.datetime.now(),
                                'date': rec.attendance_date,
                                'manager': purchase.id,
                                'responsible': rec.env.user.id,
                                'att_cus': rec.id,
                                'note': "" + str(rec.employee_id.name) + " of date " + str(
                                    rec.attendance_date or "N\A") + " " + msg + " ",

                            }
                        )
                else:
                    raise UserError(
                        "You are not allowed to Modify attendance records.Please Contact your system administrator")
                    #
                    # rec.message_post(type="notification", subtype="mt_comment", **post_vars)

                    # self.message_notify(
                    #     subject='Punches in Attendance has been changed',
                    #     body=str(rec.employee_id.name)+" of date "+str(rec.attendance_date or "N\A")+" " + msg,
                    #     partner_ids=purchase.partner_id.ids,
                    # )

        # self.message_post(body=str(self.employee_id.name)+" of date "+str(self.attendance_date or "N\A")+" " + msg, message_type='notification',
        #                   subtype='mail.mt_comment', author_id=self.env.user.partner_id.id,
        #                   notification_ids=notification_ids)

    def create_shift_rec(self, schedule, type):
        vals = self.get_dict(self.get_minute_hmformat(schedule.seconds-10800), type)
        return vals

    @api.constrains('options')
    def options_change(self):
        if self.options == 'Absent':
            self.absent = True
            self.state = 'Validated'
            self.valid = True
        elif self.options == 'Apply Shift':
            vals = []
            day = self.attendance_date.strftime('%A')
            if len(self.check_ins) == 1 and len(self.check_outs) == 0:
                schedule = self.get_schedule_ot(self.employee_id, day)
                if schedule.get('fso') not in [False, None]:
                    schedule_fso = schedule.get('fso')
                    schedule_si = schedule.get('ssi')
                    schedule_so = schedule.get('ssc')

                    vals.append(self.create_shift_rec(schedule_fso, 'checkout'))
                    vals.append(self.create_shift_rec(schedule_si, 'checkin'))
                    vals.append(self.create_shift_rec(schedule_so, 'checkout'))
                    for rec in vals:
                        if rec.get('status') == 'checkin':
                            self.check_ins |= self.check_ins.new(
                                rec
                            )
                        else:
                            self.check_outs |= self.check_outs.new(
                                rec
                            )

                    self.get_ot_hours()
                    self.valid = True
                    self.is_modif = False
                    self.state = 'Validated'
                    self.absent = False

                    schedule = schedule.get('ssc')

                print(schedule)


            elif len(self.check_ins) == 2 and len(self.check_outs) == 1:
                schedule = self.get_schedule_ot(self.employee_id, day)
                if schedule.get('ssc') not in [False, None]:
                    schedule = schedule.get('ssc')
                    vals = self.get_dict(self.get_minute_hmformat(schedule.seconds-10800), 'checkout')
                    self.check_outs |= self.check_outs.new(
                        vals
                    )
                    self.get_ot_hours()
                    self.valid = True
                    self.is_modif = False
                    self.state = 'Validated'
                    self.absent=False


                    print(schedule)

        elif self.options == 'New Time':
            self.validate_record()
        self.send_notif('Options have Changed')

    def get_dict(self, timestamp, stat):
        return {
            'timestamp': str(self.attendance_date) + " " + str(timestamp),
            'check': timestamp,
            'att_cus': self.id,
            'status': stat
        }

    def get_time(self, x):
        if x:

            if x.hour < 7:
                hours = "0" + str(x.hour)
            else:
                hours = x.hour
            if x.minute < 10:
                minut = "0" + str(x.minute)
            else:
                minut = x.minute

            if x.hour >= 24 and minut >= 59:
                return str(23) + ':' + str(minut)
            elif x.hour >= 24:
                return str(23) + ':' + str(minut)

            return str(hours) + ':' + str(minut)

    def validate_record(self):
        ins = self.check_ins
        outs = self.check_outs
        if len(ins) == len(outs):
            self.state = 'Validated'
            self.is_modif = False
            self.absent=False
            self.valid=True
            day = self.attendance_date.strftime('%A')
            emp_working = self.get_schedule_ot(self.employee_id, day)
            if ins:
                self.apply_latein(emp_working['fsi'], (ins[0].timestamp))

        else:
            raise UserError("Record is not valid")

    def calc_total_working_hours(self, ins, outs):
        seconds = 0
        if ins and outs:
            for inc, out in zip(ins, outs):
                diff = out.timestamp - inc.timestamp
                seconds += diff.seconds

        return self.get_minute_hmformat(seconds)

    @api.onchange('check_ins', 'check_outs', 'check_ins.timestamp', 'check_outs.timestamp')
    def onchn_chkin_chkout(self):
        ins = self.check_ins
        outs = self.check_outs
        if self.env.user.id not in [1, 2]:
            self.send_notif('Punches have Changed')

        # self.working = self.calc_total_working_hours(ins, outs)
        self.get_ot_hours()

        if len(ins) == len(outs):
            self.valid = True
            self.is_modif = False
            self.state = 'Validated'
        else:
            self.valid = False
            self.is_modif = True
            self.state = 'Modify'
            # self.absent=True

    def cron_update_latein(self):
        recs = self.search([])
        for rec in recs:
            ins = rec.check_ins
            if ins:
                day = rec.attendance_date.strftime('%A')
                emp_working = rec.get_schedule_ot(rec.employee_id, day)
                if ins:
                    rec.apply_latein(emp_working['fsi'], ins[0].timestamp)

    @api.onchange('first_check_in_input', 'first_check_out_input', 'second_check_in_input', 'second_check_out_inputt')
    def onchn_fciix(self):
        if self.first_check_in_input and self.first_check_out_input:
            try:
                time_obj_first_check_in = datetime.datetime.strptime(self.first_check_in_input, '%H:%M')
                self.first_check_in = str(time_obj_first_check_in.hour) + ':' + str(
                    time_obj_first_check_in.minute)

                time_obj_first_check_out = datetime.datetime.strptime(self.first_check_out_input, '%H:%M')
                self.first_check_out = str(time_obj_first_check_out.hour) + ':' + str(
                    time_obj_first_check_out.minute)


            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

        if self.second_check_in_input and self.second_check_out_inputt:
            try:
                time_obj_first_check_in = datetime.datetime.strptime(self.second_check_in_input, '%H:%M')
                self.second_check_in = str(time_obj_first_check_in.hour) + ':' + str(
                    time_obj_first_check_in.minute)

                time_obj_first_check_in = datetime.datetime.strptime(self.second_check_out_inputt, '%H:%M')
                self.second_check_out = str(time_obj_first_check_in.hour) + ':' + str(
                    time_obj_first_check_in.minute)


            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

    # @api.onchange('first_check_out_input')
    # def onchn_fcoix(self):
    #
    #
    #
    # @api.onchange('second_check_in_input')
    # def onchn_sciix(self):
    #
    #
    #
    # @api.onchange('second_check_out_inputt')
    # def onchn_scoix(self):

    @api.constrains('first_shift_record', 'second_shift_record')
    def get_fci(self):
        for rec in self:
            if rec.first_shift_record.check_in and rec.first_shift_record.check_out:
                rec.first_check_in = str(rec.first_shift_record.check_in.hour) + ':' + str(
                    rec.first_shift_record.check_in.minute)
                rec.first_check_out = str(rec.first_shift_record.check_out.hour) + ':' + str(
                    rec.first_shift_record.check_out.minute)
            else:
                rec.first_check_in = "00:00"
                rec.first_check_out = "00:00"
            if rec.second_shift_record.check_in and rec.second_shift_record.check_out:
                rec.second_check_in = str(rec.second_shift_record.check_in.hour) + ':' + str(
                    rec.second_shift_record.check_in.minute)
                rec.second_check_out = str(rec.second_shift_record.check_out.hour) + ':' + str(
                    rec.second_shift_record.check_out.minute)
            else:
                rec.second_check_in = "00:00"
                rec.second_check_out = "00:00"

    # @api.constrains('second_shift_record')
    # def onchn_ssr(self):
    #     for rec in self:
    #         if rec. second_shift_record:
    #             rec.second_check_in=str(rec.second_shift_record.check_in.hour)+':'+str(rec.second_shift_record.check_in.minute)
    #             rec.second_check_out=str(rec.second_shift_record.check_out.hour)+':'+str(rec.second_shift_record.check_out.minute)
    #

    def chk_allowed(self):
        log_usr = self.env.user.id
        for dec in self:
            allow_viewotf = False
            allow_viewoto = False
            get_rec = dec.env['hr.define.emp'].search([('employee_id', '=', log_usr)])
            if get_rec:
                for rec in get_rec.members:
                    if rec.employee_id.id == dec.employee_id.id and dec.ot_15:
                        allow_viewotf = True

                    if rec.employee_id.id == dec.employee_id.id and dec.ot_125:
                        allow_viewoto = True
            if allow_viewotf:
                dec.allow_viewotf = True
            else:
                dec.allow_viewotf = False

            if allow_viewoto:
                dec.allow_viewoto = True
            else:
                dec.allow_viewoto = False

    @api.onchange('leave')
    def onchn_lev(self):
        if self.leave:
            self.a_stat = "V"

    @api.onchange('Emerg')
    def onchn_Emerg(self):
        if self.Emerg:
            self.a_stat = "G"

    @api.onchange('Unpaid')
    def onchn_lUnpaid(self):
        if self.Unpaid:
            self.a_stat = "O"

    @api.onchange('sick_leave')
    def onchn_sick_leave(self):
        if self.sick_leave:
            self.a_stat = "S"
            # self.send_notif('Applied Sick Leave')

    @api.model
    def create(self, vals):
        attend = super(Attendance, self).create(vals)
        check = self.search([('employee_id', '=', attend.employee_id.id), ('sick_leave', '=', True)])
        for rec in check:
            if rec.attendance_date.month == attend.attendance_date.month:
                print("-===============>|GOT IT")
                if attend.attendance_date.day >= rec.sick_from.day and attend.attendance_date.day <= rec.sick_to.day:
                    print("-===============>|WAHHHH IT")
                    attend.sick_leave = True
                    attend.sick_from = rec.sick_from
                    attend.sick_to = rec.sick_to

        return attend

    def get_minute_hmformat(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        return "%d:%02d" % (hour, minutes)

    def get_local_time(self, atten_time):
        if atten_time:
            atten_time = datetime.datetime.strptime(
                atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            local_tz = pytz.timezone(
                self.env.user.tz or 'GMT')
            local_dt = local_tz.localize(atten_time, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            atten_time = datetime.datetime.strptime(
                utc_dt, "%Y-%m-%d %H:%M:%S")
            # atten_time = fields.Datetime.to_string(atten_time)
        return atten_time

    def apply_latein(self, emp_shift_start, check_in):
        # get from employee defination check in , so get the difference after checkin
        employee_checkin = emp_shift_start
        if emp_shift_start and check_in:
            # check the difference
            # if 15 min allow, he come even seconds late, what we can do mark him apply late in logic
            FMT = '%H:%M'
            # check = dt.timedelta(hours=int(str(check_in).split(':')[0]),
            #                         minutes=int(str(check_in).split(':')[1]))
            # check_in=datetime(check_in.year, check_in.month, check_in.day) + timedelta(hours=check_in.hours, minutes=check_in)
            # check_in = self.get_local_time(check_in)
            # check_in = str(check_in).split(':')[0] + ":" + str(check_in).split(':')[1]

            # if int(check_in.hours) > 23:

            # check_in = '23:59'
            #
            # emp_shift_start = self.get_minute_hmformat(emp_shift_start.seconds + 10800)
            # tdelta = datetime.datetime.strptime(str(check_in), FMT) - datetime.datetime.strptime(str(emp_shift_start),
            #                                                                                 FMT)
            # else:

            emp_shift_start = self.get_minute_hmformat(emp_shift_start.seconds)
            check = dt.timedelta(hours=int(check_in.hour),
                                 minutes=int(check_in.minute))
            check_in = self.get_minute_hmformat(check.seconds + 7200)
            tdelta = datetime.datetime.strptime(str(check_in), FMT) - datetime.datetime.strptime(str(emp_shift_start),
                                                                                                 FMT)

            _logger.info("Check ins: %s emp date => %s delta =>> %s", str(check_in), str(emp_shift_start), str(tdelta))

            # check if difference greater than 15 minute
            # also include grace time
            if tdelta.days < 0:
                self.apply_latein_deduction = False
                self.late_in = None
            if not tdelta.days < 0:
                # convert H:M to seconds and compare it with grace if its greater it means deduction apply
                seconds_difference_checkin = tdelta.seconds
                grace_time_seconds = 60
                _logger.info("difference -=> %s",
                             str(seconds_difference_checkin))

                if seconds_difference_checkin > grace_time_seconds:
                    self.apply_latein_deduction = True
                    # if seconds_difference_checkin > 3600:
                    self.absent = False

                    # seconds_difference_checkin -= 900

                    self.late_in = self.get_minute_hmformat(seconds_difference_checkin)

                else:
                    self.apply_latein_deduction = False
        else:
            self.apply_latein_deduction = False
            self.late_in = None

    @api.depends('working', 'attendance_date')
    def get_ot_hours(self):
        # if day is friday so what the rate is 1.50
        # first step get the OT hours, check if OT hours more than 2 or less, if its more than two consider 1.50 also otherwise 1,25
        for record in self:
            # self.send_notif('Applied OT')
            ins = record.check_ins
            outs = record.check_outs
            record.working = record.calc_total_working_hours(ins, outs)

            if record.working and record.attendance_date:
                # here we get Overall OT hours
                record.ot_15 = '00:00'
                record.ot_125 = '00:00'
                day = record.attendance_date.strftime('%A')
                atend_date = record.attendance_date
                publicholiday = False

                schedule_minuts = record.get_schedule_ot(record.employee_id, day)['min']
                ot_minute = (int(record.working.split(':')[0]) * 60 + int(
                    record.working.split(':')[1])) - schedule_minuts
                check_holiday = self.env['hr.calendar.leave'].search([('follow', '=', True)], limit=1)
                if check_holiday:
                    for rec in check_holiday.leave:
                        if rec.leave_date.day == atend_date.day and rec.leave_date.month == atend_date.month:
                            ot_minute = (int(record.working.split(':')[0]) * 60 + int(
                                record.working.split(':')[1]))
                            record.ot_15 = record.get_minute_hmformat(ot_minute * 60)
                            record.has_ot = True
                            publicholiday = True

                if ot_minute > 0 and not publicholiday:
                    if day == 'Friday':
                        if record.employee_id.ot_weekend:
                            record.ot_15 = record.get_minute_hmformat(ot_minute * 60)
                            record.has_ot = True
                        else:
                            pass
                    else:
                        if ot_minute <= 600:
                            if record.employee_id.ot_weekday:
                                # get the difference minute before 600=10hours and update ot1.5
                                record.ot_125 = record.get_minute_hmformat(ot_minute * 60)
                                record.has_ot = True

                        if ot_minute > 600:
                            if record.employee_id.ot_weekday:
                                # get the difference minute after 600 and update ot1.5
                                record.ot_15 = record.get_minute_hmformat((ot_minute - 600) * 60)
                                record.ot_125 = record.get_minute_hmformat(600 * 60)
                                record.has_ot = True

    def get_schedule_ot(self, emp, day):
        if day == 'Saturday':
            if emp.sat_work:
                return {'min': 300, 'fs': 300, 'ss': 300, 'ssc': False, 'ssi': False, 'fsi': False, 'fso': False}

            elif emp.sat_offic:
                return {'min': 270, 'fs': 270, 'ss': 270, 'ssc': False, 'ssi': False, 'fsi': False, 'fso': False}
            else:
                return {'min': 0, 'fs': 0, 'ss': 0, 'ssc': False, 'ssi': False, 'fsi': False, 'fso': False}

        else:
            if not emp.manual_schedule and emp.workschedule:

                if emp.ot_ramzan:
                    spdata1 = str(emp.workschedule).split("|")

                    xx = spdata1[0]
                    yy = spdata1[1]

                else:
                    spdata1 = str(emp.workschedule).split("|")[0]
                    xx = spdata1.split("-")[0]
                    yy = spdata1.split("-")[1]

                vv = dt.timedelta(hours=int(xx.split(":")[0]),
                                  minutes=int(xx.split(":")[1]))
                oo = dt.timedelta(hours=int(yy.split(":")[0]),
                                  minutes=int(yy.split(":")[1]))
                FMT = '%H:%M:%S'
                tdelta = datetime.datetime.strptime(str(oo), FMT) - datetime.datetime.strptime(str(vv), FMT)
                if tdelta.days < 0:
                    tdelta = timedelta(days=0,
                                       seconds=tdelta.seconds, microseconds=tdelta.microseconds)
                    tdelta -= timedelta(hours=12)

                fshft = str(tdelta).split(":")[0] + ":" + str(tdelta).split(":")[1]

                # emp_schedule_checkin1 = datetime.datetime.strptime(xx, '%H:%M')
                # emp_schedule_checkout1 = datetime.datetime.strptime(yy, '%H:%M')

                if emp.ot_ramzan:
                    spdata2 = str(emp.workschedule).split("|")

                    xx1 = '00:00'
                    yy1 = '00:00'

                else:
                    spdata2 = str(emp.workschedule).split("|")[1]
                    xx1 = spdata2.split("-")[0]
                    yy1 = spdata2.split("-")[1]

                vv1 = dt.timedelta(hours=int(xx1.split(":")[0]),
                                   minutes=int(xx1.split(":")[1]))
                oo1 = dt.timedelta(hours=int(yy1.split(":")[0]),
                                   minutes=int(yy1.split(":")[1]))

                tdelta1 = datetime.datetime.strptime(str(oo1), FMT) - datetime.datetime.strptime(str(vv1), FMT)
                if tdelta1.days < 0:
                    tdelta1 = timedelta(days=0,
                                        seconds=tdelta1.seconds, microseconds=tdelta1.microseconds)
                    tdelta1 -= timedelta(hours=12)

                tot = tdelta + tdelta1

                totmins = int(str(tot).split(":")[0]) * 60 + int(str(tot).split(":")[1])

                return {'min': totmins, 'fs': int(str(tdelta).split(":")[0]) * 60 + int(str(tdelta).split(":")[1]),
                        'ss': int(str(tdelta1).split(":")[0]) * 60 + int(str(tdelta1).split(":")[1]), 'ssc': oo1,
                        'ssi': vv1, 'fsi': vv, 'fso': oo}
            elif emp.manual_schedule:
                FMT = '%H:%M:%S'

                first_start_hour = str(emp.man_works_fhour).split(":")[0]
                first_start_min = str(emp.man_works_fhour).split(":")[1]

                first_end_hour = str(emp.man_works_fmins).split(":")[0]
                first_end_min = str(emp.man_works_fmins).split(":")[1]

                second_start_hour = str(emp.man_works_shour).split(":")[0]
                second_start_min = str(emp.man_works_shour).split(":")[1]

                second_end_hour = str(emp.man_works_smins).split(":")[0]
                second_end_min = str(emp.man_works_smins).split(":")[1]

                fss = dt.timedelta(hours=int(first_start_hour),
                                   minutes=int(first_start_min))
                fes = dt.timedelta(hours=int(first_end_hour),
                                   minutes=int(first_end_min))

                tdelta = datetime.datetime.strptime(str(fes), FMT) - datetime.datetime.strptime(str(fss), FMT)
                if tdelta.days < 0:
                    tdelta = timedelta(days=0,
                                       seconds=tdelta.seconds, microseconds=tdelta.microseconds)
                    tdelta -= timedelta(hours=12)

                ess = dt.timedelta(hours=int(second_start_hour),
                                   minutes=int(second_start_min))
                ees = dt.timedelta(hours=int(second_end_hour),
                                   minutes=int(second_end_min))

                tdelta1 = datetime.datetime.strptime(str(ees), FMT) - datetime.datetime.strptime(str(ess), FMT)
                if tdelta1.days < 0:
                    tdelta1 = timedelta(days=0,
                                        seconds=tdelta1.seconds, microseconds=tdelta1.microseconds)
                    tdelta1 -= timedelta(hours=12)

                tot = tdelta + tdelta1

                totmins = int(str(tot).split(":")[0]) * 60 + int(str(tot).split(":")[1])

                return {'min': totmins, 'fs': int(str(tdelta).split(":")[0]) * 60 + int(str(tdelta).split(":")[1]),
                        'ss': int(str(tdelta1).split(":")[0]) * 60 + int(str(tdelta1).split(":")[1]), 'ssc': ees,
                        'ssi': vv1, 'fsi': fss, 'fso': fes}
                # fshf = emp.man_works_fhour * 60 + emp.man_works_fmins
                # sshft = emp.man_works_shour * 60 + emp.man_works_smins
                # return fshf + sshft
            else:
                dltx = dt.timedelta(hours=0,
                                    minutes=0)
                return {'min': 0, 'fs': 0, 'ss': 0, 'ssc': False, 'ssi': False, 'fsi': False, 'fso': False}

    @api.depends('employee_id')
    def get_jobtitle(self):
        for rec in self:
            if rec.employee_id:
                jobtt = rec.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id)], limit=1)
                if jobtt:
                    # if jobtt.grade:
                    #     rec.job_title = jobtt.grade.designation.name
                    # else:
                    #     rec.job_title = None
                    rec.job_title = None
                else:
                    rec.job_title = None
            else:
                rec.job_title = None

    @api.depends('first_check_in', 'first_check_out')
    def onchangefirst_checkin_checkout(self):
        for rec in self:
            time_obj_first_check_in = False
            time_obj_first_check_out = False

            if rec.first_check_in:
                try:
                    time_obj_first_check_in = datetime.datetime.strptime(rec.first_check_in, '%H:%M')
                except:
                    raise ValidationError(_("Follow Correct Format 00:00"))
            if rec.first_check_out:
                try:
                    time_obj_first_check_out = datetime.datetime.strptime(rec.first_check_out, '%H:%M')
                except:
                    raise ValidationError(_("Follow Correct Format 00:00"))

            if time_obj_first_check_in and time_obj_first_check_out:

                if (time_obj_first_check_in.hour > 0 or time_obj_first_check_in.minute > 0) and (
                        time_obj_first_check_out.hour > 0 or time_obj_first_check_out.minute > 0):

                    rec.first_shift_total_hours = str(time_obj_first_check_out - time_obj_first_check_in).split(":")[
                                                      0] + ':' \
                                                  + str(time_obj_first_check_out - time_obj_first_check_in).split(":")[
                                                      1]

                elif rec.first_check_in:
                    day = rec.attendance_date.strftime('%A')

                    get_hrs = str(rec.get_schedule_ot(rec.employee_id, day)['fs'] / 60)

                    rec.first_shift_total_hours = str(get_hrs.split(".")[0] + ':' + get_hrs.split(".")[1])


                else:
                    rec.first_shift_total_hours = '00:00'
            else:
                rec.first_shift_total_hours = '00:00'

    @api.depends('second_check_in', 'second_check_out')
    def onchangesecond_checkin_checkout(self):
        for rec in self:
            time_obj_second_check_in = False
            time_obj_second_check_out = False

            if rec.second_check_in:
                try:
                    time_obj_second_check_in = datetime.datetime.strptime(rec.second_check_in, '%H:%M')
                except:
                    raise ValidationError(_("Follow Correct Format 00:00"))
            if rec.second_check_out:
                try:
                    time_obj_second_check_out = datetime.datetime.strptime(rec.second_check_out, '%H:%M')
                except:

                    raise ValidationError(_("Follow Correct Format 00:00"))

            if time_obj_second_check_in and time_obj_second_check_out:

                if (time_obj_second_check_in.hour > 0 or time_obj_second_check_in.minute > 0) and (
                        time_obj_second_check_out.hour > 0 or time_obj_second_check_out.minute > 0):
                    yesterday = (datetime.datetime.now().date() - timedelta(1)).strftime('%Y-%m-%d')
                    check_prev = rec.env['attendance.custom'].search(
                        [('employee_id', '=', rec.employee_id.id), ('attendance_date', '=', yesterday)])
                    if check_prev:
                        if not check_prev.second_check_out:
                            if not check_prev.second_check_in:

                                if not check_prev.first_check_out:
                                    day = check_prev.attendance_date.strftime('%A')
                                    # hrss = check_prev.get_schedule_ot(check_prev.employee_id, day)['fs'] / 60

                                    get_hrs = str(check_prev.get_schedule_ot(check_prev.employee_id, day)['fs'] / 60)

                                    get_hrs = str(check_prev.get_schedule_ot(check_prev.employee_id, day)['ss'] / 60)

                                    check_prev.ot_125 = rec.get_minute_hmformat(10 + 1 * 60)
                                    check_prev.ot_15 = rec.get_minute_hmformat(5 * 60)

                                    check_prev.second_shift_total_hours = str(
                                        get_hrs.split(".")[0] + ':' + get_hrs.split(".")[1])
                                    check_prev.first_shift_total_hours = str(
                                        get_hrs.split(".")[0] + ':' + get_hrs.split(".")[1])

                                else:
                                    day = check_prev.attendance_date.strftime('%A')
                                    # hrss=check_prev.get_schedule_ot(check_prev.employee_id, day)['ss'] / 60

                                    check_prev.ot_125 = rec.get_minute_hmformat(10 * 60)
                                    check_prev.ot_15 = rec.get_minute_hmformat(5 * 60)

                                    get_hrs = str(check_prev.get_schedule_ot(check_prev.employee_id, day)['ss'] / 60)

                                    check_prev.second_shift_total_hours = str(
                                        get_hrs.split(".")[0] + ':' + get_hrs.split(".")[1])
                            else:
                                pass

                    rec.second_shift_total_hours = str(time_obj_second_check_out - time_obj_second_check_in).split(":")[
                                                       0] + ':' \
                                                   + \
                                                   str(time_obj_second_check_out - time_obj_second_check_in).split(":")[
                                                       1]
                elif (time_obj_second_check_in.hour > 0 or time_obj_second_check_in.minute > 0):
                    day = rec.attendance_date.strftime('%A')

                    get_hrs = str(rec.get_schedule_ot(rec.employee_id, day)['ss'] / 60)

                    rec.second_shift_total_hours = str(get_hrs.split(".")[0] + ':' + get_hrs.split(".")[1])

                else:
                    rec.second_shift_total_hours = '00:00'

            else:
                rec.second_shift_total_hours = '00:00'

    # @api.depends('first_shift_total_hours', 'second_shift_total_hours')
    # def get_workingtime(self):
    #     for rec in self:
    #         sum = 0
    #         if rec.first_shift_total_hours:
    #             try:
    #                 time_obj_1st_shifttotal = datetime.datetime.strptime(rec.first_shift_total_hours, '%H:%M')
    #                 a = dt.timedelta(hours=int(rec.first_shift_total_hours.split(":")[0]),
    #                                  minutes=int(rec.first_shift_total_hours.split(":")[1]))
    #
    #             except:
    #                 raise ValidationError(_("Follow Correct Format 00:00"))
    #
    #         if rec.second_shift_total_hours:
    #             try:
    #                 time_obj_2nd_shifttotal = datetime.datetime.strptime(rec.second_shift_total_hours, '%H:%M')
    #                 b = dt.timedelta(hours=int(rec.second_shift_total_hours.split(":")[0]),
    #                                  minutes=int(rec.second_shift_total_hours.split(":")[1]))
    #
    #             except:
    #                 raise ValidationError(_("Follow Correct Format 00:00"))
    #
    #         if rec.first_shift_total_hours and rec.second_shift_total_hours:
    #             rec.working = str(a + b).split(':')[0] + ':' + str(a + b).split(':')[1]
    #             print(rec.working)
    #
    #             rec.second_shift_total_hours = str(time_obj_second_check_out - time_obj_second_check_in).split(":")[
    #                                                0] + ':' \
    #                                            + str(time_obj_second_check_out - time_obj_second_check_in).split(":")[1]
    #         elif not rec.second_check_in:
    #             day = rec.attendance_date.strftime('%A')
    #
    #             get_hrs = str(rec.get_schedule_ot(rec.employee_id, day)['ss'] / 60)
    #
    #             rec.second_shift_total_hours = str(get_hrs.split(".")[0] + ':' + get_hrs.split(".")[1])
    #
    #         else:
    #             rec.second_shift_total_hours = '00:00'

    @api.depends('first_shift_total_hours', 'second_shift_total_hours')
    def get_workingtime(self):
        for rec in self:
            sum = 0
            a = dt.timedelta(hours=int(0),
                             minutes=int(0))
            b = dt.timedelta(hours=int(0),
                             minutes=int(0))
            if rec.first_shift_total_hours:
                try:
                    time_obj_1st_shifttotal = datetime.datetime.strptime(rec.first_shift_total_hours, '%H:%M')
                    a = dt.timedelta(hours=int(rec.first_shift_total_hours.split(":")[0]),
                                     minutes=int(rec.first_shift_total_hours.split(":")[1]))

                except:
                    pass
                    # raise ValidationError(_("Follow Correct Format 00:00"))

            if rec.second_shift_total_hours:
                try:
                    time_obj_2nd_shifttotal = datetime.datetime.strptime(rec.second_shift_total_hours, '%H:%M')
                    b = dt.timedelta(hours=int(rec.second_shift_total_hours.split(":")[0]),
                                     minutes=int(rec.second_shift_total_hours.split(":")[1]))

                except:
                    pass
                    # raise ValidationError(_("Follow Correct Format 00:00"))

            if rec.first_shift_total_hours and rec.second_shift_total_hours:
                rec.working = str(a + b).split(':')[0] + ':' + str(a + b).split(':')[1]
                print(rec.working)
