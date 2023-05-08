# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta
import time
from datetime import datetime
import pytz
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import datetime as dt


class dailyxtsrdetWiseDept(models.TransientModel):
    _name = 'attendace.dept.wiz'
    _description = "absent Report Details"

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    department = fields.Many2one('hr.department', string="Department",required=True)
    check = fields.Boolean(default=True)


    def get_minute_hmformat(self, seconds):
        rec=seconds.timetuple()
        hour = int(rec.tm_hour)+3
        return "%d:%02d" % (hour, rec.tm_min)

    def get_minute_fromseconds(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        # seconds %= 3600
        minutes = seconds // 60
        # seconds %= 60

        return "%d" % (minutes)

    # def create_records(self):
    #     plist = []
    #     attends = []
    #     DeviceUserAttendance = self.env['user.attendance']
    #
    #     r = self.env['attendance.device'].search([], limit=1)
    #     attendance_states = {}
    #     for state_line in r.attendance_device_state_line_ids:
    #         attendance_states[state_line.attendance_state_id.code] = state_line.attendance_state_id.id
    #     if r:
    #
    #         dept = self.env['hr.department'].search(
    #             [('name', '!=', 'Management')])
    #         delta = timedelta(days=1)
    #         start_date = self.start_date
    #         end_date = self.end_date
    #
    #
    #         while start_date <= end_date:
    #             my_list = [[str(start_date)+' 03:30:00',0],[str(start_date)+' 08:00:00',1],[str(start_date)+' 09:30:00',0],[str(start_date)+' 13:00:00',1]]
    #             for rec in dept:
    #                 emps = self.env['hr.employee'].search(
    #                     [('contract_id.grade.department', '=', rec.id)])
    #                 for emp in emps:
    #                     AttendanceUser = self.env['attendance.device.user'].search([('employee_id','=',emp.id)])
    #
    #                     # mydic = {
    #                     #     'employee_id': emp.id,
    #                     #     'attendance_date': start_date,
    #                     # }
    #                     # attendance_custom = self.env['attendance.custom'].create(mydic)
    #                     for lst in my_list:
    #                         vals = {
    #                             'user_id':AttendanceUser.id or False,
    #                             'device_id': r.id,
    #                             'employee_id': emp.id,
    #                             'timestamp': lst[0],
    #                             'status': lst[1],
    #                             'attendance_state_id':  attendance_states[lst[1]]
    #                         }
    #                         mov=DeviceUserAttendance.sudo().create(vals)
    #                         mov.employee_id=emp.id
    #
    #
    #
    #             start_date += delta

    # def print_report_valid(self):
    #     self.print_report(True)

    def get_local_time(self, atten_time):
        if atten_time:
            atten_time = datetime.strptime(
                atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            local_tz = pytz.timezone(
                self.env.user.tz or 'GMT')
            local_dt = local_tz.localize(atten_time, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            atten_time = datetime.strptime(
                utc_dt, "%Y-%m-%d %H:%M:%S")
            # atten_time = fields.Datetime.to_string(atten_time)
        return atten_time

    def print_report(self):
        check = self.check
        ot=self._context.get('OT',False) or False
        plist = []
        attends = []

        if self.department:
            dept = self.env['hr.department'].search(
                [('name', '!=', 'Management'),('id','=',self.department.id)])


        for rec in dept:

            employ = self.env['hr.employee'].search(
                [('department_id', '=', rec.id)])
            # else:
            #     emps = self.env['hr.employee'].search(
            #         [('contract_id.grade.department', '=', rec.id)])

            for emps in employ:
                atten = self.env['attendance.custom'].search(
                    [('employee_id', 'in', emps.ids),
                     ('attendance_date', '>=', self.start_date),
                     ('attendance_date', '<=', self.end_date),

                     ])
                if atten:
                    dix = {}
                    dix['data'] = 'd'
                    dix['div'] = rec.name
                    plist.append(dix)
                    delta = timedelta(days=1)
                    start_date = self.start_date
                    end_date = self.end_date
                    while start_date <= end_date:
                        for dec in emps:
                            if dec.date_of_join < start_date:
                                attends = self.env['attendance.custom'].search(
                                    [('employee_id', '=', dec.id),
                                     ('attendance_date', '=', start_date),

                                     ])
                                attends_valid = self.env['attendance.custom'].search(
                                    [('employee_id', '=', dec.id),
                                     ('attendance_date', '=', start_date),

                                     ])
                                if attends:
                                    if ot == 1 and ((int(str(attends.ot_125 or '00:00').split(':')[0],0) or 0 > 0) or (int(str(attends.ot_15 or '00:00').split(':')[0],0) or 0 > 0)):
                                        statex = False
                                        if attends.absent:
                                            statex = 'Absent'
                                        elif not attends.absent and attends.is_modif:
                                            statex = 'present'
                                        elif attends.sick_leave:
                                            statex = 'Sick leave'
                                        elif attends.leave:
                                            statex = 'Paid Leave'
                                        elif attends.Unpaid:
                                            statex = 'un-paid leave'
                                        elif attends.valid:
                                            statex = 'Present'
                                        dix = {}
                                        dix['titlex']='MONTHLY ATTENDANCE REPORT OT'
                                        dix['roll'] = dec.identification_id
                                        dix['emp'] = dec.name
                                        dix['dept'] = dec.contract_id.grade.department.name
                                        dix['state'] = statex
                                        dix['title'] = start_date.strftime("%Y/%m/%d")
                                        dix['in'] = ' || '.join(
                                            self.get_minute_hmformat(x.timestamp) for x in attends.check_ins if
                                            x.timestamp)
                                        dix['out'] = ' || '.join(
                                            self.get_minute_hmformat(x.timestamp) for x in attends.check_outs if
                                            x.timestamp)
                                        dix['total_hours'] = attends.working
                                        ot15 = 0.0
                                        ot125 = 0.0
                                        if attends.ot_15:
                                            ot15 = dt.timedelta(hours=int(attends.ot_15.split(':')[0]),
                                                                minutes=int(attends.ot_15.split(':')[1]))
                                            ot15 = self.get_minute_fromseconds(ot15.seconds)
                                        if attends.ot_125:
                                            ot125 = dt.timedelta(hours=int(attends.ot_125.split(':')[0]),
                                                                 minutes=int(attends.ot_125.split(':')[1]))
                                            ot125 = self.get_minute_fromseconds(ot125.seconds)
                                        dix['ottotal'] = round(float(ot15) + float(ot125), 3)
                                        dix['ot15'] = attends.ot_15
                                        dix['ot125'] = attends.ot_125
                                        latex = attends.late_in
                                        if attends.late_in:
                                            latex = dt.timedelta(hours=int(attends.late_in.split(':')[0]),
                                                                 minutes=int(attends.late_in.split(':')[1]))
                                            latex = self.get_minute_fromseconds(latex.seconds)
                                        dix['late_in'] = latex

                                        dix['data'] = 'nd'
                                        dix['color'] = "black"

                                        dix['erly_in'] = 'Valid' if attends.valid else 'InValid'
                                        plist.append(dix)

                                    elif not ot and attends and start_date.strftime('%A') != 'Friday':
                                        statex = False
                                        if attends.absent:
                                            statex = 'Absent'
                                        elif not attends.absent and attends.is_modif:
                                            statex = 'present'
                                        elif attends.sick_leave:
                                            statex = 'Sick leave'
                                        elif attends.leave:
                                            statex = 'Paid Leave'
                                        elif attends.Unpaid:
                                            statex = 'un-paid leave'
                                        elif attends.valid:
                                            statex = 'Present'
                                        dix = {}
                                        dix['titlex']='Department Wise Report'
                                        dix['roll'] = dec.identification_id
                                        dix['emp'] = dec.name
                                        dix['dept'] = dec.contract_id.grade.department.name
                                        dix['state'] = statex
                                        dix['title'] = start_date.strftime("%Y/%m/%d")
                                        dix['in'] = ' || '.join(
                                            self.get_minute_hmformat(x.timestamp) for x in attends.check_ins if x.timestamp)
                                        dix['out'] = ' || '.join(
                                            self.get_minute_hmformat(x.timestamp) for x in attends.check_outs if x.timestamp)
                                        dix['total_hours'] = attends.working
                                        ot15 = 0.0
                                        ot125 = 0.0
                                        if attends.ot_15:
                                            ot15 = dt.timedelta(hours=int(attends.ot_15.split(':')[0]),
                                                                minutes=int(attends.ot_15.split(':')[1]))
                                            ot15 = self.get_minute_fromseconds(ot15.seconds)
                                        if attends.ot_125:
                                            ot125 = dt.timedelta(hours=int(attends.ot_125.split(':')[0]),
                                                                 minutes=int(attends.ot_125.split(':')[1]))
                                            ot125 = self.get_minute_fromseconds(ot125.seconds)
                                        dix['ottotal'] = round(float(ot15) + float(ot125), 3)
                                        dix['ot15'] = attends.ot_15
                                        dix['ot125'] = attends.ot_125
                                        latex = attends.late_in
                                        if attends.late_in:
                                            latex = dt.timedelta(hours=int(attends.late_in.split(':')[0]),
                                                                 minutes=int(attends.late_in.split(':')[1]))
                                            latex = self.get_minute_fromseconds(latex.seconds)
                                        dix['late_in'] = latex

                                        dix['data'] = 'nd'
                                        dix['color'] = "black"

                                        dix['erly_in'] = 'Valid' if attends.valid else 'InValid'
                                        plist.append(dix)
                                    elif not ot and  not attends_valid and start_date.strftime('%A') != 'Friday':
                                        dix = {}
                                        dix['titlex']='MONTHLY ATTENDANCE REPORT INVALID'

                                        dix['roll'] = dec.identification_id
                                        dix['emp'] = dec.name
                                        dix['dept'] = dec.contract_id.grade.department.name
                                        dix['state'] = 'Aget_timebsent'
                                        dix['data'] = 'nd'
                                        dix['title'] = start_date.strftime("%Y/%m/%d")

                                        dix['color'] = "black"
                                        if dec.date_of_join>=start_date:
                                            dix['erly_in'] = str(dec.date_of_join)
                                        else:
                                            dix['erly_in'] = "N/A"
                                        plist.append(dix)
                        start_date += delta
        # for rec in dept:
        #     dix = {}
        #     dix['data'] = 'd'
        #     dix['div'] = rec.name
        #     plist.append(dix)

        # for dec in emps:
        #     start_date = self.start_date
        #     end_date = self.end_date
        #     attends=[]
        #
        #     delta = timedelta(days=1)
        #     while start_date <= end_date:
        #         check_ins = self.env['user.attendance'].search(
        #             [('employee_id', '=', dec.id), ('status', '=', 0)], order='timestamp asc')
        #         check_ins = check_ins.filtered(lambda x: x.timestamp.date() == start_date)
        #
        #         check_outs = self.env['user.attendance'].search(
        #             [('employee_id', '=', dec.id), ('status', '=', 1)], order='timestamp asc')
        #         check_outs = check_outs.filtered(lambda x: x.timestamp.date() == start_date)
        #
        #         chk_ins_len = len(check_ins)
        #         chk_outs_len = len(check_outs)
        #
        #         if (chk_ins_len)>0 or (chk_outs_len)>0:
        #             attends+=check_ins
        #             attends+=check_outs

        # attends = self.env['attendance.custom'].search(
        #     [('employee_id', '=', dec.id),
        #      ('valid', '=', False),
        #
        #      ('attendance_date', '=', start_date),
        #      ])
        # start_date += delta
        #
        # for rec in attends:
        #     dix = {}
        #     dix['emp'] = dec.name
        #     dix['roll'] = dec.identification_id
        #     dix['date'] = self.get_time(rec.timestamp)
        #     dix['stat'] = rec.attendance_state_id.display_name

        # if rec.first_check_in:
        #     dix['stat'] = rec.first_check_in
        # else:
        #     dix['in'] = " "
        #
        # if rec.first_check_out:
        #     dix['out'] = rec.first_check_out
        # else:
        #     dix['out'] = " "
        #
        # if rec.second_check_in:
        #     dix['in2'] = rec.second_check_in
        # else:
        #     dix['in2'] = " "
        #
        # if rec.second_check_out:
        #     dix['out2'] = rec.second_check_out
        # else:
        #     dix['out2'] = " "

        # plist.append(dix)
        if not plist:
            plist.append({'titlex':"N/A"})

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.start_date,
                'date_to': self.end_date,
                'check': check,

                'dta': plist
            },
        }
        # if not check:
        return self.env.ref('attendance_customization.action_report_departmetWise_attendId').report_action(self, data=data)
        # else:
        #     return self.env.ref('attendance_customization.action_report_valid_attendance').report_action(self, data=data)

    def get_time(self, x):
        if x:
            hrs = int(str(x).split(':')[0]) + 3
            mnt = int(str(x).split(':')[1])
            if hrs < 10:
                hrs = "0" + str(hrs)

            if mnt < 10:
                mnt = "0" + str(mnt)
            # else:
            #     minut = x.minute
            #
            # if x.hour >= 24 and minut >= 59:
            #     return str(23) + ':' + str(minut)
            # elif x.hour >= 24:
            #     return str(23) + ':' + str(minut)

            return str(str(hrs) + ':' + str(mnt))


class dailyxtscxReport_invalid(models.AbstractModel):
    _name = 'report.attendance_customization.dept_wise_attend_details'
    _description = "Emp logs Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_f = data['form']['date_from']
        date_t = data['form']['date_to']
        check = data['form']['check']

        datax = data['form']['dta']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'df': date_f,
            'dt': date_t,
            'check': check,

            'dtax': datax,

            # 'end_date':end_date,
            # 'project_id':self.env['project.project'].browse(project_id),
            # 'stage_id':self.env['project.task.type'].browse(stage_id),
        }


class dailyxtscxReport_valid(models.AbstractModel):
    _name = 'report.attendance_customization.department_attend_template'
    _description = "Emp logs Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_f = data['form']['date_from']
        date_t = data['form']['date_to']
        check = data['form']['check']

        datax = data['form']['dta']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'df': date_f,
            'dt': date_t,
            'check': check,

            'dtax': datax,

            # 'end_date':end_date,
            # 'project_id':self.env['project.project'].browse(project_id),
            # 'stage_id':self.env['project.task.type'].browse(stage_id),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
