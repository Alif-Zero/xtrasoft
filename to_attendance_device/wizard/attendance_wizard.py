import logging
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError
import pandas
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime


_logger = logging.getLogger(__name__)
class CompanyInherit(models.Model):
    _inherit = 'res.company'

    last_attendance_date=fields.Date(string='Last Attendance')

class AttendanceRecords1(models.Model):
    _inherit = 'hr.attendance'
    time_start = fields.Float()
    time_end = fields.Float()
    status = fields.Selection([
        ('Absent', 'Absent'), 
        ('Present', 'Present'),
        ('On Leave','On Leave'),
        ('Half Day','Half Day'),
        ('Holiday','Holiday'),
        ('Public','Public Holiday'),
        ])
    check_in = fields.Datetime(required=False, default=False)
    attendance_date=fields.Date(string='Date')
    department_id=fields.Many2one('hr.department',related='employee_id.department_id',store=True)
    variance=fields.Float(string='Variance Hours',compute='GetVariance')
    hours_per_day = fields.Float()
    # process_status=fields.Selection([('In Process','In Process'),('Done','Done')],default='In Process')

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            # if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
            #     raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
            #         'empl_name': attendance.employee_id.name,
            #         'datetime': format_datetime(self.env, attendance.check_in, dt_format=False),
            #     })

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                # if no_check_out_attendances:
                #     raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                #         'empl_name': attendance.employee_id.name,
                #         'datetime': format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False),
                #     })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                # if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                #     raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                #         'empl_name': attendance.employee_id.name,
                #         'datetime': format_datetime(self.env, last_attendance_before_check_out.check_in, dt_format=False),
                #     })


    @api.onchange('worked_hours','check_in','check_out', 'status')
    def GetVariance(self):
        import pytz
        for rec in self:
            if rec.status not in ('Holiday', 'Public') and rec.overtime_id:
                day_of_week = rec.attendance_date.weekday()
                employee_calendar = self.env['resource.calendar.attendance'].search(
                    [('dayofweek', '=', day_of_week), ('day_period', '=', 'afternoon'),
                     ('calendar_id', '=', rec.employee_id.resource_calendar_id.id)])
                tz = pytz.timezone('Asia/Karachi')
                tz1 = pytz.timezone('UTC')
                tz2 = pytz.timezone('Asia/Karachi')
                delta = 0
                # now=fields.Datetime.now(tz)
                # print (rec.check_out.time(tz)
                if rec.check_out:
                    dt = datetime.strptime(str(rec.check_out), "%Y-%m-%d %H:%M:%S")
                    dt = tz1.localize(dt)
                    dt = dt.astimezone(tz2)
                    work_to = employee_calendar.hour_to
                    if rec.time_end:
                        work_to = rec.time_end
                    result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_to * 60, 60))

                    dt = dt.strftime("%H:%M:%S")
                    x = datetime.strptime(result, "%H:%M")
                    y = datetime.strptime(dt, "%H:%M:%S")
                    delta = (y - x).total_seconds() / 3600
                # dt=dt.astimez.one(tz)
                # print (str(dt-str('18:00'))
                # variance=rec.check_out.time()
                rec.variance = delta

            elif rec.status not in ('Holiday', 'Public') and not rec.overtime_id:
                hours_per_day = rec.hours_per_day or rec.employee_id.resource_calendar_id.hours_per_day
                rec.variance = rec.worked_hours - hours_per_day
            elif rec.status in ('Holiday', 'Public') and rec.overtime_id:
                hours_per_day = rec.hours_per_day or rec.employee_id.resource_calendar_id.hours_per_day
                rec.variance = rec.worked_hours
            elif rec.status not in ('Holiday', 'Public'):
                rec.variance = rec.worked_hours
            else:
                rec.variance = 0
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

    device_ids = fields.Many2many('attendance.device', string='Devices', default=_get_all_device_ids, domain=[('state', '=', 'confirmed')])
    fix_attendance_valid_before_synch = fields.Boolean(string='Fix Attendance Valid', help="If checked, Odoo will recompute all attendance data for their valid"
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
        devices = self.env['attendance.device'].search([('state', '=', 'confirmed')])
        devices.action_attendance_download()

    def cron_sync_attendance(self):
        self.with_context(synch_ignore_constraints=True).sync_attendance()

    def LeaveStatusUpdate(self):
        for rec in self.env['hr.attendance'].search([('status','=','Absent')]):
            if self.env['hr.leaves'].search([('request_date_from','<=',rec.attendance_date),('request_date_to','>=',rec.attendance_date)]):
                rec.status='On Leave'

    def AttendanceHolidayStatus(self):
        date = fields.Datetime.now().date() - timedelta(days=45)
        attendance_record = self.env['hr.attendance'].search([('attendance_date', '>=', date)])
        for rec in attendance_record:
            holiday = self.env['date.holiday'].search([('date', '=', rec.attendance_date)], limit=1)
            if holiday.type == 'Weekly Holiday':
                rec.status = 'Holiday'
                rec.GetOverTime()
            if holiday.type == 'Public Holiday':
                rec.status = 'Public'
                rec.GetOverTime()

    def get_employee_period(self, employee,date):
        start_time = 0
        end_time = 0
        if employee.contract_id:
            work_schedule = employee.contract_id.resource_calendar_id
            week_day = date.weekday()
            for schedule in work_schedule.sudo().attendance_ids:
                if schedule.dayofweek == str(week_day) and schedule.day_period == 'morning':
                    # work_from = schedule.hour_from
                    start_time = schedule.hour_from
                    # start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))
                if schedule.dayofweek == str(week_day) and schedule.day_period == 'afternoon':
                    # work_from = schedule.hour_to
                    end_time = schedule.hour_to
                    # end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))

        return start_time, end_time
    def CreateAttendance(self):
        for company in self.env['res.company'].search([]):
            lst=pandas.date_range(company.last_attendance_date, datetime.now(), freq='d')
            company.last_attendance_date=datetime.now()
            for date in lst:
                contract_obj=self.env['hr.contract'].search([('state','in',['open', 'probation']),('employee_id','!=',False)])
                for contract in contract_obj:
                    exempt_obj=self.env['hr.attendance.exemption'].search([('employee_id','=',contract.employee_id.id)])
                    if not self.env['hr.attendance'].search([('employee_id','=',contract.employee_id.id),('attendance_date','=',date)]):
                        checkIn_time, checkOut_time = self.get_employee_period(contract.employee_id,date)
                        hours_per_day = contract.employee_id.resource_calendar_id.hours_per_day
                        if exempt_obj:
                            vals = {
                                'employee_id': contract.employee_id.id,
                                'check_in': False,
                                'checkin_device_id': False,
                                'attendance_date': date,
                                'time_start':checkIn_time,
                                'time_end':checkOut_time,
                                'hours_per_day': hours_per_day,
                                'status': 'Present'
                            }
                            self.env['hr.attendance'].create(vals)
                        else:
                            vals = {
                                'employee_id': contract.employee_id.id,
                                'check_in': False,
                                'checkin_device_id': False,
                                'attendance_date': date,
                                'time_start':checkIn_time,
                                'time_end':checkOut_time,
                                'hours_per_day': hours_per_day,
                                'status': 'Absent'
                            }
                            self.env['hr.attendance'].create(vals)

    # def sync_attendance(self):
    #     DeviceUserAttendance = self.env['user.attendance']
    #     for attendance_record in self.env['hr.attendance'].search([]):
    #         unsync_data = DeviceUserAttendance.search([('valid', '=', True),
    #                                                     ('employee_id', '=', attendance_record.employee_id.id)], order='timestamp ASC')
    #         if unsync_data:
    #             relvant_data=unsync_data.filtered(lambda x:x.timestamp.date()==attendance_record.attendance_date)
    #             if relvant_data:
    #                 attendance_record.check_in=relvant_data[0].timestamp
    #                 attendance_record.check_out=relvant_data[-1].timestamp
    #                 attendance_record.status='Present'
    #         for att in relvant_data:
    #             att.hr_attendance_id=attendance_record.id

    def sync_attendance(self):
        DeviceUserAttendance = self.env['user.attendance']
        lst = pandas.date_range(datetime.now()-timedelta(days=2), datetime.now(), freq='d')
        for atten_date in lst:
            for attendance_record in self.env['hr.attendance'].search([('attendance_date','=',atten_date),('manual_updated','=',False)]):
                unsync_data = DeviceUserAttendance.search([('valid', '=', True),
                                                            ('employee_id', '=', attendance_record.employee_id.id)], order='timestamp ASC')
                dt_string = datetime.now()
                if unsync_data:
                    # attendance_record=self.env['hr.attendance'].search([('employee_id','=',employee.id),('attendance_date','=',unsync_data[0].timestamp.date())])
                    relvant_data=unsync_data.filtered(lambda x:x.timestamp.date()==attendance_record.attendance_date)
                    if relvant_data:
                        attendance_record.check_in=relvant_data[0].timestamp
                        attendance_record.check_out=relvant_data[-1].timestamp
                        attendance_record.status = 'Present'
                        # if attendance_record.check_in==attendance_record.check_out:
                        if attendance_record.check_in<=dt_string-timedelta(hours=13):
                            if attendance_record.worked_hours<4:
                                attendance_record.status='Absent'
                            if attendance_record.worked_hours==4:
                                attendance_record.status='Half Day'
                        for att in relvant_data:
                            att.hr_attendance_id=attendance_record.id

    def clear_attendance(self):
        if not self.device_ids:
            raise UserError(_('You must select at least one device to continue!'))
        if not self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
            raise UserError(_('Only HR Attendance Managers can manually clear device attendance data'))

        for device in self.device_ids:
                device.clearAttendance()

    def action_fix_user_attendance_valid(self):
        all_attendances = self.env['user.attendance'].search([])
        for attendance in all_attendances:
            if attendance.is_valid():
                attendance.write({'valid': True})
            else:
                attendance.write({'valid': False})
