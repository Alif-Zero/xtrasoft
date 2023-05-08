# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class logsrdetDetails(models.TransientModel):
    _name = 'emplog.wage.details'
    _description = "Project Report Details"

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)

    def get_tot_val(self, emps):
        dix = {}
        wage = 0
        tallow = 0
        hallow = 0
        gosi = 0
        net = 0
        for rec in emps:
            wage += rec.contract_id.wage
            tallow += rec.contract_id.travel_allowance
            hallow += rec.contract_id.housing_allowance
            gosi += rec.contract_id.gosi_salery
            net += rec.contract_id.housing_allowance + rec.contract_id.wage + rec.contract_id.travel_allowance
        dix['wage']=wage
        dix['tallow']=tallow
        dix['hallow']=hallow
        dix['gosi']=gosi
        dix['nets']=net
        return dix

    def print_report(self):
        plist = []

        dept = self.env['hr.department'].search(
            [])

        for dpt in dept:
            dix = {}
            dix['data'] = 'd'
            dix['div'] = dpt.name


            emps = self.env['hr.employee'].search(
                [('contract_id.grade.department', '=', dpt.id)])
            gettot = self.get_tot_val(emps)
            dix['waget'] = gettot.get('wage')
            dix['tallowt'] = gettot.get('tallow')
            dix['hallowt'] = gettot.get('hallow')
            dix['gosit'] = gettot.get('gosi')
            dix['netst'] = gettot.get('nets')
            plist.append(dix)


            for rec in emps:
                dix = {}

                dix['emp'] = rec.name
                dix['roll'] = rec.identification_id
                dix['doj'] = rec.date_of_join
                dix['div'] = rec.contract_id.grade.department.name
                dix['wage'] = rec.contract_id.wage
                dix['hallow'] = rec.contract_id.housing_allowance
                dix['tallow'] = rec.contract_id.travel_allowance
                dix['gosi_deduc'] = rec.contract_id.gosi_salery

                dix[
                    'nets'] = rec.contract_id.housing_allowance + rec.contract_id.wage + rec.contract_id.travel_allowance

                dix['data'] = 'nd'

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
        return self.env.ref('design_creative_custom.action_report_salary_listing').report_action(self, data=data)


class emplogscxReport(models.AbstractModel):
    _name = 'report.design_creative_custom.salary_report_empx'
    _description = "Emp Wage Report"

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
