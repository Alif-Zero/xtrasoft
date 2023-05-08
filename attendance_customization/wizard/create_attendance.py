# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta


class dailyxtsrdetInvalid(models.TransientModel):
    _name = 'attendace.create.wiz'
    _description = "absent Report Details"

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    employee = fields.Many2many('hr.employee', string="Employee(s)")

    # select_emp = fields.Boolean(default=False, string="Select employee")

    def create_records(self, em):
        plist = []
        attends = []
        DeviceUserAttendance = self.env['user.attendance']

        r = self.env['attendance.device'].search([], limit=1)
        attendance_states = {}
        for state_line in r.attendance_device_state_line_ids:
            attendance_states[state_line.attendance_state_id.code] = state_line.attendance_state_id.id
        if r:
            delta = timedelta(days=1)
            start_date = self.start_date
            end_date = self.end_date

            while start_date <= end_date:
                my_list = [[str(start_date) + ' 03:30:00', 0], [str(start_date) + ' 08:00:00', 1],
                           [str(start_date) + ' 09:30:00', 0], [str(start_date) + ' 13:00:00', 1]]
                emps = em
                for emp in emps:
                    AttendanceUser = self.env['attendance.device.user'].search([('employee_id', '=', emp.id)])

                    # mydic = {
                    #     'employee_id': emp.id,
                    #     'attendance_date': start_date,
                    # }
                    if AttendanceUser:
                        device_attend = self.env['user.attendance'].search(
                            [('employee_id', '=', AttendanceUser.employee_id.id),
                             ('timestamp', '>=', str(start_date) + ' 00:00:00'),
                             ('timestamp', '<=', str(start_date) + ' 23:59:59')])
                        if device_attend:
                            self.unlink_recs(device_attend)
                    for lst in my_list:
                        vals = {
                            'user_id': AttendanceUser.id or False,
                            'device_id': r.id,
                            'employee_id': emp.id,
                            'timestamp': lst[0],
                            'status': lst[1],
                            'attendance_state_id': attendance_states[lst[1]]
                        }
                        mov = DeviceUserAttendance.sudo().create(vals)
                        mov.employee_id = emp.id

                start_date += delta

    def unlink_recs(self, recs):
        if recs:
            for rec in recs:
                rec.unlink()

    def create_attendance(self):
        plist = []
        attends = []


        for emps in self.employee:
            if emps:
                atten = self.env['attendance.custom'].search(
                    [('employee_id', 'in', emps.ids),
                     ('attendance_date', '>=', self.start_date),
                     ('attendance_date', '<=', self.end_date),
                     ])
                if atten:
                    self.unlink_recs(atten)

                    delta = timedelta(days=1)
                    start_date = self.start_date
                    end_date = self.end_date

                    while start_date <= end_date:

                        attends = self.env['attendance.custom'].search(
                            [('employee_id', '=', emps.id),
                             ('attendance_date', '=', start_date),

                             ])
                        if atten:
                            self.unlink_recs(atten)
                        start_date += delta
                    self.create_records(emps)



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

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.start_date,
                'date_to': self.end_date,

                'dta': plist
            },
        }
        return self.env.ref('attendance_customization.action_report_invalid_attendance').report_action(self, data=data)

    def get_time(self, x):
        if x:
            # x = int(x.hour*60)+int(x.minute)  # convert to number of seconds
            # minute = x / 60
            # hour = minute / 60
            # my_time = time(x // 3600, (x % 3600) // 60, x % 60)  # hours, minutes, seconds
            # print(type(my_time))
            # if my_time.minute == 0:
            #     return str(my_time.hour) + ':' + str(my_time.minute) + "0"
            # else:
            # if x.minute == 0:
            #     return str(x.hour) + ':' + str(x.minute)+"0"
            # else:
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


class dailyxtscxReport_invalid(models.AbstractModel):
    _name = 'report.attendance_customization.invalid_attend_details'
    _description = "Emp logs Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_f = data['form']['date_from']
        date_t = data['form']['date_to']

        datax = data['form']['dta']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'df': date_f,
            'dt': date_t,

            'dtax': datax,

            # 'end_date':end_date,
            # 'project_id':self.env['project.project'].browse(project_id),
            # 'stage_id':self.env['project.task.type'].browse(stage_id),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
