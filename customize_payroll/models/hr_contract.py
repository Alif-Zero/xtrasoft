from odoo import models, fields,api, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class HRContract(models.Model):
    _inherit = 'hr.contract'

    def CalBaseSalary(self,category,contract,payslip):
        monthly_wage=contract.wage
        return monthly_wage
        present_records=self.env['hr.attendance'].search([
            ('employee_id','=',contract.employee_id.id),
            ('attendance_date','>=',payslip.date_from),
            ('attendance_date','<=',payslip.date_to),
            ('status','in',['Present', 'Half Day', 'On Leave'])
            ])
        
        holiday_records_weekly = self.env['date.holiday'].search([
            ('date','>=',payslip.date_from),
            ('date','<=',payslip.date_to),
            ('type','=','Weekly Holiday')
            ])
        holiday_records_public = self.env['date.holiday'].search([
            ('date','>=',payslip.date_from),
            ('date','<=',payslip.date_to),
            ('type','=','Public Holiday')
            ])
        
        total_records=self.env['hr.attendance'].search([
            ('employee_id','=',contract.employee_id.id),
            ('attendance_date','>=',payslip.date_from),
            ('attendance_date','<=',payslip.date_to),
            ('status','in',['Absent','Present', 'Half Day', 'On Leave'])
            ])
        
        absent_records=self.env['hr.attendance'].search([
            ('employee_id','=',contract.employee_id.id),
            ('attendance_date','>=',payslip.date_from),
            ('attendance_date','<=',payslip.date_to),
            ('status','=','Absent')
            ])
        
        no_of_days = 30.5
        diff = (payslip.date_to - payslip.date_from).days
        diff += 1
        
        if diff == 30:
            no_of_days = 30
        elif diff == 31:
            no_of_days = 31
        
        daily_wage=(contract.wage)/no_of_days
        earned_holidays=0
        total_days=0
        total_wage=0
        
        if 7 <= len(present_records) <= 13:
            earned_holidays=1
        elif 14 <= len(present_records) <= 20:
            earned_holidays=2          
        elif len(present_records)==21:
            earned_holidays=3
        elif len(present_records)>21:
            earned_holidays=len(holiday_records_weekly)
        else:
            earned_holidays=0
        
        earned_holidays += len(holiday_records_public)
        total_records=len(total_records)
        total_days=total_records+earned_holidays
        
        total_wage=daily_wage*total_days
        # return total_wage
        
#half day deduction
    def LateCountDeduction(self,category,contract,payslip):
        attendance_ids=self.env['hr.attendance'].search([('employee_id','=',contract.employee_id.id),('attendance_date','>=',payslip.date_from),('attendance_date','<=',payslip.date_to),('status','=','Half Day')])
        count=0
        no_of_days = 30.5
        diff = (payslip.date_to - payslip.date_from).days
        diff += 1
        
        if diff == 30:
            no_of_days = 30
        elif diff == 31:
            no_of_days = 31
        for attendance in attendance_ids:
            # print(attendance_ids.attendance_date,'aff',self.env['hr.leave'].search([('date_from','>=',attendance.attendance_date),('date_to','<=',attendance.attendance_date),('state','not in',('cancel','draft'))]))
            if not self.env['hr.leave'].search([('date_from','>=',attendance.attendance_date),('date_to','<=',attendance.attendance_date),('state','not in',('cancel','draft'))]):
                count+=1
        return round((contract.wage/no_of_days)*(count/2))
# holiday deduct
    def DeductionSunday(self,category,contract,payslip):
        attendance_ids=self.env['hr.attendance'].search([
            ('employee_id','=',contract.employee_id.id),
            ('attendance_date','>=',payslip.date_from),
            ('attendance_date','<=',payslip.date_to),
            ('status','=','Absent')
        ])
        absent_count=0
        no_of_days = 30.5
        diff = (payslip.date_to - payslip.date_from).days
        diff += 1
        
        if diff == 30:
            no_of_days = 30
        elif diff == 31:
            no_of_days = 31
        for attendance in attendance_ids:
            if not self.env['hr.leave'].search([
                ('employee_id','=',contract.employee_id.id),
                ('date_from','>=',attendance.attendance_date),
                ('date_to','<=',attendance.attendance_date),
                ('state','not in',('cancel','draft'))
            ]):
                absent_count+=1
        holiday_count = 0
        if absent_count >= 6 and absent_count < 12:
            holiday_count = 1
        elif absent_count >= 12 and absent_count < 18 :
            holiday_count = 2
        elif absent_count >= 18 and absent_count < 24:
            holiday_count = 3
        elif absent_count >= 24 and absent_count < 28:
            holiday_count = 4
        elif absent_count >= 28:
            holiday_count = 5
        return round((contract.wage/no_of_days)*(holiday_count))

#absent deudction
    def LateCountDeductionAbsent(self,category,contract,payslip):
        attendance_ids=self.env['hr.attendance'].search([
            ('employee_id','=',contract.employee_id.id),
            ('attendance_date','>=',payslip.date_from),
            ('attendance_date','<=',payslip.date_to),
            ('status','=','Absent')])
        count=0
        no_of_days = 30.5
        diff = (payslip.date_to - payslip.date_from).days
        diff += 1
        
        if diff == 30:
            no_of_days = 30
        elif diff == 31:
            no_of_days = 31
        for attendance in attendance_ids:
            if not self.env['hr.leave'].search([
                ('employee_id','=',contract.employee_id.id),
                ('date_from','>=',attendance.attendance_date),
                ('date_to','<=',attendance.attendance_date),
                ('state','not in',('cancel','draft'))]):
                count+=1

        return round((contract.wage/no_of_days)*(count))