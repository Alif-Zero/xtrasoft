import datetime
from datetime import datetime, timedelta
import xlsxwriter
import pandas
from odoo import models, fields, api

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AttendanceXlsxReport(models.TransientModel):
    _name = "attendance.report"

    date_from = fields.Date(string='From Date', required='1', help='select start date')
    date_to = fields.Date(string='To Date', required='1', help='select end date')

    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env.ref('to_attendance_device.attendance_report_xlsx_id').report_action(self, data=data,
                                                                                            config=False)


class AttendanceReportNew(models.AbstractModel):
    _name = 'report.to_attendance_device.attendance_reports'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, docids, data=None):
        doc = docids
        form = doc.get('form')
        start_date = form['date_from']
        end_date = form['date_to']
        date_lists=[]

        domain = []
        if start_date:
            domain.append(('timestamp', '>=', start_date))
        if end_date:
            domain.append(('timestamp', '<=', end_date))
            print(pandas.date_range(start_date, end_date, freq='d').strftime('%Y-%m-%d').tolist())
            date_lists=pandas.date_range(start_date, end_date, freq='d').strftime('%Y-%m-%d').tolist()

        # print(self.dates_bwn_twodates(start_date, end_date))
        sheet = workbook.add_worksheet('Attendance')
        bold = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#fffbed', 'border': True})
        title = workbook.add_format(
            {
                'bold': True,
                'align': 'center',
                'font_size': 20,
                'bg_color': '#f2eee4',
                'border': True,
            })
        header_row_style = workbook.add_format(
            {
                'bold': True,
                'align': 'center',
                'border': True,
                'bg_color': '#f2eee4',
            })
        # sheet.merge_range('A3:N1', 'Attendance Report', title)
        row = 2
        col = 0

        # Header row
        sheet.set_column(0, 19, 18)
        sheet.write(row, col, 'Emp Number ', header_row_style)
        sheet.write(row, col + 1, 'Employee name', header_row_style)
        sheet.write(row, col + 2, 'date', header_row_style)
        sheet.write(row, col + 3, 'checkin time', header_row_style)
        sheet.write(row, col + 4, 'check out time', header_row_style)
        sheet.write(row, col + 5, 'total working', header_row_style)
        row += 2

        attendance = self.env['user.attendance'].search(domain)
        print(attendance[0].timestamp.date())
        employee_ids=attendance.mapped('employee_id')
        checkin_coll = []
        checkout_coll = []
        generated=[]
        print(employee_ids)
        for employee in employee_ids:
            if employee not in generated:
                # employee_rec=self.env['hr.employee'].search([('id','=',employee)],limit=1)
                generated.append(employee)
                for date in date_lists:
                    print('in date',date)
                    generate=True
                    print(attendance.filtered(lambda x:x.employee_id==employee and x.status==0 and date==str(x.timestamp.date())))
                    # print(i.timestamp.date(),'attendance_date')
                    for i in attendance.filtered(lambda x:x.employee_id==employee and x.status==0 and date==str(x.timestamp.date())):
                        print(i)
                        c = i.timestamp
                        checkin_coll.append(c)
                    for i in attendance.filtered(lambda x:x.employee_id==employee and x.status==1 and date==str(x.timestamp.date())):
                        print(i)
                        c = i.timestamp
                        checkout_coll.append(c)
                    print(len(checkin_coll))
                    print(len(checkout_coll))
                    if len(checkin_coll)> 0 and len(checkout_coll)>0:
                        min_date = min(checkin_coll)
                        max_date = max(checkout_coll)
                        total_cal = max_date - min_date
                        
                        h = abs(total_cal)
                        sheet.write(row, col, employee.id if i.employee_id.id else '/')
                        sheet.write(row, col + 1, employee.name if i.employee_id.name else '/')
                        sheet.write(row, col + 2, str(date))
                        sheet.write(row, col + 3, str(min_date))
                        sheet.write(row, col + 4, str(max_date))
                        sheet.write(row, col + 5, str(h))
                        row += 1
                        checkin_coll=[]
                        checkout_coll=[]