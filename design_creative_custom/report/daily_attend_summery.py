# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import datetime as dt

class dailyxtsrdetsummery(models.TransientModel):
    _name = 'daily.attendace.summery'
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


    def get_minute_fromseconds(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        # seconds %= 3600
        minutes = seconds // 60
        # seconds %= 60

        return "%d" % (minutes)



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
                        ot15=0.0
                        ot125=0.0
                        if attends.ot_15:
                            ot15 = dt.timedelta(hours=int(attends.ot_15.split(':')[0]),
                                                 minutes=int(attends.ot_15.split(':')[1]))
                            ot15 = self.get_minute_fromseconds(ot15.seconds)
                        if attends.ot_125:
                            ot125 = dt.timedelta(hours=int(attends.ot_125.split(':')[0]),
                                                minutes=int(attends.ot_125.split(':')[1]))
                            ot125 = self.get_minute_fromseconds(ot125.seconds)

                        dix['ottotal']=round(float(ot15)+float(ot125),3)
                        dix['ot15'] = attends.ot_15
                        dix['ot125'] = attends.ot_125
                        latex=attends.late_in
                        if attends.late_in:
                            latex = dt.timedelta(hours=int(attends.late_in.split(':')[0]),
                                                 minutes=int(attends.late_in.split(':')[1]))
                            latex = self.get_minute_fromseconds(latex.seconds)
                        dix['late_in'] = latex

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
                    else:
                        dix = {}
                        dix['roll'] = dec.identification_id
                        dix['emp'] = dec.name
                        dix['dept'] = dec.contract_id.grade.department.name
                        dix['state'] = 'Absent'
                        dix['data'] = 'nd'
                        dix['color'] = "black"
                        dix['erly_in'] = "Invalid"

                    plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_d,
                'dta': plist
            },
        }
        return self.env.ref('design_creative_custom.action_report_dailyxsummer_attendance').report_action(self,
                                                                                                          data=data)

    def print_report_ot(self):
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
                     ('has_ot', '=', True),
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
                             ('has_ot', '=', True),
                             ('absent', '=', False),

                             ])

                        if attends:
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
                            dix['roll'] = dec.identification_id
                            dix['emp'] = dec.name
                            dix['dept'] = dec.contract_id.grade.department.name
                            dix['state'] = statex
                            dix['title'] = dec.workschedule
                            dix['in'] = ' || '.join(
                                str(self.get_minute_hmformat(x.timestamp)) for x in attends.check_ins if x.timestamp)
                            dix['out'] = ' || '.join(
                                str(self.get_minute_hmformat(x.timestamp)) for x in attends.check_outs if x.timestamp)
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
                        else:
                            dix = {}
                            dix['roll'] = dec.identification_id
                            dix['emp'] = dec.name
                            dix['dept'] = dec.contract_id.grade.department.name
                            dix['state'] = 'Absent'
                            dix['data'] = 'nd'
                            dix['color'] = "black"
                            dix['erly_in'] = "Invalid"
                            # plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_d,
                'dta': plist
            },
        }
        return self.env.ref('design_creative_custom.action_report_dailyxsummer_attendance_ot').report_action(self,
                                                                                                             data=data)

    def print_report_absent(self):
        plist = []
        dept = self.env['hr.department'].search(
            [('name', '!=', 'Management')])

        for rec in dept:
            emps = self.env['hr.employee'].search(
                [('contract_id.grade.department', '=', rec.id)])
            if emps:
                # atten = self.env['attendance.custom'].search(
                #     [('employee_id', 'in', emps.ids),
                #      ('attendance_date', '=', self.date_d),
                #      ('absent', '=', True),
                #      ])
                #
                # if atten:
                dix = {}
                dix['data'] = 'd'
                dix['div'] = rec.name
                plist.append(dix)
                for dec in emps:
                    attends = self.env['attendance.custom'].search(
                        [('employee_id', '=', dec.id),
                         ('attendance_date', '=', self.date_d),
                         ('absent', '=', True),
                         ])

                    if attends:
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
                        dix['roll'] = dec.identification_id
                        dix['emp'] = dec.name
                        dix['dept'] = dec.contract_id.grade.department.name
                        dix['state'] = statex
                        dix['title'] = dec.workschedule
                        dix['in'] = ' || '.join(
                            str(self.get_minute_hmformat(x.timestamp)) for x in attends.check_ins if x.timestamp)
                        dix['out'] = ' || '.join(
                            str(self.get_minute_hmformat(x.timestamp)) for x in attends.check_outs if x.timestamp)
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
                        # plist.append(dix)
                    # else:
                    #     dix = {}
                    #     dix['roll'] = dec.identification_id
                    #     dix['emp'] = dec.name
                    #     dix['dept'] = dec.contract_id.grade.department.name
                    #     dix['state'] = 'Absent'
                    #     dix['data'] = 'nd'
                    #     dix['color'] = "black"
                    #     dix['erly_in'] = "Invalid"
                        # plist.append(dix)
                        plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_d,
                'dta': plist
            },
        }
        return self.env.ref('design_creative_custom.action_report_dailyxsummer_attendance_absent').report_action(self,
                                                                                                                 data=data)

    def print_report_late(self):
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
                     ('apply_latein_deduction', '=', True),
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
                             ('apply_latein_deduction', '=', True),
                             ])

                        if attends:
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
                            dix['roll'] = dec.identification_id
                            dix['emp'] = dec.name
                            dix['dept'] = dec.contract_id.grade.department.name
                            dix['state'] = statex
                            dix['title'] = dec.workschedule
                            dix['in'] = ' || '.join(
                                str(self.get_minute_hmformat(x.timestamp)) for x in attends.check_ins if x.timestamp)
                            dix['out'] = ' || '.join(
                                str(self.get_minute_hmformat(x.timestamp)) for x in attends.check_outs if x.timestamp)
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
                        else:
                            dix = {}
                            dix['roll'] = dec.identification_id
                            dix['emp'] = dec.name
                            dix['dept'] = dec.contract_id.grade.department.name
                            dix['state'] = 'Absent'
                            dix['data'] = 'nd'
                            dix['color'] = "black"
                            dix['erly_in'] = "Invalid"
                            # plist.append(dix)
                            # plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_d,
                'dta': plist
            },
        }
        return self.env.ref('design_creative_custom.action_report_dailyxsummer_attendance_late').report_action(self,
                                                                                                               data=data)


class dailyxtscxReport(models.AbstractModel):
    _name = 'report.design_creative_custom.summery_attendance_daily'
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

        }


class latein_report_abstract(models.AbstractModel):
    _name = 'report.design_creative_custom.summery_attendance_daily_late'
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

        }


class absent_report_abstract(models.AbstractModel):
    _name = 'report.design_creative_custom.summery_attendance_daily_absent'
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
        }


class ot_report_abstract(models.AbstractModel):
    _name = 'report.design_creative_custom.summery_attendance_daily_ot'
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

        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
