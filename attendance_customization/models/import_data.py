from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import datetime as dt

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import time  as tm
import datetime
from odoo.exceptions import UserError, ValidationError
import base64
from xlrd import open_workbook
import xlrd
import pytz



class ImportAttendance(models.TransientModel):
    _name = 'attendance.import'

    file = fields.Binary(string='File Upload')

    def get_time(self, x):
        if x:
            x = int(x * 24 * 3600)  # convert to number of seconds
            minute = x / 60
            hour = minute / 60
            my_time = time(x // 3600, (x % 3600) // 60, x % 60)  # hours, minutes, seconds
            print(type(my_time))
            if my_time.minute == 0:
                return str(my_time.hour) + ':' + str(my_time.minute) + "0"
            else:
                return str(my_time.hour) + ':' + str(my_time.minute)

    def is_attendance_exist_sameday(self, employee_id, attendance_date):
        chk = self.env['attendance.custom'].search(
            [('employee_id', '=', employee_id), ('attendance_date', '=', attendance_date)])
        if len(chk) >= 1:
            return True
        else:
            return False

    def action_import_create_attendance(self):
        if self.file:
            wb = open_workbook(file_contents=base64.decodestring(self.file))
            sheet = wb.sheet_by_index(0)
            purchase_array = []

            # Row 2 , Column1
            attendance_date=None
            emp=False
            attendance_list = []
            last_attendance=None
            base_obj=self.env['to.base']
            checker=False
            for row in range(1, sheet.nrows):
                attendance_dict = {}
                id_no = int(sheet.cell(row, 0).value or 0)
                name = (sheet.cell(row, 1).value) or None
                if id_no <  0 and name not in [False,None,"",'']:
                    emp = self.env['hr.employee'].search([('name', '=', name)],limit=1)
                    checker=True
                elif  id_no>0:
                    emp = self.env['hr.employee'].search([('identification_id', '=', id_no)],limit=1)
                    checker=True
                else:
                    checker=False



                datexl = sheet.cell(row, 2).value or False
                # attendance_date = datetime(*xlrd.xldate_as_tuple(sheet.cell(row, 2).value, 0))
                if datexl:
                    attendance_date = xlrd.xldate.xldate_as_datetime(datexl, wb.datemode)
                    attendance_date = datetime.datetime.strftime(attendance_date, '%Y-%m-%d')
                    last_attendance = attendance_date

                if not attendance_date:
                    attendance_date = last_attendance

                if emp:
                    if attendance_date:
                        last_attendance = attendance_date
                        attend = self.get_attend_rec(emp,attendance_date)
                        if attend:

                            check_in = float(sheet.cell(row, 4).value or 0.00)
                            check_out = float(sheet.cell(row, 5).value or 0.00)

                            if check_in not in['0.0',0,'0'] and check_out not in['0.0',0,'0']:
                                check_in = datetime.datetime(*xlrd.xldate_as_tuple(check_in, wb.datemode)).strftime(
                                    '%Y-%m-%d %H:%M:%S')
                                check_out = datetime.datetime(*xlrd.xldate_as_tuple(check_out, wb.datemode)).strftime(
                                    '%Y-%m-%d %H:%M:%S')
                                if check_in and check_out:
                                    check_in = datetime.datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')
                                    check_out =datetime.datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')
                                    diff= check_out-check_in
                                    if diff.days >=0:
                                        self.create_custom_records(attend,check_in,check_out,attendance_date)

                                    else:
                                        temp=check_in
                                        check_in=check_out
                                        check_out=temp
                                        self.create_custom_records(attend, check_in, check_out,attendance_date)


    def create_custom_records(self, attendance_custom, ins,outs, date):
        # attendance_custom.employee_id.workschedule='08:00-13:00|14:00-17:00'
        check = self.create_checkins_outs(attendance_custom, ins,outs)
        # outs = self.create_checkins_outs(attendance_custom, check_outs)
        day = attendance_custom.attendance_date.strftime('%A')
        emp_working = attendance_custom.get_schedule_ot(attendance_custom.employee_id, day)
        if len(check) % 2 != 0:
            if attendance_custom.is_bonus_day:
                attendance_custom.absent = False
                attendance_custom.valid = True
                attendance_custom.is_modif = True
                attendance_custom.state = 'Modify'
            else:

                if check:
                    attendance_custom.absent = False
                    attendance_custom.valid = False
                    attendance_custom.is_modif = True
                    attendance_custom.state = 'Modify'
                    attendance_custom.apply_latein(emp_working['fsi'], (check[0].timestamp))
                # if len(check) == 0:
                #     attendance_custom.absent = True
                else:
                    attendance_custom.absent = True
                    attendance_custom.valid = True
                    attendance_custom.is_modif = True
                    attendance_custom.state = 'Modify'

                print("KONG")


        else:

            if len(check) == 0:
                day = date.strftime('%A')
                if day == 'Friday':
                    # attendance_custom.absent = False
                    # attendance_custom.valid = True
                    attendance_custom.unlink()
                else:
                    if attendance_custom.is_bonus_day:
                        attendance_custom.absent = False
                        attendance_custom.valid = True
                    else:
                        attendance_custom.valid = True
                        attendance_custom.absent = True
                        attendance_custom.is_modif = True
                        attendance_custom.state = 'Modify'

            else:
                # attendance_custom.working = self.calc_total_working_hours(check)
                attendance_custom.get_ot_hours()
                attendance_custom.valid = True
                attendance_custom.is_modif = False
                attendance_custom.absent = False
                attendance_custom.state = 'Validated'

            if check and attendance_custom:
                attendance_custom.apply_latein(emp_working['fsi'],self.get_local_time(attendance_custom.check_ins[0].timestamp))


    def create_checkins_outs(self,attendance_custom,ins,outs):
        moves=[]
        rcord = self.get_dict(ins, attendance_custom, 'checkin')
        moves += self.create_instance(rcord, 0)

        rcord = self.get_dict(outs, attendance_custom, 'checkout')
        moves += self.create_instance(rcord, 1)

        return moves

    def create_instance(self, move, status):
        chk_in_instance = self.env['check.ins']
        chk_out_instance = self.env['check.outs']
        ins = False
        if status in [0, 4]:
            ins = chk_in_instance.create(move)
        elif status in [1, 5]:
            ins = chk_out_instance.create(move)

        return ins


    def get_local_time(self, atten_time):
        if atten_time:
            atten_time = datetime.datetime.strptime(
                atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            local_tz = pytz.timezone(
                self.env.user.partner_id.tz or 'GMT')
            local_dt = local_tz.localize(atten_time, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            atten_time = datetime.datetime.strptime(
                utc_dt, "%Y-%m-%d %H:%M:%S")
            # atten_time = fields.Datetime.to_string(atten_time)
        return atten_time




    def get_dict(self, timestamp, attendance_custom,type):
        return {
            'timestamp': self.get_local_time(timestamp),
            'check': self.get_times(timestamp),
            'att_cus': attendance_custom.id,
            'status': type
        }

    def get_times(self, x):
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

    def get_attend_rec(self,rec,date):
        mydic = {
            'employee_id': rec.id,
            'attendance_date': date,
        }
        is_exist = self.env['attendance.custom'].with_context(
                            tz=self.env.user.tz or 'UTC').search(
            [('employee_id', '=', rec.id), ('attendance_date', '=', date)], limit=1)
        if not is_exist:
            attendance_custom = self.env['attendance.custom'].create(mydic)
            return  attendance_custom
        elif is_exist:
            if is_exist.valid:
                return False
            else:
                is_exist.check_ins.unlink()
                is_exist.check_outs.unlink()
                return  is_exist



    def action_create_attendance(self,attendance_records):
        for rec in attendance_records:
            attendance_dict = {}
            id_no = int(sheet.cell(row, 0).value)
            emp = self.env['hr.employee'].search([('identification_id', '=', id_no)])
            if not emp:
               pass
            else:

                first_in = sheet.cell(row, 7).value
                first_out = sheet.cell(row, 8).value
                second_in = sheet.cell(row, 12).value
                second_out = sheet.cell(row, 13).value
                exception_approved = sheet.cell(row, 26).value
                attendance_dict['employee_id'] = emp.id
                attendance_dict['attendance_date'] = attendance_date
                attendance_dict['first_in'] = self.get_time(first_in)
                attendance_dict['first_out'] = self.get_time(first_out)
                attendance_dict['second_in'] = self.get_time(second_in)
                attendance_dict['second_out'] = self.get_time(second_out)
                attendance_dict['exception_approved'] = exception_approved
                attendance_list.append(attendance_dict)

        if attendance_list:
            # create attendance records for each one, check if attendance not found on same date, else give error already exist.
            for obj in attendance_list:
                if obj['employee_id'] and obj['attendance_date']:
                    print('yes..', obj['employee_id'], obj['attendance_date'])
                    self.env['attendance.custom'].create({'employee_id': obj['employee_id'],
                                                          'attendance_date': datetime.datetime.strptime(
                                                              str(obj['attendance_date']), '%d/%m/%Y'),
                                                          'first_check_in': obj['first_in'],
                                                          'first_check_out': obj['first_out'],
                                                          'second_check_in': obj['second_in'],
                                                          'second_check_out': obj['second_out'],
                                                          'exception_approved': obj['exception_approved']})

