from openerp import models, fields, api
from openerp.exceptions import except_orm
from openerp.exceptions import ValidationError
from openerp.tools.translate import _
import time
from datetime import datetime, timedelta, date
import calendar
import logging
from openerp import tools
from _weakref import ref
from openerp.tools.safe_eval import safe_eval as eval
import copy
_logger = logging.getLogger(__name__)
import openerp
import openerp.release
import openerp.sql_db
import openerp.tools
import threading
from odoo.tools import float_compare, float_is_zero
from psycopg2 import sql


months = {'1':'Jan', '2':'Feb', '3':'Mar', '4':'Apr', '5':'May', '6':'Jun', '7':'Jul', '8':'Aug', '9':'Sep', '10':'Oct', '11':'Nov', '12':'Dec', }
months_index = {'Jan':'1', 'Feb':'2', 'Mar':'3', 'Apr':'4', 'May':'5', 'Jun':'6', 'Jul':'7', 'Aug':'8', 'Sep':'9', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
YearsList = [('2020','2019-20'),('2021','2020-21'),('2022','2021-22'),('2023','2022-23'),('2024','2023-24'),('2025','2024-25'),('2026','2025-26'),('2027','2026-27'),('2028','2027-28'),('2029','2028-29'),('2030','2029-30'),('2031','2030-31')
                             ,('2032','2031-32'),('2033','2032-33'),('2034','2033-34'),('2035','2034-35'),('2036','2035-36'),('2037','2036-37'),('2038','2037-38'),('2039','2038-39'),('2040','2039-40'),('2041','2040-41')
                             ,('2042','2041-42'),('2043','2042-43'),('2044','2043-44'),('2045','2044-45'),('2046','2045-46'),('2047','2046-47'),('2048','2047-48'),('2049','2048-49'),('2050','2049-50')]

class HRSalaryRuleType(models.Model):
    _name = 'hr.salary.rule.type'
    name = fields.Char(string="Rule Type", required=True)
    category_id = fields.Many2one('hr.salary.rule.category', string="Category")
    code = fields.Char(string="Technical Code")
    is_computation = fields.Boolean(string="Allowance Computation")
    misc_adjustment = fields.Boolean(string="Show in Salary Adjustment", default=False)
    misc_adjustment_attr = fields.Boolean(string="Misc Adjustment Attr", default=False,compute='_get_attr')
    is_recovery_advances = fields.Boolean(string="is Recovery of the Advances", default=False)
    category_name = fields.Char(related="category_id.name")
    
    def write(self, vals):
        code = vals.get('code',False)
        name = vals.get('name',False)
        if code or name:
            rule = self.env['hr.salary.rule'].search([('rule_type_id','=',self.id)])
            for r in rule:
                dic = {}
                if code:
                    dic.update({'code':code})
                if name:
                    dic.update({'name':'%s'%(name)})
                r.write(dic)
        super(HRSalaryRuleType,self).write(vals)
        
    
    def _get_attr(self):
        if self.category_id.name not in ['Allowance','Deduction']:
            self.misc_adjustment_attr = True
        else:
            self.misc_adjustment_attr = False
    
    _sql_constraints = [
        ('value_code', 'unique (code)', 'Code value for this rule already exists !'),
        ('value_name', 'unique (name)', 'This rule already exists !')
    ]



 
class salary_contribution_register(models.Model):
    """(NULL)"""
    _name = 'salary.contribution.register'
    _description = 'Salary Contributioni Register'
     
     
    def confirm_record(self):        
        x = self
        x.write(
            dict(
                xstate = 'Confirmed',
                confirmed_date = fields.Datetime.context_timestamp(self, datetime.now()),
                confirmed_by = self.env.user.id,
                )
            )
             
     
     
    @api.depends('contract_id')
    def _calc_value(self):
        contract = self.contract_id
        if contract:
            self.job_id = contract.job_id.id
            self.department_id = contract.department_id.id
            self.cnic = contract.employee_id.identification_id
            self.company_id = contract.company_id.id
     
     
    @api.depends('employee_id')
    def _get_contract(self):
        if self.employee_id:
            for x in self.employee_id.contract_ids:
                if x.state == 'Confirmed':
                    self.contract_id = x.id
                 
     
    @api.depends('rule_id')
    def _get_code(self):
        if self.rule_id:
            self.code = self.rule_id.code
             
     
    @api.onchange('employee_id')
    def onchange_employee(self):
        self._get_contract()
     
     
    @api.onchange('contract_id')
    def onchange_contract(self):
        if self.contract_id:
            self._calc_value()
     
     
     
    def unlink(self):
        for each in self:
            if each.payslip_id:
                raise ValidationError("You can not delete the record which consist payslip reference, please delete the payslip %s"%(each.payslip_id.number))
            if each.state != 'Draft':
                raise ValidationError('Cannot delete record which is not in draft state')
         
        return super(salary_contribution_register, self).unlink()
     
     
    @api.depends('rule_id')
    def _get_rule_type(self):
        if self.rule_id:
            self.rule_type_id = self.rule_id.rule_type_id.id
     
             
    name = fields.Char(string="Narration")
    rule_id = fields.Many2one('hr.salary.rule', string="Salary Rule")
    rule_type_id = fields.Many2one('hr.salary.rule.type', string="Salary Rule Type", compute=_get_rule_type, store=True)
    code = fields.Char(string="Code", compute=_get_code)
    employee_id = fields.Many2one('hr.employee', string="Employee")
     
    contract_id = fields.Many2one('hr.contract', string="Contract", compute=_get_contract, store=True)
    job_id = fields.Many2one('hr.job', string="Designation", compute=_calc_value, store=True)
    department_id = fields.Many2one('hr.department', string="Department", compute=_calc_value, store=True)
    cnic = fields.Char(string='CNIC', compute=_calc_value, store=True)
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    company_id = fields.Many2one('res.company', string="Campus", store=True,compute=_calc_value)
    state = fields.Selection([('Draft','Draft'),('Confirmed','Confirmed')], default='Draft')
    confirmed_by = fields.Many2one('res.users', string="Confirmed By")
    confirmed_date = fields.Datetime(string="Confirmed Date")
    year = fields.Selection(YearsList, string="Year", type="Integer", required=True)
                              
    month = fields.Selection([('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June')], string='Month', required=True, type="Integer")
    workdays = fields.Integer(string="Workdays")
     
     
    @api.depends('year','month')
    def _calc_date(self):
        if self.year and self.month:
            mnth = self.month
            year = self.year
            if mnth in [7,8,9,10,11,12]:
                year =  self.year - 1
             
            if int(mnth) < 10:
                mnth = '0%s'%(mnth)
             
            self.date = '%d-%s-01'%(int(year), mnth)
    date = fields.Date(string="Date", compute=_calc_date, store=True)
    amount = fields.Integer(string="Amount")


class HRSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    
    @api.onchange('rule_type_id')
    def onchange_rule_type(self):
        if self.rule_type_id:
            self.name = self.rule_type_id.name
            self.code = self.rule_type_id.code
            self.reporting_code = self.rule_type_id.code
    
    @api.depends('rule_type_id')
    def _get_tech_code(self):
        for each in self:
            if self.rule_type_id:
                self.tech_code = self.rule_type_id.code
            else:
                self.tech_code=None
        
    rule_type_id = fields.Many2one('hr.salary.rule.type', string="Rule Type")
    tech_code = fields.Char(string="Technical Code", compute=_get_tech_code)
    reporting_code = fields.Char(string="Code for Display")

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for payslip in self:
            installment = self.env['hr.loan.line'].search([('payslip_id', '=', payslip.id)])
            for each in installment:
                if each.state == 'Balance':
                    each.state = 'Deducted'
                    if not each.ref:
                        each.ref = payslip.name
            if not payslip.move_id:
                raise ValidationError('Please configure the accounts, if there is batch reference than create draft entries from batch')
            else:
                if payslip.payslip_run_id:
                    payslip.move_id.ref = payslip.payslip_run_id.name
                else:
                    payslip.move_id.ref = "%s - %s"%(payslip.number, payslip.name)
                payslip.move_id.line_ids.write({'partner_id':payslip.employee_id.address_home_id.id or False, 'payslip_id':payslip.id})
        return res
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""", track_visibility='onchange')
    total_amount = fields.Float(string='Total Amount', compute='compute_total_amount', store=True)
    move_ids = fields.One2many('account.move.line','payslip_id', string="Move Lines")
    paid_amount = fields.Float(string="Paid Amount", compute="compute_paid_amount", store=True)
    remain_amount = fields.Float(string="Remain Amount", compute="compute_paid_amount", store=True)
    payable_amount = fields.Float(string="Payable Amount", compute="compute_paid_amount", store=True)

    def calc_amt(self):
        for x in self:
            x.compute_paid_amount()

    @api.depends('move_ids','line_ids')
    def compute_paid_amount(self):
        for slip in self:
            payable_amount = 0.0
            paid_amount = 0.0
            remain_amount = 0.0
            if not slip.move_ids:
                for line in slip.line_ids:
                    if line.salary_rule_id.code == 'NET':
                        payable_amount += line.total
            else:
                for m in slip.move_ids:
                    if m.account_id.internal_type == 'payable':
                        payable_amount += m.credit
                        paid_amount += m.debit
                        

            remain_amount = payable_amount - paid_amount
            slip.payable_amount = payable_amount
            slip.remain_amount = remain_amount
            slip.paid_amount = paid_amount    

                     
                    



    @api.depends('line_ids','move_ids')
    @api.onchange('line_ids','move_ids')
    def compute_total_amount(self):
        for slip in self:
            total_amount_new = 0.0
            if not slip.move_ids:
                for line in slip.line_ids:
                    if line.salary_rule_id.code == 'NET':
                        total_amount_new+=line.total
            else:
                credit = 0.0
                debit = 0.0
                for m in slip.move_ids:
                    if m.account_id.internal_type == 'payable':
                        credit += m.credit
                        debit += m.debit
                total_amount_new = credit - debit
            slip.total_amount = total_amount_new


    def set_to_paid(self):
        self.write({'state': 'paid'})

class HRPayslipREportWizard(models.TransientModel):
    _name = 'hr.payslip.report.wizard'
    _description = 'Payslip Report Wizard'
    department_id=fields.Many2one('hr.department','Department')
    struct_id = fields.Many2many('hr.payroll.structure', string="Salary Structure")
    rule_ids = fields.Many2one(
        string='Salary Rules',
        comodel_name='hr.salary.rule',
    )

    employee_ids = fields.Many2many(
        string='Employee',
        comodel_name='hr.employee',
    )

    def _get_date_from(self):
        return datetime(fields.Datetime.now().year, fields.Datetime.now().month, 1)
    
    def _get_date_to(self):
        return datetime(fields.Datetime.now().year, fields.Datetime.now().month, calendar.monthrange(fields.Datetime.now().year, fields.Datetime.now().month)[1])
        
    date_from = fields.Date(string="Date From", default=_get_date_from)
    date_to = fields.Date(string="Date To", default=_get_date_to)

    payslip_run_id = fields.Many2one(
        string='Payslip Batch',
        comodel_name='hr.payslip.run',
    )
    
    def print_report(self):
        self.ensure_one()
        return {
            'name': 'Salary Report',
            'type': 'ir.actions.act_url',
            'url': '/salaryReport/%(res_id)s' % {'res_id': self.id},
        }
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payslip_id = fields.Many2one('hr.payslip', string='Expense', copy=False, help="Expense where the move line come from")

class HrPayrollReport(models.Model):
    _name = "hr.payslip.report"
    _description = "Payroll Analysis Report"
    _auto = False
    _rec_name = 'date_from'
    _order = 'salary_rule desc'


    date_from = fields.Date('Start Date', readonly=True)
    date_to = fields.Date('End Date', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True)
    department_id = fields.Many2one('hr.department', 'Department', readonly=True)
    job_id = fields.Many2one('hr.job', 'Job Position', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    salary_rule=fields.Char('Salary Rule')
    amount=fields.Float('Amount')

    def init(self):
        query = """
            SELECT
                row_number() OVER (PARTITION BY true) AS id,
                p.date_from as date_from,
                p.date_to as date_to,
                e.id as employee_id,
                e.department_id as department_id,
                c.job_id as job_id,
                e.company_id as company_id,
                pl.name as salary_rule,
                pl.total as amount
            FROM
                hr_payslip p inner join hr_payslip_line pl on
                p.id=pl.slip_id inner join hr_employee e on e.id=p.employee_id
                inner join hr_contract c on c.id=p.contract_id
            order by
                pl.name desc
            """
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(sql.SQL("CREATE or REPLACE VIEW {} as ({})").format(sql.Identifier(self._table), sql.SQL(query)))


# class HrPayrollReport(models.Model):
#     _inherit = "hr.payroll.report"
#     _order = 'date_from desc, salary_rule desc'

#     salary_rule=fields.Char('Salary Rule')
    
#     def init(self):
#         query = """
#             SELECT
#                 p.id as id,
#                 CASE WHEN wd.id = min_id.min_line THEN 1 ELSE 0 END as count,
#                 CASE WHEN wet.is_leave THEN 0 ELSE wd.number_of_days END as count_work,
#                 CASE WHEN wet.is_leave THEN 0 ELSE wd.number_of_hours END as count_work_hours,
#                 CASE WHEN wet.is_leave and wd.amount <> 0 THEN wd.number_of_days ELSE 0 END as count_leave,
#                 CASE WHEN wet.is_leave and wd.amount = 0 THEN wd.number_of_days ELSE 0 END as count_leave_unpaid,
#                 CASE WHEN wet.is_unforeseen THEN wd.number_of_days ELSE 0 END as count_unforeseen_absence,
#                 CASE WHEN wet.is_leave THEN wd.amount ELSE 0 END as leave_basic_wage,
#                 p.name as name,
#                 p.date_from as date_from,
#                 p.date_to as date_to,
#                 e.id as employee_id,
#                 e.department_id as department_id,
#                 c.job_id as job_id,
#                 e.company_id as company_id,
#                 wet.id as work_code,
#                 CASE WHEN wet.is_leave IS NOT TRUE THEN '1' WHEN wd.amount = 0 THEN '3' ELSE '2' END as work_type,
#                 wd.number_of_days as number_of_days,
#                 wd.number_of_hours as number_of_hours,
#                 CASE WHEN wd.id = min_id.min_line THEN pln.total ELSE 0 END as net_wage,
#                 CASE WHEN wd.id = min_id.min_line THEN plb.total ELSE 0 END as basic_wage,
#                 CASE WHEN wd.id = min_id.min_line THEN plg.total ELSE 0 END as gross_wage,
#                 pln.name as salary_rule
#             FROM
#                 (SELECT * FROM hr_payslip WHERE state IN ('done', 'paid')) p
#                     left join hr_employee e on (p.employee_id = e.id)
#                     left join hr_payslip_worked_days wd on (wd.payslip_id = p.id)
#                     left join hr_work_entry_type wet on (wet.id = wd.work_entry_type_id)
#                     left join (select payslip_id, min(id) as min_line from hr_payslip_worked_days group by payslip_id) min_id on (min_id.payslip_id = p.id)
#                     left join hr_payslip_line pln on (pln.slip_id = p.id and  pln.code = 'NET')
#                     left join hr_payslip_line plb on (plb.slip_id = p.id and plb.code = 'BASIC')
#                     left join hr_payslip_line plg on (plg.slip_id = p.id and plg.code = 'GROSS')
#                     left join hr_contract c on (p.contract_id = c.id)
#             GROUP BY
#                 e.id,
#                 e.department_id,
#                 e.company_id,
#                 wd.id,
#                 wet.id,
#                 p.id,
#                 p.name,
#                 p.date_from,
#                 p.date_to,
#                 pln.total,
#                 plb.total,
#                 plg.total,
#                 min_id.min_line,
#                 c.id,
#                 pln.name
#             Order by salary_rule desc
#             """
#         tools.drop_view_if_exists(self.env.cr, self._table)
#         self.env.cr.execute(sql.SQL("CREATE or REPLACE VIEW {} as ({})").format(sql.Identifier(self._table), sql.SQL(query)))