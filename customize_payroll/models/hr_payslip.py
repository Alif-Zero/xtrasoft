# -*- coding: utf-8 -*-

from odoo import models, api, fields
import logging
_logger = logging.getLogger(__name__)

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
    
    def cal_labour_allowance(self, rule,contract, payslip):
        attendance_allowance = 0.0
        try:
            att_allowance = float(self.env['ir.config_parameter'].sudo().get_param('labour_att_allowance'))
            absent_rec=self.env['hr.attendance'].search([('attendance_date','>=',payslip.date_from),('attendance_date','<=',payslip.date_to),('employee_id','=',payslip.employee_id),('status','=','Absent')])
            leave_rec=self.env['hr.attendance'].search([('attendance_date','>=',payslip.date_from),('attendance_date','<=',payslip.date_to),('employee_id','=',payslip.employee_id),('status','=','On Leave')])
            att_count=self.env['hr.attendance'].search_count([('attendance_date','>=',payslip.date_from),('attendance_date','<=',payslip.date_to),('employee_id','=',payslip.employee_id)])
            no_of_days = (payslip.date_to - payslip.date_from).days + 1 
            if not absent_rec and not leave_rec  and att_count >= int(no_of_days):
                attendance_allowance=att_allowance
        except Exception as e:
            _logger.exception("Salary Rule Information: Attendance Allowance Rule (cal_labour_attendance_allowance), Rule Code %s Error Message: %s" % (rule, str(e)))
        return attendance_allowance
    
    def cal_management_allowance(self, rule,contract, payslip):
        attendance_allowance = 0.0
        try:
            att_allowance = float(self.env['ir.config_parameter'].sudo().get_param('management_att_allowance'))
            absent_rec=self.env['hr.attendance'].search([('attendance_date','>=',payslip.date_from),('attendance_date','<=',payslip.date_to),('employee_id','=',payslip.employee_id),('status','=','Absent')])
            leave_rec=self.env['hr.attendance'].search([('attendance_date','>=',payslip.date_from),('attendance_date','<=',payslip.date_to),('employee_id','=',payslip.employee_id),('status','=','On Leave')])
            att_count=self.env['hr.attendance'].search_count([('attendance_date','>=',payslip.date_from),('attendance_date','<=',payslip.date_to),('employee_id','=',payslip.employee_id)])
            no_of_days = (payslip.date_to - payslip.date_from).days + 1 
            if not absent_rec and not leave_rec  and att_count >= int(no_of_days):
                attendance_allowance=att_allowance
        except Exception as e:
            _logger.exception("Salary Rule Information: Attendance Allowance Rule (cal_labour_attendance_allowance), Rule Code %s Error Message: %s" % (rule, str(e)))
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
    total_loan=fields.Float('Total Loan',compute='cal_loan_amount',store=True)
    recovered_amount=fields.Float('Recovered Amount',compute='cal_loan_amount',store=True)
    balance_amount=fields.Float('Balance Amount',compute='cal_loan_amount',store=True)
    total_overtime=fields.Float('Total Overtime',compute='cal_overtime')
    
    @api.depends('employee_id','date_from','date_to')
    def cal_overtime(self):
        for each in self:
            overimt_obj=self.env['hr.overtime'].search([('state','=','approved'),('date_from','<=',each.date_to),('date_from','>=',each.date_from),('employee_id','=',each.employee_id.id)])
            overtime_time=0
            for rec in overimt_obj:
                overtime_time+=rec.days_no_tmp_1
            each.total_overtime=overtime_time
    @api.depends('employee_id')
    def cal_loan_amount(self):
        for each in self:
            loan_obj=self.env['hr.loan'].search([('employee_id','=',each.employee_id.id),('state','=','Approved'),('loan_type.name','=','Personal Loan')])
            if loan_obj:
                each.total_loan=sum(loan_obj.mapped('net_amount'))
                each.recovered_amount=sum(loan_obj.mapped('net_amount')) - sum(loan_obj.mapped('balance_amount'))
                each.balance_amount=sum(loan_obj.mapped('balance_amount'))
            else:
                each.total_loan=0
                each.recovered_amount=0
                each.balance_amount=0