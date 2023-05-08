# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta



class attsuyweeltDetails(models.TransientModel):
    _name = 'attend.summery.week'
    _description = "Project Report Details"

    date_from = fields.Date(required=True, string="Date from")
    date_to = fields.Date(required=True, string="Date To")

    employee_id = fields.Many2one('hr.employee', string="Employee")




    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)



    def print_report(self):
        plist = []

        start_date = self.date_from
        end_date = self.date_to
        delta = timedelta(days=1)
        while start_date <= end_date:
            print(start_date.strftime("%Y-%m-%d"))
            start_date += delta




        # emps = self.env['hr.employee'].search(
        #     [])
        # for dec in emps:
        #     attends = self.env['attendance.custom'].search_count(
        #         [('employee_id', '=', dec.id), ('no_attend', '=', False), ('absent', '=', False),
        #          ('sick_leave', '=', False), ('attendance_date', '>=', self.date_from),
        #          ('attendance_date', '<=', self.date_to),
        #          ])
        #     Missing = self.env['attendance.custom'].search_count(
        #         [('employee_id', '!=', dec.id),
        #          ('attendance_date', '>=', self.date_from),
        #          ('attendance_date', '<=', self.date_to),
        #          ])
        #     Absent = self.env['attendance.custom'].search_count(
        #         [('employee_id', '=', dec.id), ('absent', '=', True)
        #             , ('attendance_date', '>=', self.date_from),
        #          ('attendance_date', '<=', self.date_to),
        #          ])
        #     leave = self.env['attendance.custom'].search_count(
        #         [('employee_id', '=', dec.id), ('leave', '=', True)
        #             , ('attendance_date', '>=', self.date_from),
        #          ('attendance_date', '<=', self.date_to),
        #          ])
        #     leave_sick = self.env['attendance.custom'].search_count(
        #         [('employee_id', '=', dec.id), ('sick_leave', '=', True)
        #             , ('attendance_date', '>=', self.date_from),
        #          ('attendance_date', '<=', self.date_to),
        #          ])
        #
        #     leave_Emerg = self.env['attendance.custom'].search_count(
        #         [('employee_id', '=', dec.id), ('Emerg', '=', True)
        #             , ('attendance_date', '>=', self.date_from),
        #          ('attendance_date', '<=', self.date_to),
        #          ])
        #
        #     leave_Unpaid = self.env['attendance.custom'].search_count(
        #         [('employee_id', '=', dec.id), ('Unpaid', '=', True)
        #             , ('attendance_date', '>=', self.date_from),
        #          ('attendance_date', '<=', self.date_to),
        #          ])
        #
        #     leave_Mater = self.env['attendance.custom'].search_count(
        #         [('employee_id', '=', dec.id), ('Mater', '=', True)
        #             , ('attendance_date', '>=', self.date_from),
        #          ('attendance_date', '<=', self.date_to),
        #          ])
        #     leave_Busi = self.env['attendance.custom'].search_count(
        #         [('employee_id', '=', dec.id), ('Busi', '=', True)
        #             , ('attendance_date', '>=', self.date_from),
        #          ('attendance_date', '<=', self.date_to),
        #          ])
        #
        #     total = attends
        #
        #     dix = {}
        #     dix['roll'] = dec.identification_id
        #
        #     dix['emp'] = dec.name
        #     dix['atend'] = attends
        #     dix['Missing'] = Missing
        #     dix['Absent'] = Absent
        #
        #     dix['leave'] = leave
        #     dix['leave_sick'] = leave_sick
        #     dix['leave_Emerg'] = leave_Emerg
        #     dix['leave_Unpaid'] = leave_Unpaid
        #     dix['leave_Mater'] = leave_Mater
        #
        #     dix['leave_Busi'] = leave_Busi
        #     dix['total'] = total
        #
        #     plist.append(dix)
        #
        # data = {
        #     'ids': self.ids,
        #     'model': self._name,
        #     'form': {
        #         'date_from': self.date_from,
        #         'date_to': self.date_to,
        #         'dta': plist
        #     },
        # }
        # return self.env.ref('design_creative_custom.action_report_summ_attendance').report_action(self, data=data)


class empsummeryogscxReport(models.AbstractModel):
    _name = 'report.design_creative_custom.summery_attendance_staff'
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
