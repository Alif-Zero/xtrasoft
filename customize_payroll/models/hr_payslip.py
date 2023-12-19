# -*- coding: utf-8 -*-

from odoo import models, api, fields
import logging
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    
    def _check_undefined_slots(self, work_entries, payslip_run):
        return True

    def _get_available_contracts_domain(self):
        super(HrPayslipEmployees,self)._get_available_contracts_domain()
        return [('contract_ids.state', 'in', ('open', 'probation')), ('company_id', '=', self.env.company.id)]


class PayslipWorkDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    total_present = fields.Float('Number of Presents',compute='_cal_total_presents',store=True)
    total_absent = fields.Float('Number of Absents',compute='_cal_total_absent',store=True)
    
    @api.depends('payslip_id.employee_id','payslip_id.date_from','payslip_id.date_to')
    def _cal_total_presents(self):
        for each in self:
            each.total_present=0
            if each.payslip_id.date_from and each.payslip_id.date_to and each.payslip_id.employee_id and each.work_entry_type_id.name=='Attendance':
                attendance_obj=self.env['hr.attendance'].search([('attendance_date','>=',each.payslip_id.date_from),('attendance_date','<=',each.payslip_id.date_to),('employee_id','=',each.payslip_id.employee_id.id),('status','=','Present')])
                each.total_present=len(attendance_obj)
#             if each.payslip_id.employee_id and each.payslip_id.date_from:
#                 print (each.payslip_id.employee_id)
#                 print (each.payslip_id.date_from)

    @api.depends('payslip_id.employee_id','payslip_id.date_from','payslip_id.date_to')
    def _cal_total_absent(self):
        for each in self:
            each.total_absent=0
            if each.payslip_id.date_from and each.payslip_id.date_to and each.payslip_id.employee_id and each.work_entry_type_id.name=='Attendance':
                attendance_obj=self.env['hr.attendance'].search([('attendance_date','>=',each.payslip_id.date_from),('attendance_date','<=',each.payslip_id.date_to),('employee_id','=',each.payslip_id.employee_id.id),('status','=','Absent')])
                each.total_absent=len(attendance_obj)


class HRContract(models.Model):
    _inherit='hr.contract'


    def call_attendance_allowance(self, rule,contract, payslip):
        attendance_allowance = 0.0
        try:
            absent_rec=self.env['hr.attendance'].search([('attendance_date','>=',payslip.date_from),('attendance_date','<=',payslip.date_to),('employee_id','=',payslip.employee_id),('status','=','Absent')])
            leave_rec=self.env['hr.attendance'].search([('attendance_date','>=',payslip.date_from),('attendance_date','<=',payslip.date_to),('employee_id','=',payslip.employee_id),('status','=','On Leave')])
            att_count=self.env['hr.attendance'].search_count([('attendance_date','>=',payslip.date_from),('attendance_date','<=',payslip.date_to),('employee_id','=',payslip.employee_id)])
            no_of_days = (payslip.date_to - payslip.date_from).days + 1 
            if not absent_rec and not leave_rec  and att_count >= int(no_of_days):
                attendance_allowance= contract.attend_allowance
        except Exception as e:
            _logger.exception("Salary Rule Information: Attendance Allowance Rule (call_attendance_allowance), Rule Code %s Error Message: %s" % (rule, str(e)))
        return attendance_allowance
    
    def AttendanceAllowance(self, rule,contract, payslip):
        attendance_allowance = 0.0
        try:
            late_checkin_minutes = contract.checking_grace_period
            late_check_in_id = self.env['hr.attendance'].search([
                ('employee_id', '=', payslip.employee_id),
                ('attendance_date', '<=', payslip.date_to),
                ('attendance_date', '>=', payslip.date_from),
                ('status', '=', 'Present'), ])

            late_checkin = 0
            early_checkout = 0
            for x in late_check_in_id:
                if not self.env['hr.leave'].search(
                        [('employee_id', '=', contract.employee_id.id), ('date_from', '>=', x.attendance_date),
                         ('date_to', '<=', x.attendance_date), ('state', 'not in', ('cancel', 'draft'))]):
                    if x.late_check_in > int(late_checkin_minutes):
                        late_checkin += 1

            total_records = int(late_checkin)
            allow_late_checkin = contract.allow_late_checkin
            absent_rec = self.env['hr.attendance'].search(
                [('attendance_date', '>=', payslip.date_from), ('attendance_date', '<=', payslip.date_to),
                 ('employee_id', '=', payslip.employee_id), ('status', '=', 'Absent')])
            leave_rec = self.env['hr.attendance'].search(
                [('attendance_date', '>=', payslip.date_from), ('attendance_date', '<=', payslip.date_to),
                 ('employee_id', '=', payslip.employee_id), ('status', '=', 'On Leave')])
            att_count = self.env['hr.attendance'].search_count(
                [('attendance_date', '>=', payslip.date_from), ('attendance_date', '<=', payslip.date_to),
                 ('employee_id', '=', payslip.employee_id)])
            no_of_days = (payslip.date_to - payslip.date_from).days + 1
            if allow_late_checkin == 0:
                allow_late_checkin = 1

            deduct_leave = total_records // allow_late_checkin
            if not absent_rec and not leave_rec and att_count >= int(no_of_days) and deduct_leave < 1:
                attendance_allowance = contract.attend_allowance
        except Exception as e:
            _logger.exception(
                "Salary Rule Information: Attendance Allowance Rule (cal_labour_attendance_allowance), Rule Code %s Error Message: %s" % (
                rule, str(e)))
        return attendance_allowance


class AttAllowanceSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    labour_att_allowance = fields.Float(string="Attendance Allowance (Labour)",
                                    config_parameter='customize_payroll.labour_att_allowance',default=2000)
    management_att_allowance = fields.Float(string="Attendance Allowance (Management)",
                                  config_parameter='customize_payroll.management_att_allowance',default=3000)

    def set_values(self):
        res = super(AttAllowanceSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('labour_att_allowance', self.labour_att_allowance)
        self.env['ir.config_parameter'].sudo().set_param('management_att_allowance', self.management_att_allowance)
        return res

class HrPayslip(models.Model):
    _inherit='hr.payslip'

    def _get_period_id(self):
        month = date.today().month
        period = self.env['payslip.period'].search([('month_from', '=', month)], limit=1)
        return period

    total_loan = fields.Float('Total Loan',compute='cal_loan_amount',store=True)
    total_advance = fields.Float('Total Advance',compute='cal_loan_amount',store=True)
    
    recovered_amount=fields.Float('Recovered Amount',compute='cal_loan_amount',store=True)
    balance_amount=fields.Float('Balance Amount',compute='cal_loan_amount',store=True)
    
    total_overtime=fields.Float('Total Overtime',compute='cal_overtime')
    period_id = fields.Many2one('payslip.period', default=_get_period_id,string="Payslip Month")

    total_attendance = fields.Integer(string="Total Attendance")
    total_absent = fields.Integer(string="Absent")
    total_present = fields.Integer(string="Present")
    total_leave = fields.Integer(string="On Leave")
    total_half_day = fields.Integer(string="Half Day")
    total_holiday = fields.Integer(string="Holiday")
    total_public = fields.Integer(string="Public Holiday")
    total_late_checking = fields.Integer(string="Late Checkin")
    total_earlyout_absent = fields.Integer(string="Early Checkout Absent")
    unpaid_leaves = fields.Float(string="Unpaid Leaves")
    unapproved_half_day = fields.Integer(string="Unapproved Half Day")
    deducted_holiday = fields.Integer(string="Deducted Holiday")
    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        for rec in self:
            rec.contract_id = rec.employee_id.contract_id.id or False
            rec.struct_id = rec.contract_id.struct_id.id or False
            rec._calculate_attendance()
        return res
    
    def _get_attendance_status_count(self, status=False):
        if status:
            return self.env['hr.attendance'].search_count([
                ('employee_id','=',self.employee_id.id),
                ('attendance_date','>=',self.date_from),
                ('attendance_date','<=',self.date_to),
                ('status', '=', status)
                ])
        return self.env['hr.attendance'].search_count([
                ('employee_id','=',self.employee_id.id),
                ('attendance_date','>=',self.date_from),
                ('attendance_date','<=',self.date_to),
                ])

    def _calculate_attendance(self):
        syatem_param_early_checkout = self.env['ir.config_parameter'].sudo().search([('key','=','employee_late_check_in.early_check_out_before')]) or 0
        early_checkout_minutes=syatem_param_early_checkout.value
        syatem_param_late_checkin = self.env['ir.config_parameter'].sudo().search([('key','=','employee_late_check_in.late_check_in_after')]) or 0
        late_checkin_minutes=syatem_param_late_checkin.value
        for rec in self:
            
            
            contract = rec.contract_id
            late_check_in_id = self.env['hr.attendance'].search([
                                                                ('employee_id', '=', rec.employee_id.id),
                                                                ('attendance_date', '<=', rec.date_to),
                                                                ('attendance_date', '>=', rec.date_from),
                                                                ('status','=','Present'),], order='late_check_in asc')

            late_checkin_absent =0
            afer_grace_period =0
            early_checkout=0 
            allow_late_checkin = contract.allow_late_checkin
            late_checkin_minutes = contract.checking_late_count
            late_grace_period = contract.checking_grace_period
            late_checkin_mint = 0 
            
            early_checkout_minutes=contract.checkout_grace_period


            for x in late_check_in_id:
                if not self.env['hr.leave'].search([('employee_id','=',contract.employee_id.id),('date_from','>=',x.attendance_date),('date_to','<=',x.attendance_date),('state','not in',('cancel','draft'))]):
                    if x.late_check_in>int(late_grace_period):
                        afer_grace_period += 1
                    if x.late_check_in>int(late_checkin_minutes):
                        late_checkin_mint += x.late_check_in - int(late_checkin_minutes)
                    if x.early_check_out > int(early_checkout_minutes):
                        early_checkout += 1

            if allow_late_checkin == 0:
                allow_late_checkin = 1
            
            late_checking_absent=afer_grace_period// allow_late_checkin
            
            

            rec.total_attendance = rec._get_attendance_status_count()
            rec.total_absent = rec._get_attendance_status_count('Absent')
            rec.total_present = rec._get_attendance_status_count('Present')
            rec.total_leave = rec._get_attendance_status_count('On Leave')
            rec.total_half_day = rec._get_attendance_status_count('Half Day')
            rec.total_holiday = rec._get_attendance_status_count('Holiday')
            rec.total_public = rec._get_attendance_status_count('Public')
            rec.total_late_checking = late_checking_absent
            rec.total_earlyout_absent = early_checkout
            total_hrs=0.0
            leave_records = self.env['hr.leave'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('request_date_to', '<=', rec.date_to),
                ('request_date_from', '>=', rec.date_from),
                ('state', '=', 'validate'),
                ('holiday_status_id.name','=','Unpaid')
            ])
            for leave in leave_records:
                total_hrs+=leave.number_of_days
            rec.unpaid_leaves = total_hrs

            attendance_ids=self.env['hr.attendance'].search([
                ('employee_id','=',rec.employee_id.id),
                ('attendance_date','>=',rec.date_from),
                ('attendance_date','<=',rec.date_to),
                ('status','=','Half Day')])
            count=0
            for attendance in attendance_ids:
                # print(attendance_ids.attendance_date,'aff',self.env['hr.leave'].search([('date_from','>=',attendance.attendance_date),('date_to','<=',attendance.attendance_date),('state','not in',('cancel','draft'))]))
                if not rec.env['hr.leave'].search([('date_from','>=',attendance.attendance_date),('date_to','<=',attendance.attendance_date),('state','not in',('cancel','draft'))]):
                    count+=1
            rec.unapproved_half_day = count
            rec.deducted_holiday = rec.get_deducted_holiday()
    def action_view_attendance(self):
        action = []
        attendance = self.env['hr.attendance'].search([
            ('employee_id','=',self.employee_id.id),
            ('attendance_date','>=',self.date_from),
            ('attendance_date','<=',self.date_to)
            ]).ids
        
        action = {
            'domain': [('id', 'in', attendance )],
            'name': 'Attendance',
            'view_mode': 'tree,form',
            'res_model': 'hr.attendance',
            'context':{
                # 'search_default_group_by_status':1,
                'group_by':'status',
                'create':False,
                },
            'type': 'ir.actions.act_window',
        }
        return action

    def action_view_overtime(self):
        action = []
        overimt_obj = self.env['hr.overtime'].search([
                ('state','=','approved'),
                ('date_from','<=',self.date_to),
                ('date_from','>=',self.date_from),
                ('employee_id','=',self.employee_id.id)
            ]).ids
        
        action = {
            'domain': [('id', 'in', overimt_obj )],
            'name': 'Overtype',
            'view_mode': 'tree,form',
            'res_model': 'hr.overtime',
            'context':{
                # 'search_default_group_by_status':1,
                'group_by':'type',
                'create':False,
                },
            'type': 'ir.actions.act_window',
        }
        return action
    @api.depends('employee_id','date_from','date_to')
    def cal_overtime(self):
        for each in self:
            overimt_obj = self.env['hr.overtime'].search([
                ('state','=','approved'),
                ('date_from','<=',each.date_to),
                ('date_from','>=',each.date_from),
                ('employee_id','=',each.employee_id.id)
            ])
            overtime_time=0
            for rec in overimt_obj:
                overtime_time+=rec.days_no_tmp_1
            each.total_overtime=overtime_time

    @api.depends('employee_id')
    def cal_loan_amount(self):
        for each in self:
            loan_obj=self.env['hr.loan'].search([
                ('employee_id','=',each.employee_id.id),
                ('state','=','Approved'),
                ('loan_type.type','=','loan')
            ])
            advance_obj=self.env['hr.loan'].search([
                ('employee_id','=',each.employee_id.id),
                ('state','=','Approved'),
                ('loan_type.type','=','advance')
            ])
            each.total_loan =sum(loan_obj.mapped('net_amount'))
            each.total_advance = sum(loan_obj.mapped('balance_amount'))
            each.balance_amount = sum(loan_obj.mapped('balance_amount')) + sum(advance_obj.mapped('balance_amount'))
            each.recovered_amount =  each.total_loan + each.total_advance - each.balance_amount

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            rec.contract_id = rec.employee_id.contract_id.id 
    
    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        for rec in self:
            rec.struct_id = rec.contract_id.struct_id.id

    @api.onchange('period_id')
    def _onchange_period_id(self):
        for rec in self:
            if rec.state == 'draft' and rec.period_id:
                year = date.today().year
                date_from = date(year,int(rec.period_id.month_from),int(rec.period_id.day_from))
                rec.date_from = date_from
                if rec.period_id.month_to < rec.period_id.month_from:
                    year += 1
                date_to = date(year,int(rec.period_id.month_to),int(rec.period_id.day_to))
                rec.date_to = date_to 
                # fields.Date.to_string(date.today().replace(day=1))
                # date_to = fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())
    




    def get_deducted_holiday(self):
        for rec in self:
            date_from = rec.date_from
            if rec.contract_id.date_start > rec.date_from:
                date_from = rec.contract_id.date_start 
            present_records=self.env['hr.attendance'].search([
                ('employee_id','=',rec.employee_id.id),
                ('attendance_date','>=',date_from),
                ('attendance_date','<=',rec.date_to),
                ('status','in',['Present', 'Half Day', 'On Leave'])
                ])
            
            holiday_records_weekly = self.env['date.holiday'].search([
                ('date','>=',date_from),
                ('date','<=',rec.date_to),
                ('type','=','Weekly Holiday')
                ])
            holiday_records_public = self.env['date.holiday'].search([
                ('date','>=',date_from),
                ('date','<=',rec.date_to),
                ('type','=','Public Holiday')
                ])
            
            total_records=self.env['hr.attendance'].search([
                ('employee_id','=',rec.employee_id.id),
                ('attendance_date','>=', date_from),
                ('attendance_date','<=',rec.date_to),
                ('status','in',['Absent','Present', 'Half Day', 'On Leave'])
                ])
            
            absent_records=self.env['hr.attendance'].search([
                ('employee_id','=',rec.employee_id.id),
                ('attendance_date','>=',date_from),
                ('attendance_date','<=',rec.date_to),
                ('status','=','Absent')
                ])
            
            monthly_wage= rec.contract_id.wage
            
            no_of_days = 30.5
            diff = (rec.date_to - rec.date_from).days
            diff += 1
            
            if diff == 30:
                no_of_days = 30
            elif diff == 31:
                no_of_days = 31
            
            daily_wage=(rec.contract_id.wage)/no_of_days
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
            total_days = total_records + earned_holidays
            
            deduct_day = no_of_days - total_days

            return deduct_day
