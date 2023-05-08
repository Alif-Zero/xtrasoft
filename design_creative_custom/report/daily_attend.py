# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import datetime as dt
import pytz


class dailyxtsrdetDetails(models.TransientModel):
    _name = 'daily.attendace.detail'
    _description = "absent Report Details"

    date_d = fields.Date(required=True, string="Date")
    ignore_valid = fields.Boolean(default=False, string="Ignore Valid")

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)

    def get_minute_hmformat(self, seconds):
        rec=seconds.timetuple()
        hour = int(rec.tm_hour)+3
        return "%d:%02d" % (hour, rec.tm_min)

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

    def get_minute_fromseconds(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        # seconds %= 3600
        minutes = seconds // 60
        # seconds %= 60

        return "%d" % (minutes)

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

    def print_report(self):
        plist = []
        dept = self.env['hr.department'].search(
            [('name', '!=', 'Management')])

        for rec in dept:
            emps = self.env['hr.employee'].search(
                [('contract_id.grade.department', '=', rec.id)])
            if emps:
                atten = self.env['attendance.custom'].search(
                    [('employee_id', '=', emps[0].id),
                     ('attendance_date', '=', self.date_d),
                     ])
                if atten:
                    dix = {}
                    dix['data'] = 'd'
                    dix['div'] = rec.name
                    plist.append(dix)

            for dec in emps:
                attends = self.env['attendance.custom'].search(
                    [('employee_id', '=', dec.id),
                     ('attendance_date', '=', self.date_d),
                     ])
                if attends:
                    if attends.employee_id.identification_id in ['1019'] and self.date_d.day == 25:
                        print(rec)

                    statex=False
                    if attends.absent:
                        statex='Absent'
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



                    # utc_timestamp = self.env['to.base'].convert_time_to_utc(x.timestamp, self.env.user_id.tz)
                    dix = {}
                    dix['roll'] = dec.identification_id
                    dix['emp'] = dec.name
                    dix['dept'] = dec.contract_id.grade.department.name
                    dix['state'] = statex
                    dix['title'] = dec.workschedule
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
                    dix['data'] = 'nd'
                    dix['color'] = "black"

                    dix['erly_in'] = "Valid"

                    # if attends.early_in:
                    #     dix['erly_in'] = "Valid"
                    #     dix['color'] = "green"
                    #
                    #
                    # elif attends.early_out:
                    #     dix['erly_in'] = "Valid"
                    #     dix['color'] = "green"

                    if not attends.valid:
                        if self.ignore_valid:
                            dix['erly_in'] = "Valid"
                            dix['color'] = "black"
                        else:
                            dix['erly_in'] = "Invalid"
                            dix['color'] = "red"

                    plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_d,
                'dta': plist
            },
        }
        return self.env.ref('design_creative_custom.action_report_dailyx_attendance').report_action(self, data=data)


class dailyxtscxReport(models.AbstractModel):
    _name = 'report.design_creative_custom.third_attendance'
    _description = "Emp logs Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_f = data['form']['date_from']
        datax = data['form']['dta']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'df': date_f,
            'dtax': datax,

            # 'end_date':end_date,
            # 'project_id':self.env['project.project'].browse(project_id),
            # 'stage_id':self.env['project.task.type'].browse(stage_id),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
