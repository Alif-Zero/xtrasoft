from odoo import api, fields, models, tools, _
from odoo.exceptions import except_orm, ValidationError
from bs4 import BeautifulSoup
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, safe_eval
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import logging
from calendar import monthrange
_logger = logging.getLogger(__name__)
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
import re

class HRContract(models.Model):
    _inherit = 'hr.contract'
    def execute_query(self, query):
        self.env.cr.execute(query)
        record = self.env.cr.fetchall()
        amount = 0.0
        ref = []
        if record and record[0]: 
            for r in record:
                amount += float(r[0])
                ref.append(int(r[1]))
            
        return amount, ref
    
    def calc_overtime_allowance(self, rule, contract, payslip):
        ot_allowance = 0.0
        try:
            ot_records = self.env['hr.overtime'].search([('employee_id', '=', payslip.employee_id),
                                                             ('date_to', '<=', payslip.date_to),
                                                             ('date_from', '>=', payslip.date_from),
                                                             ('state', '=', 'approved'),
                                                             ('type','=','cash')
                                                             ])
            for ot in ot_records:
                ot_allowance+=ot.cash_hrs_amount
        except Exception as e:
            _logger.exception("Salary Rule Information: Allowance of Overtime Rule (calc_overtime_allowance), Rule Code %s Error Message: %s" % (rule, str(e)))
        return ot_allowance
    
    def calc_recover_advance_salary(self, rule, contract, payslip):
        deduction = 0.0
        try:
            date_from = payslip.date_from
            date_to = payslip.date_to
            joining_date = contract.date_start
            month, year, work_days, month_days = self._cal_date(date_from, date_to, joining_date)
            table = 'hr_loan_line'
            ref = 0
            query = """
            SELECT amount,id
            FROM   %s 
            WHERE  year = '%s' 
                   AND month = '%s' 
                   AND state = 'Balance' 
                   AND loan_type in ('Advance Salary')
                   
                   AND case_state = 'Approved'
                   AND employee_id = %s             
            """ % (table, year, str(month).zfill(2), contract.employee_id.id)
            deduction, ref = self.execute_query(query)
            if deduction and ref:
                if len(ref) == 1:
                    self.env.cr.execute("""update hr_loan_line set payslip_id ="""+str(payslip.id)+""" where id ="""+str(ref[0]))
                elif len(ref) > 1:
                    self.env.cr.execute("""update hr_loan_line set payslip_id ="""+str(payslip.id)+""" where id ="""+tuple(ref))
        except Exception as e:
            _logger.exception("Salary Rule Information: Recov of Advance Salary Deduction Rule (calc_recover_advance_salary), Rule Code %s Error Message: %s" % (rule, str(e)))
        return deduction
    
    def calc_recover_personal_loan(self, rule, contract, payslip):
        deduction = 0.0
        try:
            date_from = payslip.date_from
            date_to = payslip.date_to
            joining_date = contract.date_start
            month, year, work_days, month_days = self._cal_date(date_from, date_to, joining_date)
            table = 'hr_loan_line'
            ref = 0
            query = """
            SELECT amount,id
            FROM   %s 
            WHERE  year = '%s' 
                   AND month = '%s' 
                   AND state = 'Balance' 
                   AND loan_type in ('Personal Loan')
                   AND case_state = 'Approved'
                   AND employee_id = %s             
            """ % (table, year, str(month).zfill(2), contract.employee_id.id)
            deduction, ref = self.execute_query(query)
            if deduction and ref:
                if len(ref) == 1:
                    self.env.cr.execute("""update hr_loan_line set payslip_id ="""+str(payslip.id)+""" where id ="""+str(ref[0]))
                elif len(ref) > 1:
                    self.env.cr.execute("""update hr_loan_line set payslip_id ="""+str(payslip.id)+""" where id in """+tuple(ref))
        except Exception as e:
            _logger.exception("Salary Rule Information: Recov of Advance Salary Deduction Rule (calc_recover_personal_loan), Rule Code %s Error Message: %s" % (rule, str(e)))
        return deduction
    
    def _cal_date(self, date_from, date_to, joining_date):
        month = date_to.month
        year = date_from.year
        work_days = 0
        work_days_from_joining = date_to - joining_date
        work_days_from_payslip = date_to - date_from
        if work_days_from_joining.days < work_days_from_payslip.days:
            work_days = work_days_from_joining.days + 1
        else:
            work_days = work_days_from_payslip.days + 1
        month_days = monthrange(year, month)[1]
        return month, year, float(work_days), float(month_days)