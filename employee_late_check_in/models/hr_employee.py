# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class AttendanceExemption(models.Model):
    _name='hr.attendance.exemption'
    employee_id=fields.Many2one('hr.employee','Employee',required=True)
    job_id=fields.Many2one('hr.job','Designation',compute='get_employee_details',store=True)
    department_id=fields.Many2one('hr.department','Department',compute='get_employee_details',store=True)
    
    @api.depends('employee_id')
    def get_employee_details(self):
        for each in self:
            if each.employee_id:
                contract_obj=self.env['hr.contract'].search([('employee_id','=',each.employee_id.id),('state','=','open')],limit=1)
                if contract_obj:
                    each.job_id=contract_obj.job_id.id
                    each.department_id=contract_obj.department_id.id
                else:
                    each.job_id=None
                    each.department_id=None
            else:
                each.job_id=None
                each.department_id=None
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    late_check_in_count = fields.Integer(string="Late Check-In", compute="get_late_check_in_count")

    def action_to_open_late_check_in_records(self):
        domain = [
            ('employee_id', '=', self.id),
        ]
        return {
            'name': _('Employee Late Check-in'),
            'domain': domain,
            'res_model': 'late.check_in',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'limit': 80,
        }

    def get_late_check_in_count(self):
        self.late_check_in_count = self.env['late.check_in'].search_count([('employee_id', '=', self.id)])


class HrEmployees(models.Model):
    _inherit = 'hr.employee.public'

    late_check_in_count = fields.Integer(string="Late Check-In", compute="get_late_check_in_count")

    def action_to_open_late_check_in_records(self):
        domain = [
            ('employee_id', '=', self.id),
        ]
        return {
            'name': _('Employee Late Check-in'),
            'domain': domain,
            'res_model': 'late.check_in',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'limit': 80,
        }

    def get_late_check_in_count(self):
        self.late_check_in_count = self.env['late.check_in'].search_count([('employee_id', '=', self.id)])
class HrContract(models.Model):
    _inherit='hr.contract'
    
    def calc_late_checkin_deduction(self,category, rule, contract, payslip):
        deduction = 0.0
        syatem_param_early_checkout = self.env['ir.config_parameter'].sudo().search([('key','=','employee_late_check_in.early_check_out_before')]) or 0
        early_checkout_minutes=syatem_param_early_checkout.value
        syatem_param_late_checkin = self.env['ir.config_parameter'].sudo().search([('key','=','employee_late_check_in.late_check_in_after')]) or 0
        late_checkin_minutes=syatem_param_late_checkin.value
        try:
            late_check_in_id = self.env['hr.attendance'].search([
                                                                ('employee_id', '=', payslip.employee_id),
                                                                ('attendance_date', '<=', payslip.date_to),
                                                                ('attendance_date', '>=', payslip.date_from),
                                                                ('status','=','Present'),])
            early_check_out_id = self.env['hr.attendance'].search([('employee_id', '=', payslip.employee_id),
                                                             ('attendance_date', '<=', payslip.date_to),
                                                             ('attendance_date', '>=', payslip.date_from),
                                                            ('status','=','Present'),
                                                             
                                                          ])
            late_checkin=0 
            early_checkout=0 
            for x in late_check_in_id:
                if not self.env['hr.leave'].search([('employee_id','=',contract.employee_id.id),('date_from','>=',x.attendance_date),('date_to','<=',x.attendance_date),('state','not in',('cancel','draft'))]):
                    if x.late_check_in>int(late_checkin_minutes):
                        late_checkin+=1
                    if x.early_check_out > int(early_checkout_minutes):
                        early_checkout += 1
            # for x in early_check_out_id:
            #     if x.early_check_out>early_checkout_minutes:
            #         if not self.env['hr.leave'].search([('date_from','>=',x.attendance_date),('date_to','<=',x.attendance_date),('state','not in',('cancel','draft'))]):
            #             early_checkout+=1
            total_records=int(late_checkin)+int(early_checkout)
            allow_late_checkin = contract.allow_late_checkin
            if allow_late_checkin == 0:
                allow_late_checkin = 1
            deduct_leave=total_records// allow_late_checkin
            
            no_of_days = 30.5
            diff = (payslip.date_to - payslip.date_from).days
            diff += 1
            
            if diff == 30:
                no_of_days = 30
            elif diff == 31:
                no_of_days = 31

            if deduct_leave != 0:
                deduction=(contract.wage/no_of_days)*deduct_leave
        except Exception as e:
            _logger.exception("Salary Rule Information: Deduction of Late Chaeckin and Early checkout Rule (calc_late_checkin_deduction), Rule Code %s Error Message: %s" % (rule, str(e)))
        return deduction
    
