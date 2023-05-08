# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from io import BytesIO
import base64

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')

class pyslippytDetails(models.TransientModel):
    _name = 'payslip.summery.details'
    _description = "Project Report Details"

    month = fields.Selection(
        [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'), ('7', 'Jul')
            , ('8', 'Aug'), ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')], 'Month',
        required=True)
    year = fields.Selection([(str(num), str(num)) for num in range(2000, (datetime.now().year) + 20)], 'Year',
                            required=True)


    def generate_excel_report(self):
        data = base64.encodestring(self.print_report())
        report_name = 'payslip Report.xls'
        report_id = self.env['master.report.out'].sudo().create(
            {'filedata': data, 'filename': 'payslip report.xls'})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=master.report.out&field=filedata&id=%s&filename=%s.xls' % (
            report_id.id, report_name),
            'target': 'new',
        }

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
        month = self.month
        year = self.year
        grand = 0.0

        dept = self.env['hr.department'].search(
            [])

        for rec in dept:
            dix = {}
            dix['data'] = 'd'
            dix['div'] = rec.name
            plist.append(dix)

            emps = self.env['hr.employee'].search(
                [('contract_id.grade.department', '=', rec.id)])
            # gettot = self.get_tot_val(emps)
            # dix['wage'] = gettot.get('wage')
            # dix['tallow'] = gettot.get('tallow')
            # dix['hallow'] = gettot.get('hallow')
            # dix['gosi'] = gettot.get('gosi')
            # dix['nets'] = gettot.get('nets')
            # plist.append(dix)
            for dec in emps:
                slip = self.env['hr.payslip'].search(
                    [('contract_id', '=', dec.contract_id.id)])
                dix = {}
                if slip:
                    for slp in slip:
                        if slp.date_from.month == int(month) and slp.date_from.year == int(year):
                            deduc = 0.0
                            ot_tot = 0.0

                            dix['data'] = 'nd'
                            dix['div'] = rec.name
                            dix['date'] = dec.date_of_join
                            dix['emp'] = dec.name
                            dix['id'] = dec.identification_id

                            dix['worked'] = slp.consider_days
                            dix['absent'] = slp.absents
                            dix['desig'] = dec.contract_id.grade.designation.name
                            dix['sick']=slp.sick_leaves

                            for nep in slp.line_ids:
                                if nep.category_id.name == "Deduction":
                                    deduc += nep.total
                                if nep.name in ["OT(1.5) Allowance", "OT (125) Allowance"]:
                                    ot_tot += nep.total
                                if nep.name == 'Net Salary':
                                    grand += nep.total

                                dix[nep.name] = nep.total
                            dix['deduc'] = deduc
                            dix['ot_tot'] = ot_tot
                        else:
                            dix['data'] = 'nd'
                            dix['div'] = rec.name
                            dix['date'] = dec.date_of_join
                            dix['emp'] = dec.name
                            dix['id'] = dec.identification_id


                else:
                    dix['data'] = 'nd'
                    dix['div'] = rec.name
                    dix['date'] = dec.date_of_join
                    dix['emp'] = dec.name
                    dix['id'] = dec.identification_id

                plist.append(dix)
        plist.append(
            {'data': 'n', 'grand': grand})

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'month': self.month,
                'year': self.year,
                'dta': plist
            },
        }
        return self.generate_xlsx_report(self, lines=data)

        # return self.env.ref('design_creative_custom.pyslipxc_payslip_report_xlsx_id').report_action(self, data=data)


    def generate_xlsx_report(self, workbook, lines, data=None):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)

        month = lines['form']['month']
        year = lines['form']['year']
        dta = lines['form']['dta']

        sign_head_grand = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'blue',
            'font_size': '12',

        })

        sign_head = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '11',

        })

        std_heading = workbook.add_format({
            "bold": 0,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'navy',
            'font_size': '10',
        })

        format2 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'blue',
            'font_size': '25',
        })

        sheet = workbook.add_worksheet('MasterSheet')

        sheet.merge_range(2, 5, 3, 10, "Payslip report", format2)

        sheet.merge_range(2, 1, 2, 2, "Month", sign_head)
        sheet.merge_range(3, 1, 3, 2, "Year", sign_head)

        sheet.merge_range(2, 3, 2, 4, month, std_heading)
        sheet.merge_range(3, 3, 3, 4, year, std_heading)

        row = 4
        col = 0
        sheet.set_column(row, col, 30)
        sheet.write(row, col, "Roll#", sign_head)

        sheet.set_column(row, col + 1, 40)
        sheet.write(row, col + 1, "Name", sign_head)
        sheet.set_column(row, col + 2, 30)
        sheet.write(row, col + 2, "Date of Join", sign_head)
        sheet.set_column(row, col + 3, 30)

        sheet.write(row, col + 3, "Designation", sign_head)

        sheet.write(row, col + 4, "Worked", sign_head)
        sheet.write(row, col + 5, "Absent", sign_head)

        sheet.write(row, col + 6, "sick leave", sign_head)

        sheet.write(row, col + 7, "Basic Salary", sign_head)
        sheet.write(row, col + 8, "Travel Allowance", sign_head)
        sheet.write(row, col + 9, "Housing Allowance", sign_head)

        sheet.write(row, col + 10, "OT1", sign_head)
        sheet.write(row, col + 11, "OT2", sign_head)
        sheet.write(row, col + 12, "Total OT", sign_head)

        sheet.write(row, col + 13, "Loan", sign_head)
        sheet.write(row, col + 14, "Hours Deduction", sign_head)

        sheet.write(row, col + 15, "GOSI Salary deductions", sign_head)
        sheet.write(row, col + 16, "Gross Pay", sign_head)
        sheet.write(row, col + 17, "Deduction", sign_head)

        sheet.write(row, col + 18, "Net Pay", sign_head)

        row = 6
        col = 0
        for rec in dta:

            if rec.get('data') == 'd':
                sheet.set_column(row + 1, col, 20)
                sheet.write(row + 1, col, rec.get('div'), sign_head)
                # sheet.write(row + 1, col + 1, rec.get('ID'), std_heading)
                # sheet.write(row + 1, col + 2, rec.get('ID'), std_heading)
                # sheet.write(row + 1, col + 3, rec.get('ID'), std_heading)
                row += 1

            if rec.get('data') == 'n':
                sheet.write(row + 1, 0, "Grand Total", sign_head_grand)

                sheet.set_column(row + 1, col, 20)
                sheet.write(row + 1, col + 17, rec.get('grand'), sign_head_grand)

            if rec.get('data') == 'nd':
                sheet.set_column(row, col, 10)
                sheet.write(row, col, rec.get('id'), std_heading)

                sheet.set_column(row, col + 1, 40)
                sheet.write(row, col + 1, rec.get('emp'), std_heading)

                sheet.set_column(row, col + 2, 15)
                sheet.write(row, col + 2, rec.get('date'), std_heading)

                sheet.set_column(row, col + 3, 15)
                sheet.write(row, col + 3, rec.get('desig'), std_heading)

                sheet.set_column(row, col + 4, 10)
                sheet.write(row, col + 4, rec.get('worked'), std_heading)

                sheet.set_column(row, col + 5, 10)
                sheet.write(row, col + 5, rec.get('absent'), std_heading)

                sheet.set_column(row, col + 6, 10)
                sheet.write(row, col + 6, rec.get('sick'), std_heading)

                sheet.set_column(row, col + 7, 10)
                sheet.write(row, col + 7, rec.get('Basic Salary'), std_heading)
                sheet.set_column(row, col + 8, 10)
                sheet.write(row, col + 8, rec.get('Travel Allowance'), std_heading)
                sheet.set_column(row, col + 9, 10)
                sheet.write(row, col + 9, rec.get('Housing Allowance'), std_heading)

                sheet.set_column(row, col + 10, 15)
                sheet.write(row, col + 10, rec.get('OT (125) Allowance'), std_heading)
                sheet.set_column(row, col + 11, 15)
                sheet.write(row, col + 11, rec.get('OT(1.5) Allowance'), std_heading)
                sheet.set_column(row, col + 12, 10)
                sheet.write(row, col + 12, rec.get('ot_tot'), std_heading)

                sheet.set_column(row, col + 13, 10)
                sheet.write(row, col + 13, rec.get('Loan Earning'), std_heading)
                sheet.set_column(row, col + 14, 15)
                sheet.write(row, col + 14, rec.get('Late In Deduction'), std_heading)
                sheet.set_column(row, col + 15, 15)

                sheet.write(row, col + 15, rec.get('Gosi Deduction'), std_heading)
                sheet.set_column(row, col + 16, 10)
                sheet.write(row, col + 16, rec.get('Gross'), std_heading)
                sheet.set_column(row, col + 17, 10)
                sheet.write(row, col + 17, rec.get('deduc'), std_heading)
                sheet.set_column(row, col + 18, 10)

                sheet.write(row, col + 18, rec.get('Net Salary'), std_heading)

            row += 1
        workbook.close()
        fp.seek(0)
        result = fp.read()

        return result



