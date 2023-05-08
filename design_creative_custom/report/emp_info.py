# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class logsemprdetDetails(models.TransientModel):
    _name = 'emplog.info.details'
    _description = "Project Report Details"

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)
    def diff_month(self, d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month

    def print_report(self):
        plist = []
        today = fields.Date.today()

        dept = self.env['hr.department'].search(
            [])

        for dpt in dept:
            dix = {}
            dix['data'] = 'd'
            dix['div'] = dpt.name
            plist.append(dix)
            emps = self.env['hr.employee'].search(
                [('contract_id.grade.department', '=', dpt.id)])

            for rec in emps:
                dix = {}
                dd = 0
                if rec.date_of_join:

                    difference_in_years = relativedelta(today, rec.date_of_join).years
                    month = self.diff_month(today, rec.date_of_join) - (difference_in_years * 12)
                    dd += (difference_in_years * 365)
                    dd += (month * 30)
                    delta = (today - rec.date_of_join)
                    tenur = str(difference_in_years) + " Y " + str(month) + " M " + str((delta.days) - dd) + " D"
                else:
                    tenur = "N/A"

                dix['emp'] = rec.name
                dix['roll'] = rec.identification_id
                dix['pexp'] = rec.passport_id
                dix['nat'] = rec.country_id.name
                dix['cprexp'] = rec.cpr_no
                dix['bname'] = rec.bank_name
                dix['bacount'] = rec.bank_account_id.display_name
                dix['iban'] = rec.iban
                dix['data'] = 'nd'
                dix['tenur'] = tenur

                dix['pexpd'] = rec.passport_exp_date
                dix['rpexpd'] = rec.rp_exp_date
                dix['cprexpd'] = rec.cpr_exp_date

                plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {

                'dta': plist

                # 'user_id': self.user_id.id,
                # 'start_date': self.start_date,
                # 'end_date':self.end_date,
                # 'stage_id':self.stage_id.id,
            },
        }
        return self.env.ref('design_creative_custom.action_report_document_empinfox').report_action(self, data=data)

    def print_report_grade(self):
        plist = []
        today = fields.Date.today()
        dept = self.env['hr.grade'].search(
            [])
        for dpt in dept:
            emps = self.env['hr.employee'].search(
                [('contract_id.grade', '=', dpt.id)])
            if emps:
                dix = {}
                dix['data'] = 'd'
                dix['div'] = dpt.name
                plist.append(dix)
                for rec in emps:
                    dix = {}
                    dd = 0
                    if rec.date_of_join:

                        difference_in_years = relativedelta(today, rec.date_of_join).years
                        month = self.diff_month(today, rec.date_of_join) - (difference_in_years * 12)
                        dd += (difference_in_years * 365)
                        dd += (month * 30)
                        delta = (today - rec.date_of_join)
                        tenur = str(difference_in_years) + " Y " + str(month) + " M " + str((delta.days) - dd) + " D"
                    else:
                        tenur = "N/A"

                    dix['emp'] = rec.name
                    dix['roll'] = rec.identification_id
                    dix['pexp'] = rec.passport_id
                    dix['nat'] = rec.country_id.name
                    dix['cprexp'] = rec.cpr_no
                    dix['bname'] = rec.bank_name
                    dix['bacount'] = rec.bank_account_id.display_name
                    dix['iban'] = rec.iban
                    dix['data'] = 'nd'
                    dix['tenur'] = tenur

                    dix['pexpd'] = rec.passport_exp_date
                    dix['rpexpd'] = rec.rp_exp_date
                    dix['cprexpd'] = rec.cpr_exp_date

                    plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {

                'dta': plist

                # 'user_id': self.user_id.id,
                # 'start_date': self.start_date,
                # 'end_date':self.end_date,
                # 'stage_id':self.stage_id.id,
            },
        }
        return self.env.ref('design_creative_custom.action_report_document_empinfox_gradewise').report_action(self,
                                                                                                              data=data)


class empinfologscxReport(models.AbstractModel):
    _name = 'report.design_creative_custom.document_report_empinfox'
    _description = "Emp logs Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        datax = data['form']['dta']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],

            'dtax': datax,

            # 'end_date':end_date,
            # 'project_id':self.env['project.project'].browse(project_id),
            # 'stage_id':self.env['project.task.type'].browse(stage_id),
        }


class empinfoGradeWiseReport(models.AbstractModel):
    _name = 'report.design_creative_custom.document_report_empinfoxgradewise'
    _description = "Emp logs Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        datax = data['form']['dta']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],

            'dtax': datax,

            # 'end_date':end_date,
            # 'project_id':self.env['project.project'].browse(project_id),
            # 'stage_id':self.env['project.task.type'].browse(stage_id),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
