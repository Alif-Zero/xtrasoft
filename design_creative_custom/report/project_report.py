# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class logsrdetDetails(models.TransientModel):
    _name = 'emplog.details'
    _description = "Project Report Details"

    date_from = fields.Date(required=True,string="Date from")
    date_to = fields.Date(required=True,string="Date To")

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)

    def print_report(self):
        emps = self.env['hr.employee'].search(
            [('date_of_leave', '>=', self.date_from), ('date_of_leave', '<=', self.date_to)])
        plist = []
        for rec in emps:
            dix = {}
            if rec.resign:
                dix['reason'] = 'Resign'
            if rec.terminate:
                dix['reason'] = 'Terminate'
            if rec.runaway:
                dix['reason'] = 'Runaway'
            dix['date'] = rec.date_of_leave
            dix['emp'] = rec.name
            dix['manager'] = rec.manager_log.name
            plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'dta': plist

                # 'user_id': self.user_id.id,
                # 'start_date': self.start_date,
                # 'end_date':self.end_date,
                # 'stage_id':self.stage_id.id,
            },
        }
        return self.env.ref('design_creative_custom.emplogs_log_report_action').report_action(self, data=data)


class emplogscxReport(models.AbstractModel):
    _name = 'report.design_creative_custom.logs_emp_templates'
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