#     def calc_early_checkout_deduction(self, rule, contract, payslip):
#         deduction = 0.0
#         try:
#             early_check_out_id = self.env['early.check_out'].search([('employee_id', '=', payslip.employee_id),
#                                                              ('date', '<=', payslip.date_to),
#                                                              ('date', '>=', payslip.date_from),
#                                                              ('state', '=', 'approved'),
#                                                              ])
#             deduct_leave=len(early_check_out_id)//3
#             if deduct_leave >=1:
#                 deduction=(self.wage/31)*deduct_leave
#         except Exception as e:
#             _logger.exception("Salary Rule Information: Deduction of Early Chaeckout Rule (calc_early_checkout_deduction), Rule Code %s Error Message: %s" % (rule, str(e)))
#         return deduction

    def LateCheckinAbsent(self,category, rule, contract, payslip):
        deduction = 0.0
        late_checkin_minutes = contract.checking_grace_period
        try:
            late_check_in_id = self.env['hr.attendance'].search([
                                                                ('employee_id', '=', payslip.employee_id),
                                                                ('attendance_date', '<=', payslip.date_to),
                                                                ('attendance_date', '>=', payslip.date_from),
                                                                ('status','=','Present'),])

            late_checkin=0 
            early_checkout=0 
            for x in late_check_in_id:
                if not self.env['hr.leave'].search([('employee_id','=',contract.employee_id.id),('date_from','>=',x.attendance_date),('date_to','<=',x.attendance_date),('state','not in',('cancel','draft'))]):
                    if x.late_check_in>int(late_checkin_minutes):
                        late_checkin+=1
            
            total_records=int(late_checkin)
            allow_late_checkin = contract.allow_late_checkin
            if allow_late_checkin == 0:
                allow_late_checkin = 1
            
            deduct_leave=total_records// allow_late_checkin
            
            no_of_days = 30.5
            diff = (payslip.date_to - payslip.date_from).days
            diff += 1
            
            if diff == 30:
                no_of_days = 30
            elif diff == 31:
                no_of_days = 31

            if deduct_leave != 0:
                deduction=(contract.wage/no_of_days)*deduct_leave
        except Exception as e:
            _logger.exception("Salary Rule Information: Deduction of Late Chaeckin and Early checkout Rule (calc_late_checkin_deduction), Rule Code %s Error Message: %s" % (rule, str(e)))
        return deduction
    
    def LateCheckinDeduction(self,category, rule, contract, payslip):
        deduction = 0.0
        late_checkin_minutes=contract.checking_late_count
        try:
            late_check_in_id = self.env['hr.attendance'].search([
                                                                ('employee_id', '=', payslip.employee_id),
                                                                ('attendance_date', '<=', payslip.date_to),
                                                                ('attendance_date', '>=', payslip.date_from),
                                                                ('status','=','Present'),], order='late_check_in asc')

            late_checkin=0 
            late_count=0
            limit = contract.allow_late_checkin - 1

            for x in late_check_in_id:
                if not self.env['hr.leave'].search([('employee_id','=',contract.employee_id.id),('date_from','>=',x.attendance_date),('date_to','<=',x.attendance_date),('state','not in',('cancel','draft'))]):
                    if x.late_check_in>int(late_checkin_minutes):
                        late_checkin += x.late_check_in - int(late_checkin_minutes)
                    #     late_count += 1 
                    # if late_count == limit and limit != 0:
                    #     break
            if late_checkin != 0:
                deduction=(contract.over_hour/60)*late_checkin
        except Exception as e:
            _logger.exception("Salary Rule Information: Deduction of Late Chaeckin and Early checkout Rule (calc_late_checkin_deduction), Rule Code %s Error Message: %s" % (rule, str(e)))
        return deduction

    def EarlyCheckoutAbsent(self, category, rule, contract, payslip):
        deduction = 0.0
        early_checkout_minutes = contract.checkout_grace_period
        try:
            late_check_in_id = self.env['hr.attendance'].search([
                ('employee_id', '=', payslip.employee_id),
                ('attendance_date', '<=', payslip.date_to),
                ('attendance_date', '>=', payslip.date_from),

                ('status', '=', 'Present'), ])

            late_checkin = 0
            early_checkout = 0
            for x in late_check_in_id:
                ot_records = self.env['hr.overtime'].search([('employee_id', '=', contract.employee_id.id),
                                                             ('date_to', '<=', x.attendance_date),
                                                             ('date_from', '>=', x.attendance_date),
                                                             ('state', '=', 'approved'),
                                                             ('type', '=', 'cash')
                                                             ])
                if ot_records:
                    print('-------')
                    continue
                if not self.env['hr.leave'].search(
                        [('employee_id', '=', contract.employee_id.id), ('date_from', '>=', x.attendance_date),
                         ('date_to', '<=', x.attendance_date), ('state', 'not in', ('cancel', 'draft'))]):
                    if x.early_check_out > int(early_checkout_minutes):
                        early_checkout += 1

            total_records = int(early_checkout)
            allow_early_checkout = contract.allow_early_checkout
            if allow_early_checkout == 0:
                allow_early_checkout = 1
            deduct_leave = total_records // allow_early_checkout

            no_of_days = 30.5
            diff = (payslip.date_to - payslip.date_from).days
            diff += 1

            if diff == 30:
                no_of_days = 30
            elif diff == 31:
                no_of_days = 31

            if deduct_leave != 0:
                deduction = (contract.wage / no_of_days) * deduct_leave
        except Exception as e:
            _logger.exception(
                "Salary Rule Information: Deduction of Late Chaeckin and Early checkout Rule (calc_late_checkin_deduction), Rule Code %s Error Message: %s" % (
                rule, str(e)))
        return deduction

    def EarlyCheckoutDeduction(self, category, rule, contract, payslip):
        deduction = 0.0
        early_checkout_minutes = contract.early_checkout_count

        try:
            late_check_in_id = self.env['hr.attendance'].search([
                ('employee_id', '=', payslip.employee_id),
                ('attendance_date', '<=', payslip.date_to),
                ('attendance_date', '>=', payslip.date_from),
                ('status', '=', 'Present'), ], order='early_check_out asc')

            late_checkin = 0
            early_checkout = 0
            limit = contract.allow_early_checkout - 1
            deduct_leave = 0
            for x in late_check_in_id:
                ot_records = self.env['hr.overtime'].search([('employee_id', '=', contract.employee_id.id),
                                                             ('date_to', '<=', x.attendance_date),
                                                             ('date_from', '>=', x.attendance_date),
                                                             ('state', '=', 'approved'),
                                                             ('type', '=', 'cash')
                                                             ])
                if ot_records:
                    continue
                if x.early_check_out > int(early_checkout_minutes):
                    if self.env['hr.leave'].search(
                            [('employee_id', '=', contract.employee_id.id), ('date_from', '>=', x.attendance_date),
                             ('date_to', '<=', x.attendance_date), ('state', 'not in', ('cancel', 'draft'))]):
                        early_checkout += x.early_check_out - int(early_checkout_minutes)
                        # if early_checkout == limit and limit != 0:
                        #     break
                    else:
                        deduct_leave += 1

            if early_checkout != 0:
                deduction = (contract.over_hour / 60) * early_checkout
            no_of_days = 30.5
            # diff = (payslip.date_to - payslip.date_from).days
            # diff += 1
            # if diff == 30:
            #         no_of_days = 30
            # elif diff == 31:
            #     no_of_days = 31

            # if deduct_leave != 0:
            #     deduction +=(contract.wage/no_of_days)*deduct_leave

        except Exception as e:
            _logger.exception(
                "Salary Rule Information: Deduction of Late Chaeckin and Early checkout Rule (calc_late_checkin_deduction), Rule Code %s Error Message: %s" % (
                rule, str(e)))
        return deduction