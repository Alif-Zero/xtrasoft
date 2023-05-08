# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class attsummerytDetails(models.TransientModel):
    _name = 'attend.summery.details'
    _description = "Project Report Details"

    date_from = fields.Date(required=True, string="Date from")
    date_to = fields.Date(required=True, string="Date To")

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)

    def print_report(self):
        plist = []
        ddic = {}
        list_day = []
        ddic_day = []

        start_date = self.date_from
        end_date = self.date_to
        dix = {}

        delta = timedelta(days=1)
        while start_date <= end_date:
            ddic_day.append(start_date.day)
            start_date += delta

        emps = self.env['hr.employee'].search(
            [])

        for dec in emps:
            start_date = self.date_from
            end_date = self.date_to
            dix = {}
            cnt = 0
            minux = 0
            absnt=0
            delta = timedelta(days=1)

            while start_date <= end_date:
                ddic = {}

                stax = self.env['attendance.custom'].search(
                    [('employee_id', '=', dec.id),
                     ('attendance_date', '=', start_date),
                     ], limit=1)
                if stax and stax.valid:
                    dix[start_date.day] = "A"
                elif stax and not stax.valid:
                    dix[start_date.day] = "AB"

                elif stax and start_date.strftime("%A") == 'Friday':
                    dix[start_date.day] = "A"
                    minux+=1

                elif not stax and start_date.strftime("%A") != 'Friday':
                    dix[start_date.day] = "AB"
                    absnt+=1

                elif not stax:
                    dix[start_date.day] = "P"
                else:
                    dix[start_date.day] = "AB"
                    absnt+=1

                # ddic['empp'] = dec.name
                # list_day.append(ddic)

                start_date += delta
                cnt += 1

            attends = self.env['attendance.custom'].search_count(
                [('employee_id', '=', dec.id), ('no_attend', '=', False), ('absent', '=', False),('valid', '=', True),
                 ('sick_leave', '=', False), ('attendance_date', '>=', self.date_from),
                 ('attendance_date', '<=', self.date_to),
                 ])
            Missing = self.env['attendance.custom'].search_count(
                [('employee_id', '!=', dec.id),
                 ('attendance_date', '>=', self.date_from),
                 ('attendance_date', '<=', self.date_to),
                 ])
            Absent = self.env['attendance.custom'].search_count(
                [('employee_id', '=', dec.id),'|',('absent', '=', True),('valid', '=', False)
                    ,('attendance_date', '>=', self.date_from),
                 ('attendance_date', '<=', self.date_to),
                 ])
            leave = self.env['attendance.custom'].search_count(
                [('employee_id', '=', dec.id), ('leave', '=', True)
                    , ('attendance_date', '>=', self.date_from),
                 ('attendance_date', '<=', self.date_to),
                 ])
            leave_sick = self.env['attendance.custom'].search_count(
                [('employee_id', '=', dec.id), ('sick_leave', '=', True)
                    , ('attendance_date', '>=', self.date_from),
                 ('attendance_date', '<=', self.date_to),
                 ])

            leave_Emerg = self.env['attendance.custom'].search_count(
                [('employee_id', '=', dec.id), ('Emerg', '=', True)
                    , ('attendance_date', '>=', self.date_from),
                 ('attendance_date', '<=', self.date_to),
                 ])

            leave_Unpaid = self.env['attendance.custom'].search_count(
                [('employee_id', '=', dec.id), ('Unpaid', '=', True)
                    , ('attendance_date', '>=', self.date_from),
                 ('attendance_date', '<=', self.date_to),
                 ])
            leave_paid =(int(round(cnt) / 7)-minux)

            leave_Mater = self.env['attendance.custom'].search_count(
                [('employee_id', '=', dec.id), ('Mater', '=', True)
                    , ('attendance_date', '>=', self.date_from),
                 ('attendance_date', '<=', self.date_to),
                 ])
            leave_Busi = self.env['attendance.custom'].search_count(
                [('employee_id', '=', dec.id), ('Busi', '=', True)
                    , ('attendance_date', '>=', self.date_from),
                 ('attendance_date', '<=', self.date_to),
                 ])

            total = attends+leave_paid

            dix['roll'] = dec.identification_id

            dix['emp'] = dec.name
            dix['atend'] = attends+minux
            dix['Missing'] = Missing
            dix['Absent'] = Absent+absnt

            dix['leave'] = leave
            dix['dayoff'] = leave_Unpaid
            dix['death'] = leave_Emerg
            dix['paid'] = leave+leave_paid

            dix['leave_sick'] = leave_sick
            dix['leave_Emerg'] = leave_Emerg
            dix['leave_paid'] = leave_paid
            dix['leave_Unpaid'] = leave_Unpaid
            dix['leave_Mater'] = leave_Mater

            dix['leave_Busi'] = leave_Busi
            dix['total'] = total

            plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'dta': plist,
                'day_l': ddic_day,
                # 'day_data': list_day
            },
        }
        return self.env.ref('attendance_customization.action_report_summ_attendancee').report_action(self, data=data)


class empsummeryogscxReportss(models.AbstractModel):
    _name = 'report.attendance_customization.summery_attendance_staffxx'
    _description = "Emp logs Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_f = data['form']['date_from']
        date_t = data['form']['date_to']
        datax = data['form']['dta']
        dayl = data['form']['day_l']
        # dayv = data['form']['day_data']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'df': date_f,
            'dt': date_t,
            'dtax': datax,
            'dayl': dayl,
            # 'dayd': dayv

            # 'end_date':end_date,
            # 'project_id':self.env['project.project'].browse(project_id),
            # 'stage_id':self.env['project.task.type'].browse(stage_id),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
