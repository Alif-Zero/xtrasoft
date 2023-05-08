
from openerp import models, fields, api, exceptions
from openerp.exceptions import except_orm
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
import time
import threading
import openerp
import openerp.release
import openerp.sql_db
import openerp.tools
from openerp.tools.translate import _

YearsList = [('2020','2020'),('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),('2025','2025'),('2026','2026'),('2027','2027'),('2028','2028'),('2029','2029'),('2030','2030'),('2031','2031')
                             ,('2032','2032'),('2033','2033'),('2034','2034'),('2035','2035'),('2036','2036'),('2037','2037'),('2038','2038'),('2039','2039'),('2040','2040'),('2041','2041')
                             ,('2042','2042'),('2043','2043'),('2044','2044'),('2045','2045'),('2046','2046'),('2047','2047'),('2048','2048'),('2049','2049'),('2050','2050')]

class hr_loan_type(models.Model):
    """(NULL)"""
    _name = 'hr.loan.type'
    name = fields.Char(string='Loan Type', required=True)
    rule_type_id = fields.Many2one('hr.salary.rule.type', string="Recovery Rule", domain="[('is_recovery_advances','=',True)]")


class hr_loan(models.Model):
    """(NULL)"""
    _name = 'hr.loan'
    
    
    def bulk_confirm(self):
        data = self.env['hr.loan'].search([('contract_id.employee_category.code','in',['B','C']),('company_id','=',1),('state','=','Draft')])
        ids = []
        user_name = self.env['res.users'].browse(26187).name
        error_messages = []
        for d in data:
            try:
                d.calc_name()
#                 d.submit_loan_request()
                d.confirm_loan_request()
                self.env.cr.execute("""update hr_loan set write_uid =26187, create_uid = 26187, submitted_by = 26187, confirmed_by = 26187 where id = %s""",(d.id,))
                self.env.cr.execute("""update hr_loan_line set write_uid =26187,create_uid =26187 where loan_id = %s """,(d.id,))
                self.env.cr.commit()
            except Exception as e:
                error_messages.append(str(e))
                continue
        if error_messages:
            raise ValidationError(','.join(error_messages))
        
    @api.depends('approve_amount', 'deducted_amount')
    def _cal_amount(self):
        for each in self:
            each.net_amount = round(each.approve_amount - each.deducted_amount)
    

    @api.depends('loan_line', 'loan_line.state', 'state','net_amount')
    def _calc_balance(self):
        for each in self:
            if each.loan_line:
                balance = 0
                receivable = each.net_amount
                received = 0
                for l in each.loan_line:
                    if l.state == 'Deducted':
                        received += l.amount
                balance = receivable - received
                each.balance_amount = balance
                if balance == 0 and each.state == "Approved":
                    if each and each.id:
                        self.env.cr.execute("update hr_loan set state = 'Recovered' where id = %s",(each.id,))
                    else:
                        each.state = 'Recovered'
            else:
                each.balance_amount=each.net_amount
        
    def _get_employee(self):
        employee_obj=self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        if employee_obj:
            return employee_obj.id
        else:
            return False
    
    name = fields.Char(string="Name",default='/',readonly=True)
    company_id = fields.Many2one('res.company', string='Company',related='employee_id.company_id',store=True)
    state = fields.Selection([('Draft', 'Draft'),('Waiting Approval','Waiting Approval'),('Approved', 'Approved'), ('Recovered', 'Recovered'), ('Rejected', 'Rejected')], string='Status', default='Draft')
    department_id = fields.Many2one('hr.department', string='Department',related='employee_id.department_id',store=True)
    loan_type = fields.Many2one('hr.loan.type', string='Advance Type', ondelete='restrict',required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    employee_id = fields.Many2one('hr.employee', string="Employee",default=_get_employee)
    designation_id = fields.Many2one('hr.job', string='Designation')
    contract_id = fields.Many2one('hr.contract', string='Contract Number')
    deduction_from = fields.Date(string="Deduction from Salary")
    approve_amount = fields.Integer(string="Requested Amount")
    deducted_amount = fields.Integer(string="Already Paid Amount(If Any)")
    net_amount = fields.Integer(string="Net Amount", compute=_cal_amount, store=True, readonly=True)
    installments = fields.Integer(string="No. of Installments")
    per_month_installment = fields.Integer(string="Per Month Installment",compute='_cal_installment', store=True)
    balance_amount = fields.Integer(string="Balance Amount", compute=_calc_balance, store=True)
    loan_line = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line")
    description = fields.Text(string="Note")
    submitted_by = fields.Many2one('res.users', string='Submitted By')
    submitted_at = fields.Date(string='Submitted At')
    confirmed_by = fields.Many2one('res.users', string='Approved By')
#     submitted_by = fields.Many2one('res.users', string='Submitted By')
    rejected_by = fields.Many2one('res.users', string='Rejected By')
    
    journal_id = fields.Many2one('account.journal', string="Bank Journal")
    applicable_cheque = fields.Boolean(default=False)
#     applicable_cheque = fields.Boolean(related="journal_id.allow_check_writing")
    cheque_id = fields.Many2one('account.cheque_book', string="Cheque #")
    move_id = fields.Many2one('account.move', string="Accounting Entry")
    payment_date = fields.Date(string="Payment Date")
#     period_id = fields.Many2one('account.period')
    debit_account_id = fields.Many2one('account.account', string="Account", compute='get_account')
    installment_created=fields.Boolean('Installment Created',default=False)
    installment_type=fields.Selection([('System Generated Plan','System Generated Plan'),('Manual Plan','Manual Plan')],'Installment Plan Type',default='System Generated Plan',required=True)
    
    @api.onchange('state')
    def create_installments(self):
        if self.state=='Approved':
            loan_lines=self.env['hr.loan.line'].search([('loan_id','=',self.id),('state','=','Balance')])
            if loan_lines:
                loan_lines.unlink()
    #         self.check_loan()
            balance_amount = self.balance_amount
            installments = self.installments
            amnt_per_installment = self.per_month_installment
            first_installment = 0
            diff = balance_amount - (installments * amnt_per_installment)
            first_installment = amnt_per_installment + diff 
            for i in range(0, installments):
                date_after_month = datetime.strptime(str(self.deduction_from), '%Y-%m-%d') + relativedelta(months=i)
                month_name = dict(self.env['hr.loan.line'].fields_get(['month'])['month']['selection'])[str(date_after_month.date().month).zfill(2)]
                name = month_name + ", " + str(date_after_month.date().year)
                dic = {
                       'name':name or '',
                       'month':str(date_after_month.date().month).zfill(2),
                       'year':str(date_after_month.date().year),
                       'loan_id':self.id,
                       'amount':first_installment,
                       'state':'Balance',
                       'company_id':self.company_id.id or '',
                       'department_id':self.department_id.id or '',
                       'employee_id':self.employee_id.id or '',
                       'contract_id':self.contract_id.id or '',
                       'loan_type':self.loan_type.name or ''
                       }
                self.env['hr.loan.line'].create(dic)
                first_installment = amnt_per_installment
    #         self.loan_id.installments=self.installments
    #         self.loan_id.per_month_installment=self.per_month_installment
            self.installment_created=True
    @api.depends('installments', 'balance_amount')
    def _cal_installment(self):
        for each in self:
            if each.installments:
                each.per_month_installment = round(each.balance_amount / each.installments)
            else:
                each.per_month_installment=0
    @api.constrains('employee_id','state')
    def loan_request_unique(self):
        for x in self:
            if x.employee_id and x.state and x.loan_type.name =='Loan':
                rec = x.search([('employee_id','=',x.employee_id.id),('state','not in',['Recovered','Rejected']),('loan_type.name','=','Loan')])
                if len(rec)>1:
                    raise ValidationError("""You can't apply new loan request unless previous case is settled !""")

    def bulk_payment(self):
        journal_id = self.journal_id.id
        debit_account_id = self.debit_account_id.id
        period_id = self.period_id.id
        applicable_cheque = False

        for x in self.env['hr.loan'].search([('company_id','=',self.company_id.id),('state','=','Approved'),('move_id','=',False)]):
            try:
                x.write({'journal_id':journal_id,
                         'debit_account_id':debit_account_id,
                         'period_id':period_id,
                         'applicable_cheque':applicable_cheque,
                         })
    
                x.register_payment()
                x.env.cr.commit()
                _logger.info("payment register for Advance %s"%(x.name))
            except Exception as e:
                _logger.error("Error payment register for Advance %s, %s"%(x.employee_id.name,e))
    
    
    def register_payment(self):
        account = self.debit_account_id and self.debit_account_id.id
#         if self.cheque_id and self.cheque_id.state != 'Open':
#             raise ValidationError('selected cheque has been paid, please select another one.') 
        if self.loan_type and not self.debit_account_id:
            rule_type = self.loan_type.rule_type_id or ''
            if rule_type:
                rule = self.env['hr.salary.rule'].search([('rule_type_id','=',rule_type.id)], limit=1)
                if rule and rule.account_credit:
                    account = rule.account_credit.id
            else:
                raise ValidationError('Please select rule type in %s'%(self.loan_type.name))
        if not account:
            raise ValidationError('Please define the credit account in rule type %s'%(self.loan_type.rule_type_id.name))
        
#         period = self.period_id and self.period_id.id
        timenow = time.strftime('%Y-%m-%d')
        timenow = self.date
        
        if self.journal_id and not self.journal_id.payment_credit_account_id:
            raise ValidationError('Payment Credit account not found against selected journal')

        if not self.debit_account_id:
            self.debit_account_id = account
        journal = self.journal_id
        if self.employee_id.user_id:
            partner_id = self.employee_id.user_id.partner_id.id
        else:
            partner_id=None

        
        move_lines = [(5,0,0)]
        line_vals_credit={
                        'partner_id':partner_id,
                         'name':self.name,
                         'account_id':journal.payment_credit_account_id.id or False,
                         'credit':float(self.approve_amount),
#                          'cheque_id':self.cheque_id.id or False,
#                          'move_id':move_id.id
                         }
        move_lines.append((0,0,line_vals_credit))
        line_vals_debit={
                        'partner_id':partner_id,
                         'name':self.name,
                         'account_id':account,
                         'debit':float(self.approve_amount),
#                          'move_id':move_id.id
                         }
        move_lines.append((0,0,line_vals_debit))
        move_vals={
                    'narration': self.name,
                    'company_id':self.company_id.id,
                    'ref':self.name,
                    'journal_id':journal.id,
        #             'period_id':period,
                    'date':timenow,
                    'line_ids':move_lines
                }
        move_obj=self.env['account.move'].create(move_vals)
            
        move_obj.action_post()
        self.move_id = move_obj.id
        
        
    
    @api.depends('loan_type','journal_id')
    def get_account(self):
        account = False
        if self.loan_type:
            rule_type = self.loan_type.rule_type_id or ''
            if rule_type:
                rule = self.env['hr.salary.rule'].search([('rule_type_id','=',rule_type.id)], limit=1)
                if rule and rule.account_credit:
                    account = rule.account_credit.id
        self.debit_account_id = account
        
        
    
    def get_period(self):
        period = False
        timenow = time.strftime('%Y-%m-%d')
        period_obj = self.env['account.period'].search([('date_start','<=',timenow),
                                           ('date_stop','>=',timenow),
                                           ('company_id','=',self.company_id.id)], limit=1)
        if period_obj:
            period = period_obj.id
        self.period_id = period
    
    def set_discard(self):
        for l in self.loan_line:
            if l.payslip_id and l.payslip_id.state == 'draft':
                raise ValidationError("You can not discard the record because draft payslips found  against the installment's, please first delete or confirm the the payslip")
        self.state = 'Discarded'
        self.discarded_by = self._uid
                
    
    
    def _check_user_group(self):
        group_pool = self.env['res.groups']
        user = self.env['res.users'].browse(self._uid)
        employee_pool = self.env['hr.employee']
        employee = employee_pool.search([('user_id', '=', user.id)])
        if user.has_group('lms_hr.group_salary_manager') or user.has_group('base.group_erp_manager'):
            return False
        else:
            return True

    is_readonly = fields.Boolean(string="Read Only", default=_check_user_group)
    confirmed_date = fields.Date(string='Approved Date')
    show_own_record = fields.Char(string="Own Record", compute='_get_own_advances', search='_search_own_advances')
    
    def _get_own_advances(self):
        _logger.info("user can show only his record")
         
    def _search_own_advances(self, operator, value):
        try:
            filter = []
            result = [('id','=',-1)]
            user_pool = self.env['res.users']
            user = user_pool.browse(self._uid)
            if (user.has_group('base.group_erp_manager')) or (user.has_group('lms_hr.group_salary_officer')) or (user.has_group('lms_hr.group_salary_manager')):
                result = []
            else:
                loan_obj=self.env['hr.loan'].search([('employee_id.user_id','=',self.env.user.id)]).ids
                result =  [('id','in',loan_obj)]
            return result 
        except Exception as e:
            raise ValidationError(e)

    @api.model
    def get_filtered_record(self):
        view_id_tree = self.env['ir.ui.view'].search([('name', '=', 'hr.loan.tree')])

        return {
            'type': 'ir.actions.act_window',
            'name': _('Student Profile'),
            'res_model': 'hr.loan',
            'view_type':'tree',
            'view_mode': 'tree',
            'view_id': view_id_tree.id,
#             'views': [(view_id_tree.id, 'tree'), (view_id_form.id, 'form')],
            'target': 'current',
#             'domain': [('id', 'in', loan_ids)],
        }
    
    
    def unlink(self):
        for each in self:
            if each.state != 'Draft':
                raise ValidationError('Cannot delete record which is not in draft state')
        
        return super(hr_loan, self).unlink()
    
    
    def print_record(self):
        output = 'PDF'
        report_name = 'HRLoanPreviewReport'
        tech_name = 'Loan Preview Report'
        
        params = {'loan_id':self.id,
                'printed_by':self.env.user.partner_id.name}
        self.env.cr.execute("""
          CREATE OR REPLACE VIEW view_loan_preview AS
          (SELECT l.id,
                  balance_amount,
                  deducted_amount,
                  l.employee_id,
                  l.contract_id,
                  l.designation_id,
                  per_month_installment,
                  approve_amount,
                  l.company_id,
                  installments,
                  l.state,
                  month as month_index,
                  deduction_from, date, l.loan_type,
                                        net_amount,
                                        l.department_id,
                                        description,
                                        (select name from res_users u inner join res_partner p on u.partner_id = p.id where u.id = confirmed_by) "confirmed_by_name",
                                        confirmed_date,
                                        confirmed_by,
                                        l.name,
                                        ll.id line_id,
                                        loan_id,
                                        amount,
                                        case 
                                            when month = '1' then 'Jan'
                                            when month = '2' then 'Feb'
                                            when month = '3' then 'Mar'
                                            when month = '4' then 'Apr'
                                            when month = '5' then 'May'
                                            when month = '6' then 'Jun'
                                            when month = '7' then 'July'
                                            when month = '8' then 'Aug'
                                            when month = '9' then 'Sep'
                                            when month = '10' then 'Oct'
                                            when month = '11' then 'Nov'
                                            when month = '12' then 'Dec'
                                        END as month,
                                        ll.state line_state,
                                        YEAR,
                                        REF,
                                        ll.name AS line_name,
        
             (SELECT name
              FROM res_company
              WHERE id = l.company_id ) "company_name",
        
             (SELECT name
              FROM hr_department
              WHERE id = l.department_id ) "department_name",
        
             (SELECT name
              FROM hr_loan_type
              WHERE id = l.loan_type ) "loan_type_name",
        
             (SELECT complete_name
              FROM hr_employee
              WHERE id = l.employee_id) "employee_name",
        
             (SELECT name
              FROM hr_contract
              WHERE id = l.contract_id) "contract_name",
        
             (SELECT name
              FROM hr_job
              WHERE id = l.designation_id) "designation_name"
           FROM hr_loan l
           INNER JOIN hr_loan_line ll ON ll.loan_id = l.id 
           ORDER BY year, month::integer)
           """)
        self.env.cr.commit()
        try:
            self.env.cr.execute("select id from view_loan_preview where id=" + str(self.id))
        except Exception as e:
            pass
        
        data = self.env.cr.fetchone()
        if self.loan_line:
            if data and data[0]:
                return self.env['campus.configuration.default'].download_report(params, report_name, tech_name, output)
            else:
                raise ValidationError('No record found!')
        else:
                raise ValidationError('Installment line can not be empty')
    
    
    @api.model
    def create(self, vals):
        if vals.get('employee_id', False):
            result = self.get_emp_data(vals.get('employee_id'))
            if result:
                vals['contract_id'] = result['contract_id']
                vals['designation_id'] = result['designation_id']
                vals['department_id'] = result['department_id'] 
        return super(hr_loan, self).create(vals)
    
    
    def write(self, vals):
        if vals.get('employee_id', False):
            result = self.get_emp_data(vals.get('employee_id'))
            if result:
                vals['contract_id'] = result['contract_id']
                vals['designation_id'] = result['designation_id']
                vals['department_id'] = result['department_id'] 
        super(hr_loan, self).write(vals)
    
    
    def get_emp_data(self, employee_id):
        contract = ''
        employee = self.env['hr.employee'].browse(employee_id)
        job = ''
        department = ''
        if employee and employee.contract_id.id:
            contract = employee.contract_id.id
            job = employee.contract_id.job_id.id
            department = employee.contract_id.department_id.id
        
        result = {
                  'contract_id':contract or '',
                  'designation_id':job or '',
                  'department_id':department or ''
                  }
        
        return result
        
    @api.onchange('employee_id')
    def onchange_employee(self):
        result = self.get_emp_data(self.employee_id.id)
        self.contract_id = result['contract_id']
        self.designation_id = result['designation_id']
        self.department_id = result['department_id']
    
    
    def check_loan(self):
        if self.loan_type:
            existing_loan = self.search([('employee_id', '=', self.employee_id.id), ('state', '=', 'Approved'), ('loan_type', '=', self.loan_type.id)])
            if existing_loan.ids:
                raise except_orm('Invalid Action', '\nEmployee '+self.employee_id.name+'\n already is availing the service of ' + str(self.loan_type.name).lower() + ' advance, \n record reference '+str(tuple(existing_loan.ids)))
        
    
    @api.constrains('approve_amount', 'deducted_amount', 'installments')
    def check_negative_values(self):
        if self.approve_amount < 0:
            raise ValidationError('Amount Approved can not be negative')
        if self.deducted_amount < 0:
            raise ValidationError('Already Deducted Amount can not be negative')
        if self.installments < 0:
            raise ValidationError('Installments can not be negative')
        return True
    
    
    def submit_for_approval(self):
        date = datetime.strptime(str(self.date), '%Y-%m-%d').date()
        if not self.loan_type.rule_type_id:
            raise ValidationError('Please configure recovery rules in advance types')
        rule = self.env['hr.salary.rule'].sudo().search([('rule_type_id','=',self.loan_type.rule_type_id.id)])
        if not rule:
            raise ValidationError("No rule found against rule type %s"%(self.loan_type.rule_type_id.name))
        loan_request_no = self.env['ir.sequence'].next_by_code('loan_request_seq')
        request_year=self.date.year
#         joining_month=datetime.strptime(date, '%Y-%m-%d').strftime("%m")
        self.write({'name':str(self.loan_type.name)+"-"+str(request_year)+'-'+str(loan_request_no),
                    'state':'Waiting Approval',
                    'submitted_at': fields.Date.context_today(self),
                    'submitted_by':self.env.user.id,})
        
    
    def merge_installments(self):
        form = self.env.ref('odoo_hr.view_hr_installment_merge_form')
        ids = []
        for l in self.loan_line:
            if l.state == 'Balance':
                ids.append(l.id)
        res = {
           'type': 'ir.actions.act_window',
           'name': 'Merge Installments',
           'res_model': 'hr.installment.merge',
           'view_mode': 'form',
           'view_id': form.id,
           'target': 'new',
           'context':{'default_loan_id':self.id}
       }
        return res
    
    
    def pay_balance(self):
        
        form = self.env.ref('odoo_hr.view_hr_loan_payment_form', False)
        res = {
           'type': 'ir.actions.act_window',
           'name': 'Balance Payment',
           'res_model': 'hr.loan.payment',
           'view_type': 'form',
           'view_mode': 'form',
           'view_id': form.id,
           'target': 'new',
           'auto_refresh':1,
           'context':{'default_loan_id':self.id, 'default_balance_amount':self.balance_amount, 'default_pay_amount':self.balance_amount}
           
       }
        return res

class InstallmentPlanWizard(models.TransientModel):
    _name = 'installment.plan.wizard'
    loan_id=fields.Many2one('hr.loan','Loan')
    balance_amount = fields.Integer(string="Balance Amount")
    installments = fields.Integer(string="No    . of Installments")
    per_month_installment = fields.Integer(string="Per Month Installment", compute='_cal_installment', store=True)
    
    @api.depends('installments', 'balance_amount')
    def _cal_installment(self):
        if self.installments:
            self.per_month_installment = round(self.balance_amount / self.installments)
              
    def create_installments(self):
        
        loan_lines=self.env['hr.loan.line'].search([('loan_id','=',self.loan_id.id),('state','=','Balance')])
        if loan_lines:
            loan_lines.unlink()
#         self.check_loan()
        balance_amount = self.balance_amount
        installments = self.installments
        amnt_per_installment = self.per_month_installment
        first_installment = 0
        diff = balance_amount - (installments * amnt_per_installment)
        first_installment = amnt_per_installment + diff 
        for i in range(0, installments):
            date_after_month = datetime.strptime(str(self.loan_id.deduction_from), '%Y-%m-%d') + relativedelta(months=i)
            month_name = dict(self.env['hr.loan.line'].fields_get(['month'])['month']['selection'])[str(date_after_month.date().month).zfill(2)]
            name = month_name + ", " + str(date_after_month.date().year)
            dic = {
                   'name':name or '',
                   'month':str(date_after_month.date().month).zfill(2),
                   'year':str(date_after_month.date().year),
                   'loan_id':self.loan_id.id,
                   'amount':first_installment,
                   'state':'Balance',
                   'company_id':self.loan_id.company_id.id or '',
                   'department_id':self.loan_id.department_id.id or '',
                   'employee_id':self.loan_id.employee_id.id or '',
                   'contract_id':self.loan_id.contract_id.id or '',
                   'loan_type':self.loan_id.loan_type.name or ''
                   }
            self.env['hr.loan.line'].create(dic)
            first_installment = amnt_per_installment
        self.loan_id.installments=self.installments
        self.loan_id.per_month_installment=self.per_month_installment
        self.loan_id.installment_created=True

        
class hr_installment_month(models.Model):
    _name = 'hr.installment.month'
    
    name = fields.Char(string="Name")
    code = fields.Char(string="code")

    @api.model
    def generate_month(self):
        if not self.env['hr.installment.month'].search([]):
            for x in range(1,12):
                name = str(dict(self.env['hr.loan.line']._fields['month'].selection).get(str(x).zfill(2)))
                self.create({'name': name, 'code': str(x).zfill(2)})
    
class hr_installment_merge(models.TransientModel):
    """(NULL)"""
    
    _name = 'hr.installment.merge'
    _table = 'hr_installment_merge'
    
    loan_id = fields.Many2one('hr.loan', string="Loan")
    installment_ids = fields.Many2many('hr.loan.line', string="Installments")
    month = fields.Many2one('hr.installment.month', string="Month")
    year = fields.Integer(string="Year", compute="onchange_month")
    
    
    @api.onchange('installment_ids')
    def onchange_intallments(self):
        self.month = ''
        domain = {'month':  [('id', '=', -1)]}
        month = []
        for i in self.installment_ids:
            month.append(i.month)
        if month:
            domain = {'month':[('code', 'in', month)]}
                 
        return {'domain': domain}
    
    
    @api.depends('month')
    def onchange_month(self):
        self.year = 0
        if self.month:
            for i in self.installment_ids:
                 if i.month == self.month.code:
                     self.year = i.year
    
    
    def merge_installments(self):
        if self.installment_ids:
            year = self.year
            month = self.month.code or ''
            merge_amount = 0
            for i in self.installment_ids:
                merge_amount += i.amount
                i.state = 'Merged'
            existing_installment = self.env['hr.loan.line'].search([('month', '=', month), ('month', '=', year), ('loan_id', '=', self.loan_id.id), ('state', '=', 'Balance')])
            
            month_name = dict(self.env['hr.loan.line'].fields_get(['month'])['month']['selection'])[str(self.month.code)]
            name = month_name + ", " + str(self.year)
            dic = {
                   'name':name or '',
                   'month':self.month.code or '',
                   'year':str(self.year),
                   'loan_id':self.loan_id.id,
                   'amount':merge_amount,
                   'state':'Balance',
                   'department_id':self.loan_id.department_id.id,
                   'employee_id':self.loan_id.employee_id.id,
                   'company_id':self.loan_id.company_id.id,
                   'loan_type':self.loan_id.loan_type.name or '',
                   'contract_id':self.loan_id.contract_id.id or '',
                   }
            new_id = self.env['hr.loan.line'].create(dic)
            for i in self.installment_ids:
                i.ref = new_id.name
                i.installment_id = new_id.id
             
        
class hr_loan_line(models.Model):
    """(NULL)"""
    _name = 'hr.loan.line'
    _order = 'year,month'

    name = fields.Char(string="Name",compute="_cal_name",store=True)
    loan_id = fields.Many2one('hr.loan', string="Loan", ondelete='cascade')
    month = fields.Selection([('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'),('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June')], 'Month')
    year = fields.Selection(YearsList, string="Year", type="Integer", required=True)
    amount = fields.Integer(string="Deduction Amount")
    state = fields.Selection([('Balance', 'Balance'), ('Deducted', 'Deducted'), ('Merged', 'Merged')], string='Status', default='Balance')
    ref = fields.Char(string="Reference")
    installment_id = fields.Many2one('hr.loan.line', string="Installment Reference")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Reference")
    case_state = fields.Selection(related="loan_id.state", string="Case State", store=True)
    loan_type = fields.Char(string="Advance Type",related='loan_id.loan_type.name',store=True)
    company_id = fields.Many2one('res.company', string='Campus')
    department_id = fields.Many2one('hr.department', string='Department')
    employee_id = fields.Many2one('hr.employee', string="Employee", domain="[('id','=',-1)]")
    contract_id = fields.Many2one('hr.contract', string='Contract Number')
    
    def unlink(self):
        for rec in self:
            if rec.state!='Balance':
                raise ValidationError('You are not allowed to delete this record at this state.')
        return super(hr_loan_line,rec).unlink()
    
    @api.depends('month','year')
    def _cal_name(self):
        for each in self:
            if each.year and each.month:
                each.name=str(dict(self._fields['month'].selection).get(each.month))+ ", " + str(each.year)
#                 each.name=str(each.month) + ", " + str(each.year)
            else:
                each.name=''
    
    def shift_at_last(self):
        rec = self.search([('loan_id','=',self.loan_id.id)], order="id desc", limit=1)
        month = int(rec.month)
        year = int(rec.year)
        if month and year:
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
            self.write({'year':str(year), 'month':str(month).zfill(2)})

class hr_loan_payment(models.TransientModel):
    """(NULL)"""
    _name = 'hr.loan.payment'
    
    loan_id = fields.Many2one('hr.loan', string="Loan")
    balance_amount = fields.Integer(string="Balance Amount")
    pay_amount = fields.Integer(string="Pay Amount")
    ref = fields.Char(string="Reference")
    description = fields.Text(string="Note")

    
    def pay_balance(self):
        if self.pay_amount > self.balance_amount:
            raise except_orm('Invalid Action', 'Paid amount can not greater than balanced amount')
        if self.balance_amount:
            existing_installment = self.env['hr.loan.line'].search([('loan_id', '=', self.loan_id.id), ('state', '=', 'Balance')])
            pay_amount = self.pay_amount
            balance_amount = self.balance_amount
            for e in existing_installment:
                if pay_amount:
                    if pay_amount >= e.amount:
                        e.state = 'Deducted'
                        e.ref = str(self.ref)
                        pay_amount -= e.amount
                    else:
                        e.amount = e.amount - pay_amount
                        pay_amount = 0 
                        e.ref = str(self.ref)
            self.loan_id._calc_balance()
            if self.loan_id.balance_amount == 0:
               self.loan_id.state = 'Recovered' 
               