# class pylsiprelipReportExcel(models.AbstractModel):
#     _name = 'report.design_creative_custom.report_xlsx_ciew'
#     # _inherit = 'report.odoo_report_xlsx.abstract'
#
#     def generate_xlsx_report(self, workbook, lines, data=None):
#
#         month = lines['form']['month']
#         year = lines['form']['year']
#         dta = lines['form']['dta']
#
#         sign_head_grand = workbook.add_format({
#             "bold": 1,
#             "border": 1,
#             "align": 'center',
#             "valign": 'vcenter',
#             "font_color": 'blue',
#             'font_size': '12',
#
#         })
#
#         sign_head = workbook.add_format({
#             "bold": 1,
#             "border": 1,
#             "align": 'center',
#             "valign": 'vcenter',
#             "font_color": 'black',
#             'font_size': '11',
#
#         })
#
#         std_heading = workbook.add_format({
#             "bold": 0,
#             "border": 1,
#             "align": 'center',
#             "valign": 'vcenter',
#             "font_color": 'navy',
#             'font_size': '10',
#         })
#
#         format2 = workbook.add_format({
#             "bold": 1,
#             "border": 1,
#             "align": 'center',
#             "valign": 'vcenter',
#             "font_color": 'blue',
#             'font_size': '25',
#         })
#
#         sheet = workbook.add_worksheet('MasterSheet')
#
#         sheet.merge_range(2, 5, 3, 10, "Payslip report", format2)
#
#         sheet.merge_range(2, 1, 2, 2, "Month", sign_head)
#         sheet.merge_range(3, 1, 3, 2, "Year", sign_head)
#
#         sheet.merge_range(2, 3, 2, 4, month, std_heading)
#         sheet.merge_range(3, 3, 3, 4, year, std_heading)
#
#         row = 4
#         col = 0
#         sheet.set_column(row, col, 30)
#         sheet.write(row, col, "Roll#", sign_head)
#
#         sheet.set_column(row, col + 1, 40)
#         sheet.write(row, col + 1, "Name", sign_head)
#         sheet.set_column(row, col + 2, 30)
#         sheet.write(row, col + 2, "Date of Join", sign_head)
#         sheet.set_column(row, col + 3, 30)
#
#         sheet.write(row, col + 3, "Designation", sign_head)
#
#         sheet.write(row, col + 4, "Worked", sign_head)
#         sheet.write(row, col + 5, "Absent", sign_head)
#
#         sheet.write(row, col + 6, "sick leave", sign_head)
#
#         sheet.write(row, col + 7, "Basic Salary", sign_head)
#         sheet.write(row, col + 8, "Travel Allowance", sign_head)
#         sheet.write(row, col + 9, "Housing Allowance", sign_head)
#
#         sheet.write(row, col + 10, "OT1", sign_head)
#         sheet.write(row, col + 11, "OT2", sign_head)
#         sheet.write(row, col + 12, "Total OT", sign_head)
#
#         sheet.write(row, col + 13, "Loan", sign_head)
#         sheet.write(row, col + 14, "Hours Deduction", sign_head)
#
#         sheet.write(row, col + 15, "GOSI Salary deductions", sign_head)
#         sheet.write(row, col + 16, "Gross Pay", sign_head)
#         sheet.write(row, col + 17, "Deduction", sign_head)
#
#         sheet.write(row, col + 18, "Net Pay", sign_head)
#
#         row = 6
#         col = 0
#         for rec in dta:
#
#             if rec.get('data') == 'd':
#                 sheet.set_column(row + 1, col, 20)
#                 sheet.write(row + 1, col, rec.get('div'), sign_head)
#                 # sheet.write(row + 1, col + 1, rec.get('ID'), std_heading)
#                 # sheet.write(row + 1, col + 2, rec.get('ID'), std_heading)
#                 # sheet.write(row + 1, col + 3, rec.get('ID'), std_heading)
#                 row += 1
#
#             if rec.get('data') == 'n':
#                 sheet.write(row + 1, 0, "Grand Total", sign_head_grand)
#
#                 sheet.set_column(row + 1, col, 20)
#                 sheet.write(row + 1, col + 17, rec.get('grand'), sign_head_grand)
#
#             if rec.get('data') == 'nd':
#                 sheet.set_column(row, col, 10)
#                 sheet.write(row, col, rec.get('id'), std_heading)
#
#                 sheet.set_column(row, col + 1, 40)
#                 sheet.write(row, col + 1, rec.get('emp'), std_heading)
#
#                 sheet.set_column(row, col + 2, 15)
#                 sheet.write(row, col + 2, rec.get('date'), std_heading)
#
#                 sheet.set_column(row, col + 3, 15)
#                 sheet.write(row, col + 3, rec.get('desig'), std_heading)
#
#                 sheet.set_column(row, col + 4, 10)
#                 sheet.write(row, col + 4, rec.get('worked'), std_heading)
#
#                 sheet.set_column(row, col + 5, 10)
#                 sheet.write(row, col + 5, rec.get('absent'), std_heading)
#
#                 sheet.set_column(row, col + 6, 10)
#                 sheet.write(row, col + 6, rec.get('sick'), std_heading)
#
#                 sheet.set_column(row, col + 7, 10)
#                 sheet.write(row, col + 7, rec.get('Basic Salary'), std_heading)
#                 sheet.set_column(row, col + 8, 10)
#                 sheet.write(row, col + 8, rec.get('Travel Allowance'), std_heading)
#                 sheet.set_column(row, col + 9, 10)
#                 sheet.write(row, col + 9, rec.get('Housing Allowance'), std_heading)
#
#                 sheet.set_column(row, col + 10, 15)
#                 sheet.write(row, col + 10, rec.get('OT (125) Allowance'), std_heading)
#                 sheet.set_column(row, col + 11, 15)
#                 sheet.write(row, col + 11, rec.get('OT(1.5) Allowance'), std_heading)
#                 sheet.set_column(row, col + 12, 10)
#                 sheet.write(row, col + 12, rec.get('ot_tot'), std_heading)
#
#                 sheet.set_column(row, col + 13, 10)
#                 sheet.write(row, col + 13, rec.get('Loan Earning'), std_heading)
#                 sheet.set_column(row, col + 14, 15)
#                 sheet.write(row, col + 14, rec.get('Late In Deduction'), std_heading)
#                 sheet.set_column(row, col + 15, 15)
#
#                 sheet.write(row, col + 15, rec.get('Gosi Deduction'), std_heading)
#                 sheet.set_column(row, col + 16, 10)
#                 sheet.write(row, col + 16, rec.get('Gross'), std_heading)
#                 sheet.set_column(row, col + 17, 10)
#                 sheet.write(row, col + 17, rec.get('deduc'), std_heading)
#                 sheet.set_column(row, col + 18, 10)
#
#                 sheet.write(row, col + 18, rec.get('Net Salary'), std_heading)
#
#             row += 1
#
#     def _get_objs_for_report(self, docids, data):
#         """
#         Returns objects for xlx report.  From WebUI these
#         are either as docids taken from context.active_ids or
#         in the case of wizard are in data.  Manual calls may rely
#         on regular context, setting docids, or setting data.
#
#         :param docids: list of integers, typically provided by
#             qwebactionmanager for regular Models.
#         :param data: dictionary of data, if present typically provided
#             by qwebactionmanager for TransientModels.
#         :param ids: list of integers, provided by overrides.
#         :return: recordset of active model for ids.
#         """
#         if docids:
#             ids = docids
#         elif data and 'context' in data:
#             ids = data["context"].get('active_ids', [])
#         else:
#             ids = self.env.context.get('active_ids', [])
#         return self.env[self.env.context.get('active_model')].browse(ids)
#
#     def create_xlsx_report(self, docids, data):
#         objs = self._get_objs_for_report(docids, data)
#         file_data = BytesIO()
#         workbook = xlsxwriter.Workbook(file_data, self.get_workbook_options())
#         self.generate_xlsx_report(workbook, data, objs)
#         workbook.close()
#         file_data.seek(0)
#         return file_data.read(), 'xlsx'
#
#     def get_workbook_options(self):
#         """
#         See https://xlsxwriter.readthedocs.io/workbook.html constructor options
#         :return: A dictionary of options
#         """
#         return {}
#
#     # def generate_xlsx_report(self, workbook, data, objs):
#     #     raise NotImplementedError()
