# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import base64
from io import BytesIO

import xlsxwriter


class masterReportOut(models.TransientModel):
    _name = 'master.report.out'

    filedata = fields.Binary('Download file', readonly=True)
    filename = fields.Char('Filename', size=64, readonly=True)


class empcostytDetails(models.TransientModel):
    _name = 'employee.cost.details'
    _description = "Project Report Details"

    date_from = fields.Date(required=True, string="Date from")
    date_to = fields.Date(required=True, string="Date To")

    employee_id = fields.Many2one('hr.employee', string="Employee")

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)

    def generate_excel_report(self):
        data = base64.encodestring(self.print_report())
        report_name = 'MasterSheet Report.xls'
        report_id = self.env['master.report.out'].sudo().create(
            {'filedata': data, 'filename': 'MasterSheet report.xls'})
        print(report_id, "233333333333333")
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=master.report.out&field=filedata&id=%s&filename=%s.xls' % (
            report_id.id, report_name),
            'target': 'new',
        }

    def print_report(self):
        plist = []
        regular_tot = 0.0
        display_regular_hrs = 0.0
        display_regular_mins = 0.0

        display_ot_hrs = 0.0
        display_ot_mins = 0.0

        display_regular = "00:00"
        ots_total = 0.0
        totx = 0.0
        sick = 0
        voca = 0
        hol = 0
        start_date = self.date_from
        end_date = self.date_to

        delta = timedelta(days=1)
        while start_date <= end_date:
            attend = self.env['attendance.custom'].search(
                [('attendance_date', '=', start_date), ('employee_id', '=', self.employee_id.id)], limit=1)
            if attend:
                day = attend.attendance_date.strftime('%A')
                regular = (attend.get_schedule_ot(self.employee_id, day)['min'] / 60)
                ot = 0.0
                if attend.working:
                    temp1 = float(str(attend.working).split(":")[0])
                    temp2 = float(str(attend.working).split(":")[1]) / 60
                    temp = temp1 + temp2
                    if (temp - regular) > 0:
                        ot = temp - regular

                        regular = temp
                        display_regular_hrs += float(str(attend.working).split(":")[0])
                        display_regular_mins += round(float(str(attend.working).split(":")[1]), 2)

                        display_ot_hrs += float(str(attend.ot_125).split(":")[0])
                        display_ot_mins += round(float(str(attend.ot_125).split(":")[1]), 2)

                        if attend.ot_15:
                            display_ot_hrs += float(str(attend.ot_15).split(":")[0])
                            display_ot_mins += round(float(str(attend.ot_15).split(":")[1]), 2)


                    else:
                        regular = temp
                        display_regular_hrs += float(str(attend.working).split(":")[0])
                        display_regular_mins += float(str(attend.working).split(":")[1])
                else:
                    regular = 0.0
                    display_regular_hrs += 0
                    display_regular_mins += 0

                deduc = 0.0
                ot_tot = 0.0
                holi = 0
                dix = {}
                dix['date'] = start_date
                dix['stime'] = attend.first_check_in or " "
                dix['etime'] = attend.second_check_out or " "
                dix['rhours'] = attend.working

                dix['OT'] = attend.ot_125

                leave_sick = self.env['attendance.custom'].search_count(
                    [('employee_id', '=', self.employee_id.id), ('sick_leave', '=', True)
                        , ('attendance_date', '=', start_date),
                     ])
                leave = self.env['attendance.custom'].search_count(
                    [('employee_id', '=', self.employee_id.id), ('leave', '=', True)
                        , ('attendance_date', '=', start_date),
                     ])
                check_holiday = self.env['hr.calendar.leave'].search([('follow', '=', True)], limit=1)
                if check_holiday:
                    for rec in check_holiday.leave:
                        if rec.leave_date.day == day and rec.leave_date.month == attend.month:
                            holi += 1

                dix['sick'] = leave_sick
                dix['vacation'] = leave
                dix['holi'] = holi

                dix['total'] = regular + ot
                totx += regular + ot
                # dix['ot_tot'] = ot_tot
                dix['data'] = 'y'

                regular_tot += regular
                ots_total += ot
                sick += leave_sick
                voca += leave
                hol += holi

                plist.append(dix)
            else:

                dix = {}
                dix['date'] = start_date
                dix['stime'] = 0
                dix['etime'] = 0
                dix['rhours'] = 0
                dix['OT'] = 0

                dix['sick'] = None
                dix['vacation'] = None
                dix['holi'] = None

                dix['total'] = 0
                dix['data'] = 'y'

                plist.append(dix)

            start_date += delta
        adhr = 0
        minad = 0
        if display_ot_mins >= 60:
            nep = round(display_ot_mins / 60, 2)
            adhr = int(str(nep).split(".")[0])
            minad = float(str(nep).split(".")[1])

        adhrr = 0
        minadr = 0

        if display_regular_mins >= 60:
            nepr = round(display_regular_mins / 60, 2)
            adhrr = int(str(nepr).split(".")[0])
            minadr = float(str(nepr).split(".")[1])

        display_ots = str(int(display_ot_hrs + adhr)) + ":" + str(int(minad))
        display_regular = str(int(display_regular_hrs + adhrr)) + ":" + str(int(minadr))

        totx_display_hrs = int(str(display_ots).split(":")[0]) + int(str(display_regular).split(":")[0])
        totx_display_mins = int(str(display_ots).split(":")[1]) + int(str(display_regular).split(":")[1])
        display_totx = str(totx_display_hrs) + ":" + str(totx_display_mins)

        plist.append(
            {'data': 'n', 'pay': 'x', 'reg': display_regular, 'ot': display_ots, 'sik': sick, 'voc': voca, 'holi': hol,
             'totx': display_totx})

        # ttoott= str(totx).split(".")[0]
        # ttoottmin= int(str(totx).split(".")[1])*10

        # ot_display=str(int(display_regular_hrs+ttoott))+":"+str(int(display_regular_mins+ttoottmin))
        plist.append(
            {'data': 'n', 'pay': 'f', 'reg': display_regular, 'ot': display_ots, 'sik': sick, 'voc': voca, 'holi': hol,
             'totx': display_totx})
        plist.append(
            {'data': 'n', 'pay': 't', 'reg': float(regular_tot * float(self.employee_id.contract_id.final_hourly_rate)),
             'ot': float(ots_total * self.employee_id.contract_id.final_hourly_rate)
                , 'totx': float(totx * self.employee_id.contract_id.final_hourly_rate), 'sik': sick, 'voc': voca,
             'holi': hol, })

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date': self.date_from,
                'dateto': self.date_to,
                'emp': self.employee_id.name,

                'dta': plist
            },
        }
        return self.generate_xlsx_report(self, lines=data)
        # return self.env.ref('attendance_customization.empcost_payslip_report_xlsx_id').report_action(self, data=data)

    def generate_xlsx_report(self, workbook, lines, data=None):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)

        datef = lines['form']['date']
        datet = lines['form']['dateto']
        emp = lines['form']['emp']

        dta = lines['form']['dta']

        sign_head = workbook.add_format({
            "bold": 1,
            "border": 0,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '12',

        })

        sign_head_sick = workbook.add_format({
            "bold": 1,
            "border": 0,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'blue',
            'font_size': '12',

        })
        sign_head_vaca = workbook.add_format({
            "bold": 1,
            "border": 0,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'red',
            'font_size': '12',

        })
        sign_head_holi = workbook.add_format({
            "bold": 1,
            "border": 0,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'green',
            'font_size': '12',

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
            "text_wrap": True,
            "font_color": 'blue',
            'font_size': '30',
        })

        sign_head_pay = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'navy blue',
            'font_size': '14',

        })

        sheet = workbook.add_worksheet('MasterSheet')

        # style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')

        sheet.merge_range(1, 3, 2, 6, "Employee Cost report", format2)

        sheet.merge_range(3, 1, 3, 2, "Employee", sign_head)
        # sheet.merge_range(1, 3, 2, 9, "Employee Cost report", format2)
        sheet.merge_range(4, 1, 4, 2, "Date from:", sign_head)
        sheet.merge_range(5, 1, 5, 2, "Date To:", sign_head)

        sheet.merge_range(3, 3, 3, 4, emp, std_heading)
        # sheet.merge_range(1, 3, 2, 9, "Employee Cost report", format2)
        sheet.merge_range(4, 3, 4, 4, datef, std_heading)
        sheet.merge_range(5, 3, 5, 4, datet, std_heading)

        row = 6
        col = 0
        sheet.set_column(row, col, 40)
        sheet.write(row, col, "Date", sign_head)

        sheet.write(row, col + 1, "START TIME", sign_head)
        sheet.write(row, col + 2, "FINISH TIME", sign_head)
        sheet.write(row, col + 3, "REGULAR HRS", sign_head)
        sheet.write(row, col + 4, "OVERTIME HRS", sign_head)

        sheet.write(row, col + 5, "SICK", sign_head_sick)
        sheet.write(row, col + 6, "VACATION", sign_head_vaca)
        sheet.write(row, col + 7, "HOLIDAY", sign_head_holi)

        sheet.write(row, col + 8, "TOTAL HOURS", sign_head)

        row = 8
        col = 0
        for rec in dta:

            if rec.get('data') == 'n':
                sheet.set_column(row + 1, col, 20)
                if rec.get('pay') == 'f':
                    sheet.write(row + 1, col + 2, "Total Hours", sign_head)

                elif rec.get('pay') == 'x':
                    sheet.write(row + 1, col + 2, "Total", sign_head)


                else:
                    sheet.write(row + 1, col + 2, "Total Payment", sign_head_pay)

                sheet.write(row + 1, col + 3, rec.get('reg'), sign_head)
                sheet.write(row + 1, col + 4, rec.get('ot'), sign_head)

                sheet.write(row + 1, col + 5, rec.get('sik'), sign_head)
                sheet.write(row + 1, col + 6, rec.get('voc'), sign_head)
                sheet.write(row + 1, col + 7, rec.get('holi'), sign_head)

                if 'totx' in rec:
                    sheet.write(row + 1, col + 8, rec.get('totx'), sign_head)

                # sheet.write(row + 1, col + 1, rec.get('ID'), std_heading)
                # sheet.write(row + 1, col + 2, rec.get('ID'), std_heading)
                # sheet.write(row + 1, col + 3, rec.get('ID'), std_heading)
                row += 1

            if rec.get('data') == 'y':
                sheet.set_column(row, col, 40)
                sheet.write(row, col, rec.get('date'), std_heading)

                sheet.set_column(row, col + 1, 40)
                sheet.write(row, col + 1, rec.get('stime'), std_heading)

                sheet.set_column(row, col + 2, 15)
                sheet.write(row, col + 2, rec.get('etime'), std_heading)

                sheet.set_column(row, col + 3, 10)
                sheet.write(row, col + 3, rec.get('rhours'), std_heading)

                sheet.set_column(row, col + 4, 10)
                sheet.write(row, col + 4, rec.get('OT'), std_heading)

                sheet.set_column(row, col + 5, 10)
                sheet.write(row, col + 5, rec.get('sick'), std_heading)
                sheet.set_column(row, col + 6, 10)
                sheet.write(row, col + 6, rec.get('vacation'), std_heading)
                sheet.set_column(row, col + 7, 10)
                sheet.write(row, col + 7, rec.get('holi'), std_heading)

                sheet.set_column(row, col + 8, 15)
                sheet.write(row, col + 8, rec.get('total'), std_heading)

            row += 1
        workbook.close()
        fp.seek(0)
        result = fp.read()

        return result

        # sheet.merge_range(row1, col, row1+4, col+4,sign_admin , std_heading2)

        # for rec in data.employee_id:
        #     sheet.write(row, col, 'Employee ID', main_heading)
        #     sheet.write_string(row, col + 1, str(rec.employee_code), main_heading)
        #     sheet.write(row, col + 2, 'Employee Name', main_heading)
        #     sheet.write_string(row, col + 3, str(rec.name), main_heading)
        #     sheet.write(row + 1, col, 'Job Position', main_heading)
        #     sheet.write_string(row + 1, col + 1, str(rec.job_id.name), main_heading)
        #     sheet.write(row + 1, col + 2, 'Joining Date', main_heading)
        #     sheet.write_string(row + 1, col + 3, rec.bsgjoining_date.strftime("%m/%d/%Y"))
        #     emp_payslip = self.env['hr.payslip'].search(
        #         [('employee_id', '=', rec.id), ('date_from', '<=', data.to_date),
        #          ('date_to', '>', data.from_date)])
        #     row += 3
        #     list_dict = []
        #     if emp_payslip:
        #         rule_dict = OrderedDict.fromkeys((rule.name for payslip in emp_payslip for rule in payslip.line_ids),
        #                                          0.0)
        #         rule_dict.move_to_end('Net Salary')
        #         sheet.write(row, col, 'Payslip Name', main_heading2)
        #         col += 1
        #         for rule_name in rule_dict:
        #             sheet.write_string(row, col, rule_name, main_heading2)
        #             col += 1
        #         row += 1
        #         col = 0



