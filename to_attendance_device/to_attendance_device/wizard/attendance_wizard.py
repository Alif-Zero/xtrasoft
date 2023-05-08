import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import datetime as dt
from datetime import date, datetime, time, timedelta

_logger = logging.getLogger(__name__)


class AttendanceWizard(models.TransientModel):
    _name = 'attendance.wizard'
    _description = 'Attendance Wizard'

    @api.model
    def _get_all_device_ids(self):
        all_devices = self.env['attendance.device'].search([('state', '=', 'confirmed')])
        if all_devices:
            return all_devices.ids
        else:
            return []

    device_ids = fields.Many2many('attendance.device', string='Devices', default=_get_all_device_ids,
                                  domain=[('state', '=', 'confirmed')])
    fix_attendance_valid_before_synch = fields.Boolean(string='Fix Attendance Valid',
                                                       help="If checked, Odoo will recompute all attendance data for their valid"
                                                            " before synchronizing with HR Attendance (upon you hit the 'Synchronize Attendance' button)")

    def download_attendance_manually(self):
        # TODO: remove me after 12.0
        self.action_download_attendance()

    def action_download_attendance(self):
        if not self.device_ids:
            raise UserError(_('You must select at least one device to continue!'))
        self.device_ids.action_attendance_download()

    def download_device_attendance(self):
        # TODO: remove me after 12.0
        self.cron_download_device_attendance()

    def cron_download_device_attendance(self):
        devices = self.env['attendance.device'].search([('state', '=', 'confirmed')],limit=1)
        devices.action_create_attendance()

    def cron_sync_attendance(self):
        self.with_context(synch_ignore_constraints=True).sync_attendance()

    def sync_attendance(self):
        """
        This method will synchronize all downloaded attendance data with Odoo attendance data.
        It do not download attendance data from the devices.
        """
        if self.fix_attendance_valid_before_synch:
            self.action_fix_user_attendance_valid()

        self.device_ids[0].action_create_attendance()

        # synch_ignore_constraints = self.env.context.get('synch_ignore_constraints', False)
        #
        # error_msg = {}
        # HrAttendance = self.env['hr.attendance'].with_context(synch_ignore_constraints=synch_ignore_constraints)
        #
        # activity_ids = self.env['attendance.activity'].search([])
        #
        # DeviceUserAttendance = self.env['user.attendance']
        #
        # custom_attendance = self.env['attendance.custom']
        #
        # last_employee_attendance = {}
        # for activity_id in activity_ids:
        #     if activity_id.id not in last_employee_attendance.keys():
        #         last_employee_attendance[activity_id.id] = {}
        #
        #     unsync_data = DeviceUserAttendance.search([('hr_attendance_id', '=', False),
        #                                                ('valid', '=', True),
        #                                                ('employee_id', '!=', False),
        #                                                ('activity_id', '=', activity_id.id)], order='timestamp ASC')
        #     for att in unsync_data:
        #         employee_id = att.user_id.employee_id
        #         if employee_id.id not in last_employee_attendance[activity_id.id].keys():
        #             last_employee_attendance[activity_id.id][employee_id.id] = False
        #
        #         if att.type == 'checkout':
        #             # find last attendance
        #
        #             last_employee_attendance[activity_id.id][employee_id.id] = HrAttendance.search(
        #                 [('employee_id', '=', employee_id.id),
        #                  ('activity_id', 'in', (activity_id.id, False)),
        #                  ('check_in', '<=', att.timestamp)], limit=1, order='check_in DESC')
        #
        #             hr_attendance_id = last_employee_attendance[activity_id.id][employee_id.id]
        #
        #             if hr_attendance_id:
        #                 try:
        #                     hr_attendance_id.with_context(synch_ignore_constraints=synch_ignore_constraints).write({
        #                         'check_out': att.timestamp,
        #                         'checkout_device_id': att.device_id.id
        #                     })
        #                 except ValidationError as e:
        #                     if att.device_id not in error_msg:
        #                         error_msg[att.device_id] = ""
        #
        #                     msg = ""
        #                     att_check_time = fields.Datetime.context_timestamp(att, att.timestamp)
        #                     msg += str(e) + "<br />"
        #                     msg += _("'Check Out' time cannot be earlier than 'Check In' time. Debug information:<br />"
        #                              "* Employee: <strong>%s</strong><br />"
        #                              "* Type: %s<br />"
        #                              "* Attendance Check Time: %s<br />") % (
        #                                employee_id.name, att.type, fields.Datetime.to_string(att_check_time))
        #                     _logger.error(msg)
        #                     error_msg[att.device_id] += msg
        #         else:
        #             # create hr attendance data
        #             vals = {
        #                 'employee_id': employee_id.id,
        #                 'check_in': att.timestamp,
        #                 'checkin_device_id': att.device_id.id,
        #                 'activity_id': activity_id.id,
        #             }
        #
        #             hr_attendance_id = HrAttendance.search([
        #                 ('employee_id', '=', employee_id.id),
        #                 ('check_in', '=', att.timestamp),
        #                 ('checkin_device_id', '=', att.device_id.id),
        #                 ('activity_id', '=', activity_id.id)], limit=1)
        #
        #             # is_first = HrAttendance.search([
        #             #     ('employee_id', '=', employee_id.id),
        #             #     ('check_in', '<=', att.timestamp),
        #             #     ('checkin_device_id', '=', att.device_id.id),
        #             #     ('activity_id', '=', activity_id.id)], limit=1, order='check_in DESC')
        #             # if is_first:
        #             #     if is_first.check_in.date == att.timestamp.date:
        #
        #             c_attend = custom_attendance.search(
        #                 [('employee_id', '=', employee_id.id), ('attendance_date', '=', att.timestamp.date())],
        #                 limit=1)
        #
        #             if not hr_attendance_id:
        #                 try:
        #                     hr_attendance_id = HrAttendance.create(vals)
        #
        #                     if not c_attend:
        #                         vals_custom = {
        #                             'employee_id': employee_id.id,
        #                             'attendance_date': att.timestamp,
        #                             'first_check_in': str(
        #                                 hr_attendance_id.check_in.hour if hr_attendance_id.check_in else "00") + ':' + str(
        #                                 hr_attendance_id.check_in.minute if hr_attendance_id.check_in else "00"),
        #                             'first_check_out': str(
        #                                 hr_attendance_id.check_out.hour if hr_attendance_id.check_out else "00") + ':' + str(
        #                                 hr_attendance_id.check_out.minute if hr_attendance_id.check_out else "00")
        #                         }
        #                         c_attend = custom_attendance.create(vals_custom)
        #                         c_attend.first_shift_record = hr_attendance_id.id
        #                     else:
        #                         vals_custom = {
        #                             'employee_id': employee_id.id,
        #                             'attendance_date': att.timestamp,
        #                             'second_check_in': str(
        #                                 hr_attendance_id.check_in.hour if hr_attendance_id.check_in else "00") + ':' + str(
        #                                 hr_attendance_id.check_in.minute if hr_attendance_id.check_in else "00"),
        #                             'second_check_out': str(
        #                                 hr_attendance_id.check_out.hour if hr_attendance_id.check_out else "00") + ':' + str(
        #                                 hr_attendance_id.check_out.minute if hr_attendance_id.check_out else "00")
        #                         }
        #                         c_attend.write(vals_custom)
        #                         c_attend.second_shift_record = hr_attendance_id.id
        #
        #
        #
        #
        #                 except Exception as e:
        #                     _logger.error(e)
        #             else:
        #                 if not c_attend:
        #                     vals_custom = {
        #                         'employee_id': employee_id.id,
        #                         'attendance_date': att.timestamp,
        #                         'first_check_in': str(
        #                             hr_attendance_id.check_in.hour if hr_attendance_id.check_in else "00") + ':' + str(
        #                             hr_attendance_id.check_in.minute if hr_attendance_id.check_in else "00"),
        #                         'first_check_out': str(
        #                             hr_attendance_id.check_out.hour if hr_attendance_id.check_out else "00") + ':' + str(
        #                             hr_attendance_id.check_out.minute if hr_attendance_id.check_out else "00")
        #                     }
        #                     c_attend = custom_attendance.create(vals_custom)
        #                     c_attend.first_shift_record = hr_attendance_id.id
        #
        #                 else:
        #                     vals_custom = {
        #                         'employee_id': employee_id.id,
        #                         'attendance_date': att.timestamp,
        #                         'second_check_in': str(
        #                             hr_attendance_id.check_in.hour if hr_attendance_id.check_in else "00") + ':' + str(
        #                             hr_attendance_id.check_in.minute if hr_attendance_id.check_in else "00"),
        #                         'second_check_out': str(
        #                             hr_attendance_id.check_out.hour if hr_attendance_id.check_out else "00") + ':' + str(
        #                             hr_attendance_id.check_out.minute if hr_attendance_id.check_out else "00")
        #                     }
        #                     c_attend.write(vals_custom)
        #                     c_attend.second_shift_record = hr_attendance_id.id
        #
        #         if hr_attendance_id:
        #             att.write({
        #                 'hr_attendance_id': hr_attendance_id.id
        #             })
        # self.update_attendance()
        #
        # if bool(error_msg):
        #     for device in error_msg.keys():
        #
        #         if not device.debug_message:
        #             continue
        #         device.message_post(body=error_msg[device])
        # HrAttendance.invalidate_cache()
        # Create Custom attendace
        # for rec in HrAttendance.search([])
        # vals = {
        #     'employee_id': employee_id.id,
        #     'check_in': att.timestamp,
        #     'checkin_device_id': att.device_id.id,
        #     'activity_id': activity_id.id,
        # }

    def clear_attendance(self):
        if not self.device_ids:
            raise UserError(_('You must select at least one device to continue!'))
        if not self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
            raise UserError(_('Only HR Attendance Managers can manually clear device attendance data'))

        for device in self.device_ids:
            device.clearAttendance()

    def update_attendance(self):
        synch_ignore_constraints = self.env.context.get('synch_ignore_constraints', False)

        error_msg = {}
        HrAttendance = self.env['hr.attendance'].with_context(synch_ignore_constraints=synch_ignore_constraints)

        activity_ids = self.env['attendance.activity'].search([])

        DeviceUserAttendance = self.env['user.attendance']

        custom_attendance = self.env['attendance.custom']

        last_employee_attendance = {}
        for activity_id in activity_ids:
            if activity_id.id not in last_employee_attendance.keys():
                last_employee_attendance[activity_id.id] = {}
            unsync_data = DeviceUserAttendance.search([('valid', '=', False),
                                                       ('activity_id', '=', activity_id.id)], order='timestamp ASC')
            for att in unsync_data:
                employee_id = att.user_id.employee_id
                if employee_id.id not in last_employee_attendance[activity_id.id].keys():
                    last_employee_attendance[activity_id.id][employee_id.id] = False
                if employee_id:

                    if att.type == 'checkout':
                        # find last attendance

                        last_employee_attendance[activity_id.id][employee_id.id] = HrAttendance.search(
                            [('employee_id', '=', employee_id.id),
                             ('activity_id', 'in', (activity_id.id, False)),
                             ('check_in', '<=', att.timestamp)], limit=1, order='check_in DESC')

                        hr_attendance_id = last_employee_attendance[activity_id.id][employee_id.id]

                        if hr_attendance_id:
                            try:
                                hr_attendance_id.with_context(synch_ignore_constraints=synch_ignore_constraints).write({
                                    'check_out': att.timestamp,
                                    'checkout_device_id': att.device_id.id
                                })
                            except ValidationError as e:
                                if att.device_id not in error_msg:
                                    error_msg[att.device_id] = ""

                                msg = ""
                                att_check_time = fields.Datetime.context_timestamp(att, att.timestamp)
                                msg += str(e) + "<br />"
                                msg += _(
                                    "'Check Out' time cannot be earlier than 'Check In' time. Debug information:<br />"
                                    "* Employee: <strong>%s</strong><br />"
                                    "* Type: %s<br />"
                                    "* Attendance Check Time: %s<br />") % (
                                           employee_id.name, att.type, fields.Datetime.to_string(att_check_time))
                                _logger.error(msg)
                                error_msg[att.device_id] += msg
                    else:
                        # create hr attendance data
                        vals = {
                            'employee_id': employee_id.id,
                            'check_in': att.timestamp,
                            'checkin_device_id': att.device_id.id,
                            'activity_id': activity_id.id,
                        }

                        hr_attendance_id = HrAttendance.search([
                            ('employee_id', '=', employee_id.id),
                            ('check_in', '=', att.timestamp),
                            ('checkin_device_id', '=', att.device_id.id),
                            ('activity_id', '=', activity_id.id)], limit=1)

                        # is_first = HrAttendance.search([
                        #     ('employee_id', '=', employee_id.id),
                        #     ('check_in', '<=', att.timestamp),
                        #     ('checkin_device_id', '=', att.device_id.id),
                        #     ('activity_id', '=', activity_id.id)], limit=1, order='check_in DESC')
                        # if is_first:
                        #     if is_first.check_in.date == att.timestamp.date:

                        c_attend = custom_attendance.search(
                            [('employee_id', '=', employee_id.id), ('attendance_date', '=', att.timestamp.date())],
                            limit=1)

                        if not hr_attendance_id:
                            try:
                                hr_attendance_id = HrAttendance.create(vals)

                                if not c_attend:
                                    vals_custom = {
                                        'employee_id': employee_id.id,
                                        'attendance_date': att.timestamp,
                                        'first_check_in': str(
                                            hr_attendance_id.check_in.hour if hr_attendance_id.check_in else "00") + ':' + str(
                                            hr_attendance_id.check_in.minute if hr_attendance_id.check_in else "00"),
                                        'first_check_out': str(
                                            hr_attendance_id.check_out.hour if hr_attendance_id.check_out else "00") + ':' + str(
                                            hr_attendance_id.check_out.minute if hr_attendance_id.check_out else "00")
                                    }
                                    c_attend = custom_attendance.create(vals_custom)
                                    c_attend.first_shift_record = hr_attendance_id.id

                                else:
                                    vals_custom = {
                                        'employee_id': employee_id.id,
                                        'attendance_date': att.timestamp,
                                        'second_check_in': str(
                                            hr_attendance_id.check_in.hour if hr_attendance_id.check_in else "00") + ':' + str(
                                            hr_attendance_id.check_in.minute if hr_attendance_id.check_in else "00"),
                                        'second_check_out': str(
                                            hr_attendance_id.check_out.hour if hr_attendance_id.check_out else "00") + ':' + str(
                                            hr_attendance_id.check_out.minute if hr_attendance_id.check_out else "00")
                                    }
                                    c_attend.write(vals_custom)
                                    c_attend.second_shift_record = hr_attendance_id.id



                            except Exception as e:
                                _logger.error(e)
                        else:
                            if not c_attend:
                                vals_custom = {
                                    'employee_id': employee_id.id,
                                    'attendance_date': att.timestamp,
                                    'first_check_in': str(
                                        hr_attendance_id.check_in.hour if hr_attendance_id.check_in else "00") + ':' + str(
                                        hr_attendance_id.check_in.minute if hr_attendance_id.check_in else "00"),
                                    'first_check_out': str(
                                        hr_attendance_id.check_out.hour if hr_attendance_id.check_out else "00") + ':' + str(
                                        hr_attendance_id.check_out.minute if hr_attendance_id.check_out else "00")
                                }
                                c_attend = custom_attendance.create(vals_custom)
                                c_attend.first_shift_record = hr_attendance_id.id

                            else:
                                vals_custom = {
                                    'employee_id': employee_id.id,
                                    'attendance_date': att.timestamp,
                                    'second_check_in': str(
                                        hr_attendance_id.check_in.hour if hr_attendance_id.check_in else "00") + ':' + str(
                                        hr_attendance_id.check_in.minute if hr_attendance_id.check_in else "00"),
                                    'second_check_out': str(
                                        hr_attendance_id.check_out.hour if hr_attendance_id.check_out else "00") + ':' + str(
                                        hr_attendance_id.check_out.minute if hr_attendance_id.check_out else "00")
                                }
                                c_attend.write(vals_custom)
                                c_attend.second_shift_record = hr_attendance_id.id

                    if hr_attendance_id:
                        att.write({
                            'hr_attendance_id': hr_attendance_id.id
                        })

    def action_fix_user_attendance_valid(self):
        all_attendances = self.env['user.attendance'].search([])
        for attendance in all_attendances:
            if attendance.is_valid():
                attendance.write({'valid': True})
            else:
                attendance.write({'valid': False})

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

    def create_instance(self, move, status):
        chk_in_instance = self.env['check.ins']
        chk_out_instance = self.env['check.outs']
        ins = False
        if status in [0, 4]:
            ins = chk_in_instance.create(move)
        elif status in [1, 5]:
            ins = chk_out_instance.create(move)

        return ins

    def get_dict(self, ci, attendance_custom):
        return {
            'timestamp': ci.timestamp,
            'check': self.get_time(ci.timestamp),
            'att_cus': attendance_custom.id,
            'status': ci.type
        }

    def create_checkins_outs(self, attendance_custom, checks):
        moves = []
        if attendance_custom and checks:
            if len(checks) > 1:
                fcin = None
                for ci in checks:
                    if fcin != None:
                        diff = ci.timestamp - fcin.timestamp
                        minutes = diff.seconds / 60
                        fcin = ci
                        if minutes < 1:
                            pass
                            # rcord = self.get_dict(ci, attendance_custom)
                            # attendance_custom.valid = False
                            # moves += self.create_instance(rcord, ci.status)
                            #
                            # print("king")
                        else:
                            rcord = self.get_dict(ci, attendance_custom)
                            moves += self.create_instance(rcord, ci.status)


                    else:
                        rcord = self.get_dict(ci, attendance_custom)
                        fcin = ci
                        moves += self.create_instance(rcord, ci.status)
            else:
                rcord = self.get_dict(checks, attendance_custom)
                moves += self.create_instance(rcord, checks.status)
        return moves

    def action_clear_attendance(self):
        clear_data = self.env['clear.data.model'].search([('name', '=', 'nj')])
        if clear_data:
            clear_data.action_do_clear()

    def cron_download_device_attendance(self):
        if self.state=='confirmed':
            self.action_attendance_download()

    def action_create_attendance(self):
        self.cron_download_device_attendance()

        # self.action_clear_attendance()
        # self.invalidate_cache()
        list_valid_cin = []
        list_valid_cout = []
        # get_emp = self.env['user.attendance'].search([]).mapped('employee_id')
        # for rec in get_emp:
        #     time_stams = list(self.env['user.attendance'].search([('employee_id', '=', rec.id)],
        #                                                          order='timestamp asc').mapped('timestamp'))
        #     time_stams = time_stams[len(time_stams) - 260:]
        #     last_time = -1
        #     checkins = self.env['user.attendance'].search(
        #         [('employee_id', '=', rec.id), ('attendance_state_id.type', '=', 'checkin')], order='timestamp asc')
        #     checkouts = self.env['user.attendance'].search(
        #         [('employee_id', '=', rec.id), ('attendance_state_id.type', '=', 'checkout')], order='timestamp asc')
        #
        #     start_date = time_stams[0].date()
        #     end_date = fields.Datetime.now().date()
        #     delta = timedelta(days=1)
        #     # while start_date <= end_date:
        #     #     print(start_date.strftime("%Y-%m-%d"))
        #     #
        #     while start_date <= end_date:
        #         # if last_time != time.day:
        #         #     last_time = time.day
        #         date = start_date
        #         check_ins = checkins.filtered(lambda x: x.timestamp.date() == date)
        #         check_outs = checkouts.filtered(lambda x: x.timestamp.date() == date)
        #         mydic = {
        #             'employee_id': rec.id,
        #             'attendance_date': date,
        #         }
        #         is_exist = self.env['attendance.custom'].search(
        #             [('employee_id', '=', rec.id), ('attendance_date', '=', date)], limit=1)
        #         if not is_exist:
        #             attendance_custom = self.env['attendance.custom'].create(mydic)
        #
        #             self.create_custom_records(attendance_custom, check_ins, check_outs, date)
        #
        #         elif is_exist:
        #             for dec in is_exist:
        #                 # if not dec.valid:
        #                 dec.check_ins = [(5,)]
        #                 dec.check_outs = [(5,)]
        #                 self.create_custom_records(dec, check_ins, check_outs, date)
        #         start_date += delta
        #         # else:
        #         #     dec.valid=True

    def calc_total_working_hours(self, ins, outs):
        seconds = 0
        if ins and outs:
            for inc, out in zip(ins, outs):
                diff = out.timestamp - inc.timestamp
                seconds += diff.seconds

        return self.get_minute_hmformat(seconds)

    def create_custom_records(self, attendance_custom, check_ins, check_outs, date):
        # attendance_custom.employee_id.workschedule='08:00-13:00|14:00-17:00'
        ins = self.create_checkins_outs(attendance_custom, check_ins)
        outs = self.create_checkins_outs(attendance_custom, check_outs)
        day = attendance_custom.attendance_date.strftime('%A')
        emp_working = attendance_custom.get_schedule_ot(attendance_custom.employee_id, day)
        if len(ins) != len(outs):
            if ins:
                attendance_custom.apply_latein(emp_working['fsi'], self.get_time(ins[0].timestamp))
            if len(ins) == 0 and len(outs) == 0:
                attendance_custom.absent = True
            else:
                if date.month == 1:
                    if outs:
                        shift_end = emp_working['ssc']
                        shift_start = emp_working['ssi']

                        check_out_last = outs[len(outs) - 1].timestamp
                        if check_out_last and shift_end:

                            if shift_end:
                                check_out_last = dt.timedelta(hours=int(check_out_last.hour),
                                                              minutes=int(check_out_last.minute))
                                get_dif = check_out_last - shift_end
                                if get_dif.days < 0:
                                    get_dif = check_out_last - shift_start
                                    if get_dif.days < 0:
                                        attendance_custom.valid = False
                                    else:
                                        get_min_hrs = self.get_minute_hmformat(get_dif.seconds)

                                        fsth = emp_working['fs']
                                        ssth = int(str(get_min_hrs).split(":")[0]) * 60 + int(
                                            str(get_min_hrs).split(":")[1])

                                        tot = (fsth + ssth)
                                        hours = int(str(tot / 60).split('.')[0])
                                        minutes = int(str(tot / 60).split('.')[1])
                                        work = "%d:%02d" % (hours, minutes)
                                        attendance_custom.working = work
                                        attendance_custom.valid = True
                                else:
                                    get_min_hrs = self.get_minute_hmformat(get_dif.seconds)

                                    get_tot = emp_working['min']

                                    tot = (get_tot)
                                    hours = int(str(tot / 60).split('.')[0]) + int(
                                        get_min_hrs.split(':')[0])
                                    minutes = int(str(tot / 60).split('.')[1]) + int(
                                        get_min_hrs.split(':')[1])
                                    work = "%d:%02d" % (hours, minutes)
                                    attendance_custom.working = work
                                    attendance_custom.valid = True

                        else:
                            get_tot = emp_working['min']
                            tot = (get_tot)
                            hours = int(str(tot / 60).split('.')[0])
                            minutes = int(str(tot / 60).split('.')[1])
                            work = "%d:%02d" % (hours, minutes)
                            attendance_custom.working = work
                            attendance_custom.valid = True

                    else:
                        attendance_custom.valid = False

                        # get_tot = emp_working['min']
                        #
                        # tot = (get_tot)
                        # hours = int(str(tot / 60).split('.')[0])
                        # minutes = int(str(tot / 60).split('.')[1])
                        # work = "%d:%02d" % (hours, minutes)
                        # attendance_custom.working = work
                        # attendance_custom.valid = True
                else:
                    attendance_custom.valid = False
                    attendance_custom.absent = True



        else:
            if ins:
                attendance_custom.apply_latein(emp_working['fsi'], self.get_time(ins[0].timestamp))

            if len(ins) == 0 and len(outs) == 0:
                day = date.strftime('%A')
                if day == 'Friday':
                    pass
                else:
                    attendance_custom.valid = False
                    attendance_custom.absent = False

            else:
                attendance_custom.working = self.calc_total_working_hours(ins, outs)
                attendance_custom.get_ot_hours()
                attendance_custom.valid = True

    def get_minute_hmformat(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        return "%d:%02d" % (hour, minutes)

    # def get_ot_hours(self):
    #     # if day is friday so what the rate is 1.50
    #     # first step get the OT hours, check if OT hours more than 2 or less, if its more than two consider 1.50 also otherwise 1,25
    #     for record in self:
    #         if record.working and record.attendance_date:
    #             # here we get Overall OT hours
    #             record.ot_15 = '00:00'
    #             record.ot_125 = '00:00'
    #             day = record.attendance_date.strftime('%A')
    #             atend_date = record.attendance_date
    #             publicholiday = False
    #
    #             schedule_minuts = record.get_schedule_ot(record.employee_id, day)['min']
    #             ot_minute = (int(record.working.split(':')[0]) * 60 + int(
    #                 record.working.split(':')[1])) - schedule_minuts
    #             check_holiday = self.env['hr.calendar.leave'].search([('follow', '=', True)], limit=1)
    #             if check_holiday:
    #                 for rec in check_holiday.leave:
    #                     if rec.leave_date.day == atend_date.day and rec.leave_date.month == atend_date.month:
    #                         ot_minute = (int(record.working.split(':')[0]) * 60 + int(
    #                             record.working.split(':')[1]))
    #                         record.ot_15 = record.get_minute_hmformat(ot_minute * 60)
    #                         publicholiday = True
    #
    #             if ot_minute > 0 and not publicholiday:
    #                 if day == 'Friday':
    #                     if record.employee_id.ot_weekend:
    #                         record.ot_15 = record.get_minute_hmformat(ot_minute * 60)
    #                     else:
    #                         pass
    #                 else:
    #                     if ot_minute <= 600:
    #                         if record.employee_id.ot_weekday:
    #                             # get the difference minute before 600=10hours and update ot1.5
    #                             record.ot_125 = record.get_minute_hmformat(ot_minute * 60)
    #
    #                     if ot_minute > 600:
    #                         if record.employee_id.ot_weekday:
    #                             # get the difference minute after 600 and update ot1.5
    #                             record.ot_15 = record.get_minute_hmformat((ot_minute - 600) * 60)
    #                             record.ot_125 = record.get_minute_hmformat(600 * 60)
    #
    #
    #
    #             # chk_ins_len = len(check_ins)
    #             # chk_outs_len = len(check_outs)
    #             # mydic = {}
    #             # if chk_ins_len == chk_outs_len and (chk_ins_len >= 1 and chk_ins_len <= 3) and (
    #             #         chk_outs_len >= 1 and chk_outs_len <= 3):
    #             #
    #             #     if chk_ins_len == 2 and chk_outs_len == 2:
    #             #         data1 = check_ins[0].timestamp
    #             #         data2 = check_ins[1].timestamp
    #             #
    #             #         diff = data2 - data1
    #             #         minutes = diff.seconds / 60
    #             #
    #             #         if minutes < 1:
    #             #             mydic = {
    #             #                 'employee_id': rec.id,
    #             #                 'attendance_date': time.date(),
    #             #                 'valid': True,
    #             #                 'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #                 'first_check_out': self.get_time(check_outs[1].timestamp),
    #             #
    #             #             }
    #             #         else:
    #             #             mydic = {
    #             #                 'employee_id': rec.id,
    #             #                 'attendance_date': time.date(),
    #             #                 'valid': True,
    #             #                 'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #                 'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #                 'second_check_in': self.get_time(check_ins[1].timestamp),
    #             #                 'second_check_out': self.get_time(check_outs[1].timestamp),
    #             #
    #             #             }
    #             #     if chk_ins_len == 1 and chk_outs_len == 1:
    #             #         mydic = {
    #             #             'employee_id': rec.id,
    #             #             'attendance_date': time.date(),
    #             #             'valid': True,
    #             #             'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #             'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #
    #             #         }
    #             #
    #             #     if chk_ins_len == 3 and chk_outs_len == 3:
    #             #         mydic = {
    #             #             'employee_id': rec.id,
    #             #             'valid': True,
    #             #             'attendance_date': time.date(),
    #             #             'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #             'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #             'second_check_in': self.get_time(check_ins[2].timestamp),
    #             #             'second_check_out': self.get_time(check_outs[2].timestamp),
    #             #         }
    #             #
    #             #
    #             # elif chk_ins_len and chk_outs_len:
    #             #     if chk_ins_len == 0 and chk_ins_len == 0:
    #             #         pass
    #             #     else:
    #             #         if chk_ins_len > 2 and chk_outs_len > 2 and chk_ins_len != chk_outs_len:
    #             #             mydic = {
    #             #                 'employee_id': rec.id,
    #             #                 'attendance_date': time.date(),
    #             #                 'valid': True,
    #             #                 'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #                 'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #                 'second_check_in': self.get_time(check_ins[2].timestamp),
    #             #                 'second_check_out': self.get_time(check_outs[2].timestamp),
    #             #
    #             #             }
    #             #
    #             #         elif chk_ins_len > 1 and chk_outs_len > 1 and chk_ins_len != chk_outs_len:
    #             #             mydic = {
    #             #                 'employee_id': rec.id,
    #             #                 'attendance_date': time.date(),
    #             #                 'valid': True,
    #             #                 'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #                 'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #                 'second_check_in': self.get_time(check_ins[1].timestamp),
    #             #                 'second_check_out': self.get_time(check_outs[1].timestamp),
    #             #
    #             #             }
    #             #         # elif chk_ins_len >2 and chk_outs_len > 2 and  chk_ins_len==chk_outs_len:
    #             #         # elif chk_ins_len > 0 and chk_outs_len >0:
    #             #         #     mydic = {
    #             #         #         'employee_id': rec.id,
    #             #         #         'attendance_date': time.date(),
    #             #         #         'valid': False,
    #             #         #         'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #         #         'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #         #
    #             #         #
    #             #         #     }
    #             #
    #             #         if chk_ins_len >= 2 and chk_outs_len == 0:
    #             #             mydic = {
    #             #                 'employee_id': rec.id,
    #             #                 'attendance_date': time.date(),
    #             #                 'valid': False,
    #             #                 'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #                 'second_check_in': self.get_time(check_ins[1].timestamp),
    #             #
    #             #             }
    #             #         if chk_ins_len == 0 and chk_outs_len >= 2:
    #             #             mydic = {
    #             #                 'employee_id': rec.id,
    #             #                 'attendance_date': time.date(),
    #             #                 'valid': False,
    #             #                 'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #                 'second_check_out': self.get_time(check_outs[1].timestamp),
    #             #
    #             #             }
    #             #
    #             #         if chk_ins_len >= 1 and chk_outs_len == 0:
    #             #             mydic = {
    #             #                 'employee_id': rec.id,
    #             #                 'attendance_date': time.date(),
    #             #                 'valid': False,
    #             #                 'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #
    #             #             }
    #             #         if chk_ins_len == 0 and chk_outs_len >= 1:
    #             #             mydic = {
    #             #                 'employee_id': rec.id,
    #             #                 'attendance_date': time.date(),
    #             #                 'valid': False,
    #             #                 'second_check_out': self.get_time(check_outs[0].timestamp),
    #             #
    #             #             }
    #             # if mydic:
    #             #     self.env['attendance.custom'].create(mydic)
    #             # else:
    #             #     mydic = {
    #             #         'employee_id': rec.id,
    #             #         'attendance_date': time.date(),
    #             #         'valid': False,
    #             #
    #             #     }
    #             #     self.env['attendance.custom'].create(mydic)
    #             #
    #             #     print(chk_ins_len, " AND ", chk_outs_len)
    #             #
    #             # if chk_ins_len > 2 and chk_outs_len > 2 and chk_ins_len == chk_outs_len:
    #             #     mydic = {
    #             #         'employee_id': rec.id,
    #             #         'attendance_date': time.date(),
    #             #         'valid': False,
    #             #         'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #         'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #
    #             #     }
    #             #
    #             # if chk_ins_len > 2 and chk_outs_len > 2 and chk_ins_len == chk_outs_len:
    #             #     mydic = {
    #             #         'employee_id': rec.id,
    #             #         'attendance_date': time.date(),
    #             #         'valid': False,
    #             #         'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #         'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #
    #             #     }
    #             #
    #             # if chk_ins_len > 2 and chk_outs_len > 2 and chk_ins_len == chk_outs_len:
    #             #     mydic = {
    #             #         'employee_id': rec.id,
    #             #         'attendance_date': time.date(),
    #             #         'valid': False,
    #             #         'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #         'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #
    #             #     }
    #             #
    #             # if chk_ins_len > 2 and chk_outs_len > 2 and chk_ins_len == chk_outs_len:
    #             #     mydic = {
    #             #         'employee_id': rec.id,
    #             #         'attendance_date': time.date(),
    #             #         'valid': False,
    #             #         'first_check_in': self.get_time(check_ins[0].timestamp),
    #             #         'first_check_out': self.get_time(check_outs[0].timestamp),
    #             #
    #             #     }
