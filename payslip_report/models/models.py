# -*- coding: utf-8 -*-
from num2words import num2words
from odoo import models, fields, api
from odoo.exceptions import UserError


class LoanClass(models.Model):
    _inherit = 'hr.loan'

    payslip_ids = fields.Many2many('hr.payslip')


class PayslipReport(models.Model):
    _inherit = 'hr.payslip'
    
    loan_ids = fields.Many2many('hr.loan', index=True)
    remaining_loan_amount = fields.Char()
    wage = fields.Monetary(related='contract_id.wage', string='Basic Salary')
    no_of_days = fields.Char(compute='_getDaysFromDates')
    int_to_word = fields.Char(compute='_get_amount_in_words')
    late_checkin_days = fields.Integer(compute='lateCheckinDays',store=True)
    late_checkin_days_2 = fields.Integer(compute='lateCheckinDays',store=True)

    def lateCheckinDays(self):
        for rec in self:
            early_checkout_minutes = int(self.env['ir.config_parameter'].sudo().get_param('early_check_out_before')) or 0
            # early_checkout_minutes=15
            # late_checkin_minutes=17
            late_checkin_minutes = int(self.env['ir.config_parameter'].sudo().get_param('late_check_in_after')) or 0
            late_check_in_id = self.env['hr.attendance'].search([
                                                                ('employee_id', '=', rec.employee_id.id),
                                                                ('attendance_date', '<=', rec.date_to),
                                                                ('attendance_date', '>=', rec.date_from),
                                                                ('status','=','Present'),])

            late_checkin=0 
            early_checkout=0 
            for x in late_check_in_id:
                if not self.env['hr.leave'].search([('employee_id','=',rec.employee_id.id),('date_from','>=',x.attendance_date),('date_to','<=',x.attendance_date),('state','not in',('cancel','draft'))]):
                    if x.late_check_in>late_checkin_minutes:
                        late_checkin+=1
                    if x.early_check_out > early_checkout_minutes:
                        early_checkout += 1
            # for x in early_check_out_id:
            #     if x.early_check_out>early_checkout_minutes:
            #         if not self.env['hr.leave'].search([('date_from','>=',x.attendance_date),('date_to','<=',x.attendance_date),('state','not in',('cancel','draft'))]):
            #             early_checkout+=1
            total_records=int(late_checkin)+int(early_checkout)
            deduct_leave=total_records//3
            rec.late_checkin_days=deduct_leave



    def _getDaysFromDates(self):
        d0 = self.date_from
        d1 = self.date_to
        delta = (d1 - d0)
        delta = delta.days
        self.no_of_days = delta+1

    def _get_amount_in_words(self):
        self.remain_amount = round(self.remain_amount)
        total = num2words(self.remain_amount).title()        
        if total:
            self.int_to_word = total
        else:
            self.int_to_word = 'Null'