# class empcostipReportExcel(models.AbstractModel):
#     _name = 'report.attendance_customization.report_xlsx_csot'
#     # _inherit = 'report.odoo_report_xlsx.abstract'
#
#     def generate_xlsx_report(self, workbook, lines, data=None):
#
#         datef = lines['form']['date']
#         datet = lines['form']['dateto']
#         emp = lines['form']['emp']
#
#         dta = lines['form']['dta']
#
#         sign_head = workbook.add_format({
#             "bold": 1,
#             "border": 0,
#             "align": 'center',
#             "valign": 'vcenter',
#             "font_color": 'black',
#             'font_size': '12',
#
#         })
#
#         sign_head_sick = workbook.add_format({
#             "bold": 1,
#             "border": 0,
#             "align": 'center',
#             "valign": 'vcenter',
#             "font_color": 'blue',
#             'font_size': '12',
#
#         })
#         sign_head_vaca = workbook.add_format({
#             "bold": 1,
#             "border": 0,
#             "align": 'center',
#             "valign": 'vcenter',
#             "font_color": 'red',
#             'font_size': '12',
#
#         })
#         sign_head_holi = workbook.add_format({
#             "bold": 1,
#             "border": 0,
#             "align": 'center',
#             "valign": 'vcenter',
#             "font_color": 'green',
#             'font_size': '12',
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
#             "text_wrap": True,
#             "font_color": 'blue',
#             'font_size': '30',
#         })
#
#         sign_head_pay = workbook.add_format({
#             "bold": 1,
#             "border": 1,
#             "align": 'center',
#             "valign": 'vcenter',
#             "font_color": 'navy blue',
#             'font_size': '14',
#
#         })
#
#         sheet = workbook.add_worksheet('MasterSheet')
#
#         # style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')
#
#         sheet.merge_range(1, 3, 2, 6, "Employee Cost report", format2)
#
#         sheet.merge_range(3, 1, 3, 2, "Employee", sign_head)
#         # sheet.merge_range(1, 3, 2, 9, "Employee Cost report", format2)
#         sheet.merge_range(4, 1, 4, 2, "Date from:", sign_head)
#         sheet.merge_range(5, 1, 5, 2, "Date To:", sign_head)
#
#         sheet.merge_range(3, 3, 3, 4, emp, std_heading)
#         # sheet.merge_range(1, 3, 2, 9, "Employee Cost report", format2)
#         sheet.merge_range(4, 3, 4, 4, datef, std_heading)
#         sheet.merge_range(5, 3, 5, 4, datet, std_heading)
#
#         row = 6
#         col = 0
#         sheet.set_column(row, col, 40)
#         sheet.write(row, col, "Date", sign_head)
#
#         sheet.write(row, col + 1, "START TIME", sign_head)
#         sheet.write(row, col + 2, "FINISH TIME", sign_head)
#         sheet.write(row, col + 3, "REGULAR HRS", sign_head)
#         sheet.write(row, col + 4, "OVERTIME HRS", sign_head)
#
#         sheet.write(row, col + 5, "SICK", sign_head_sick)
#         sheet.write(row, col + 6, "VACATION", sign_head_vaca)
#         sheet.write(row, col + 7, "HOLIDAY", sign_head_holi)
#
#         sheet.write(row, col + 8, "TOTAL HOURS", sign_head)
#
#         row = 8
#         col = 0
#         for rec in dta:
#
#             if rec.get('data') == 'n':
#                 sheet.set_column(row + 1, col, 20)
#                 if rec.get('pay') == 'f':
#                     sheet.write(row + 1, col + 2, "Total Hours", sign_head)
#
#                 elif rec.get('pay') == 'x':
#                     sheet.write(row + 1, col + 2, "Total", sign_head)
#
#
#                 else:
#                     sheet.write(row + 1, col + 2, "Total Payment", sign_head_pay)
#
#                 sheet.write(row + 1, col + 3, rec.get('reg'), sign_head)
#                 sheet.write(row + 1, col + 4, rec.get('ot'), sign_head)
#
#                 sheet.write(row + 1, col + 5, rec.get('sik'), sign_head)
#                 sheet.write(row + 1, col + 6, rec.get('voc'), sign_head)
#                 sheet.write(row + 1, col + 7, rec.get('holi'), sign_head)
#
#                 if 'totx' in rec:
#                     sheet.write(row + 1, col + 8, rec.get('totx'), sign_head)
#
#                 # sheet.write(row + 1, col + 1, rec.get('ID'), std_heading)
#                 # sheet.write(row + 1, col + 2, rec.get('ID'), std_heading)
#                 # sheet.write(row + 1, col + 3, rec.get('ID'), std_heading)
#                 row += 1
#
#             if rec.get('data') == 'y':
#                 sheet.set_column(row, col, 40)
#                 sheet.write(row, col, rec.get('date'), std_heading)
#
#                 sheet.set_column(row, col + 1, 40)
#                 sheet.write(row, col + 1, rec.get('stime'), std_heading)
#
#                 sheet.set_column(row, col + 2, 15)
#                 sheet.write(row, col + 2, rec.get('etime'), std_heading)
#
#                 sheet.set_column(row, col + 3, 10)
#                 sheet.write(row, col + 3, rec.get('rhours'), std_heading)
#
#                 sheet.set_column(row, col + 4, 10)
#                 sheet.write(row, col + 4, rec.get('OT'), std_heading)
#
#                 sheet.set_column(row, col + 5, 10)
#                 sheet.write(row, col + 5, rec.get('sick'), std_heading)
#                 sheet.set_column(row, col + 6, 10)
#                 sheet.write(row, col + 6, rec.get('vacation'), std_heading)
#                 sheet.set_column(row, col + 7, 10)
#                 sheet.write(row, col + 7, rec.get('holi'), std_heading)
#
#                 sheet.set_column(row, col + 8, 15)
#                 sheet.write(row, col + 8, rec.get('total'), std_heading)
#
#             row += 1
#
#         # sheet.merge_range(row1, col, row1+4, col+4,sign_admin , std_heading2)
#
#         # for rec in data.employee_id:
#         #     sheet.write(row, col, 'Employee ID', main_heading)
#         #     sheet.write_string(row, col + 1, str(rec.employee_code), main_heading)
#         #     sheet.write(row, col + 2, 'Employee Name', main_heading)
#         #     sheet.write_string(row, col + 3, str(rec.name), main_heading)
#         #     sheet.write(row + 1, col, 'Job Position', main_heading)
#         #     sheet.write_string(row + 1, col + 1, str(rec.job_id.name), main_heading)
#         #     sheet.write(row + 1, col + 2, 'Joining Date', main_heading)
#         #     sheet.write_string(row + 1, col + 3, rec.bsgjoining_date.strftime("%m/%d/%Y"))
#         #     emp_payslip = self.env['hr.payslip'].search(
#         #         [('employee_id', '=', rec.id), ('date_from', '<=', data.to_date),
#         #          ('date_to', '>', data.from_date)])
#         #     row += 3
#         #     list_dict = []
#         #     if emp_payslip:
#         #         rule_dict = OrderedDict.fromkeys((rule.name for payslip in emp_payslip for rule in payslip.line_ids),
#         #                                          0.0)
#         #         rule_dict.move_to_end('Net Salary')
#         #         sheet.write(row, col, 'Payslip Name', main_heading2)
#         #         col += 1
#         #         for rule_name in rule_dict:
#         #             sheet.write_string(row, col, rule_name, main_heading2)
#         #             col += 1
#         #         row += 1
#         #         col = 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
