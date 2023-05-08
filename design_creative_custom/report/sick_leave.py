# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class absentsrdetDetails(models.TransientModel):
    _name = 'absent.details'
    _description = "absent Report Details"

    date_from = fields.Date(required=True, string="Date from")
    date_to = fields.Date(required=True, string="Date To")

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)
    def get_tot_val(self, emps):
        dix = {}
        tot = 0

        for rec in emps:
            attends = self.env['attendance.custom'].search_count(
                [('employee_id', '=', rec.id), '|', ('absent', '=', True),
                 ('sick_leave', '=', True), ('attendance_date', '>=', self.date_from),
                 ('attendance_date', '<=', self.date_to),
                 ])
            tot += attends

        dix['totl'] = tot

        return dix

    def print_report(self):
        plist = []

        dept = self.env['hr.department'].search(
            [('name', '!=', 'Management')])

        for rec in dept:
            dix = {}
            dix['data'] = 'd'
            dix['div'] = rec.name

            emps = self.env['hr.employee'].search(
                [('contract_id.grade.department', '=', rec.id)])
            gettot = self.get_tot_val(emps)

            dix['tot'] =gettot.get('totl')
            plist.append(dix)
            for dec in emps:
                attends = self.env['attendance.custom'].search_count(
                    [('employee_id', '=', dec.id), '|', ('absent', '=', True),
                     ('sick_leave', '=', True), ('attendance_date', '>=', self.date_from),
                     ('attendance_date', '<=', self.date_to),
                     ])
                dix = {}
                dix['roll'] = dec.identification_id

                dix['emp'] = dec.name
                dix['nat'] = dec.country_id.name
                dix['div'] = rec.name
                dix['total'] = attends
                dix['data'] = 'nd'
                plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'dta': plist
            },
        }
        return self.env.ref('design_creative_custom.action_report_sick_attendance').report_action(self, data=data)


class absnetscxReport(models.AbstractModel):
    _name = 'report.design_creative_custom.sick_attendance'
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
