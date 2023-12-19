from odoo import http
from odoo.http import request
from odoo import http, _
from odoo.http import request
import datetime as dtime
from datetime import datetime, timedelta, date
import calendar
from odoo.tools.float_utils import float_round
from collections import defaultdict
from stdnum.exceptions import ValidationError

class SalaryReport(http.Controller):
    @http.route(['/salaryReport/<int:res_id>'], type='http', auth="user", website=True)
    def salary_report(self, res_id, **kw):
        lang_code = request.env.user.lang or 'en_US'
        lang = request.env['res.lang'].search([('code','=',lang_code)])
        format = lang.date_format
        res = request.env['hr.payslip.report.wizard'].browse(res_id)

        employee_ids = res.employee_ids or False
        date_from = datetime(res.date_from.year, res.date_from.month, 1)  or False
        date_to = datetime(res.date_to.year, res.date_to.month, calendar.monthrange(res.date_to.year, res.date_to.month)[1]) or False
        batch_id = res.payslip_run_id or False
        rule_ids = res.rule_ids or False
        struct_id = res.struct_id or False
        user = request.env.user
        single_month = False
        department_ids=[]
        if res.department_id:
            department_ids.append(res.department_id.id)
        for dept in request.env['hr.department'].search([('parent_id','=',res.department_id.id)]):
            department_ids.append(dept.id)
            
        domain = []
        if res.date_from.year == res.date_to.year and res.date_from.month == res.date_to.month:
            single_month = True
        if struct_id and date_from and date_to:
            if not employee_ids:
                if user.has_group('base.group_erp_manager') or user.has_group('hr.group_hr_manager'):
                    employee_ids = request.env['hr.employee'].search([])
            domain.append(('employee_id','in',employee_ids.ids))
            domain.append(('contract_id','in',employee_ids.mapped('contract_id').ids))
            domain.append(('date_from','>=',date_from))
            domain.append(('date_to','<=',date_to))
            domain.append(('slip_id.state','in',['verify','done','paid']))
            domain.append(('slip_id.contract_id.department_id','in',department_ids))
#             domain.append('|',('department_id.parent_id','=',res.department_id.id),('department_id','=',res.department_id.id))
            # if single_month:
            #     domain.append(('slip_id.state','in',['verify','done']))
            # else:
            #     domain.append(('slip_id.state','in',['done']))

            if batch_id:
                domain.append(('slip_id.payslip_run_id','=',batch_id.id))
            if not rule_ids:
                rule_ids = request.env['hr.salary.rule'].search([('struct_id','in',struct_id.ids)], order="sequence asc")
            else:
                rule_ids = request.env['hr.salary.rule'].search([('struct_id','in',struct_id.ids),('id','in',rule_ids.ids)], order="sequence asc")
            domain.append((('salary_rule_id','in',rule_ids.ids)))


            fields = ['name','code','total','employee_id','salary_rule_id']
            if single_month:
                fields.append('slip_id')
            groupby= ['employee_id','salary_rule_id']
            if single_month:
                groupby.append('slip_id')
            data = request.env['hr.payslip.line'].sudo().read_group(domain, fields, groupby, lazy=False)
            final_data = [{'slip':x.get('slip_id',False)[0] if x.get('slip_id',False) else False, 'rule':x['salary_rule_id'][0], 'amount':x['total'], 'employee_id':x['employee_id'][0]} for x in data]
            slip_rec =  {}
            emp_rec = {}
            employee_pool = request.env['hr.employee']
            slip_pool = request.env['hr.payslip']
            rule_pool = request.env['hr.salary.rule']
            for d in final_data:
                if single_month:
                    slip_rec.setdefault(slip_pool.browse(d['slip']), {}).update({rule_pool.browse(d['rule']):d['amount']})
                else:
                    emp_rec.setdefault(employee_pool.browse(d['employee_id']), {}).update({rule_pool.browse(d['rule']):d['amount']})
            rules_dic = defaultdict(float)
            for r in slip_rec.values():
                for k,v in r.items():
                    rules_dic[k] += v
            for r in emp_rec.values():
                for k,v in r.items():
                    rules_dic[k] += v
            salary_structure=', '.join(map(lambda x: str(x.name), struct_id))
            values = {
                    'rules':rule_ids,
                    'rule_dic':rules_dic,
                    'slip_records':slip_rec,
                    'emp_records':emp_rec,
                    'date_from':date_from.strftime('%d-%m-%Y'), 
                    'date_to':date_to.strftime('%d-%m-%Y'),
                    'structure':salary_structure or '-',
                    'batch':batch_id.name if batch_id else ''
                    }
            
            return request.render("odoo_hr.payslipdetailreport", values)

#         lang_code = request.env.user.lang or 'en_US'
#         lang = request.env['res.lang'].search([('code','=',lang_code)])
#         format = lang.date_format
#         res = request.env['hr.payslip.report.wizard'].browse(res_id)
# 
#         employee_ids = res.employee_ids or False
#         date_from = datetime(res.date_from.year, res.date_from.month, 1)  or False
#         date_to = datetime(res.date_to.year, res.date_to.month, calendar.monthrange(res.date_to.year, res.date_to.month)[1]) or False
#         batch_id = res.payslip_run_id or False
#         rule_ids = res.rule_ids or False
#         struct_id = res.struct_id or False
#         department_id=res.department_id
#         user = request.env.user
#         single_month = False
#         domain = []
#         if res.date_from.year == res.date_to.year and res.date_from.month == res.date_to.month:
#             single_month = True
#         if struct_id and date_from and date_to:
#             if not employee_ids:
#                 if user.has_group('base.group_erp_manager') or user.has_group('hr.group_hr_manager'):
#                     employee_ids = request.env['hr.employee'].search([])
# #             domain.append(('employee_id','in',employee_ids.ids))
# #             domain.append(('contract_id','in',employee_ids.mapped('contract_id').ids))
#             domain.append(('date_from','>=',date_from))
#             domain.append(('date_to','<=',date_to))
# #             domain.append(('slip_id.state','in',['verify','done','paid']))
#             # if single_month:
#             #     domain.append(('slip_id.state','in',['verify','done']))
#             # else:
#             #     domain.append(('slip_id.state','in',['done']))
# 
#             if batch_id:
#                 domain.append(('slip_id.payslip_run_id','=',batch_id.id))
#             if not rule_ids:
#                 rule_ids = request.env['hr.salary.rule'].search([('struct_id','=',struct_id.id)], order="sequence asc")
#             else:
#                 rule_ids = request.env['hr.salary.rule'].search([('struct_id','=',struct_id.id),('id','in',rule_ids.ids)], order="sequence asc")
#             domain.append((('salary_rule_id','in',rule_ids.ids)))
# 
# 
#             fields = ['name','code','total','employee_id','salary_rule_id']
#             if single_month:
#                 fields.append('slip_id')
#             groupby= ['employee_id','salary_rule_id']
# #             groupby= ['employee_id']
#             if single_month:
#                 groupby.append('slip_id')
#             query="""select 
#                        (select name from hr_employee where id=employee_id) as employee_name,
#                         (select name from hr_department where id=(select department_id from hr_contract where id=hr_payslip.contract_id)) as department_name,
#                         late_checkin_days,
#                         date_from,
#                         date_to,
#                         (select wage from hr_contract where id=hr_payslip.contract_id) as basic_salary,
#                         (select ROUND(number_of_days::integer,0) from hr_payslip_worked_days inner join hr_work_entry_type on hr_work_entry_type.id=hr_payslip_worked_days.work_entry_type_id 
#                         where payslip_id=hr_payslip.id and hr_work_entry_type.name='Attendance') as no_of_days,
#                         (select ROUND(total_present::integer,0) from hr_payslip_worked_days inner join hr_work_entry_type on hr_work_entry_type.id=hr_payslip_worked_days.work_entry_type_id 
#                         where payslip_id=hr_payslip.id and hr_work_entry_type.name='Attendance') as total_present,
#                         (select ROUND(total_absent::integer,0) from hr_payslip_worked_days inner join hr_work_entry_type on hr_work_entry_type.id=hr_payslip_worked_days.work_entry_type_id 
#                         where payslip_id=hr_payslip.id and hr_work_entry_type.name='Attendance') as total_absent,
#                         (select total from hr_payslip_line where slip_id=hr_payslip.id and name='Attendance Allowance') as attendance_allowance,
#                         (select sum(days_no_tmp) from hr_overtime where employee_id=hr_payslip.employee_id and date_from <= hr_payslip.date_to::date AND date_from>=hr_payslip.date_from::date AND state='approved') as overtime_hours,
#                         (select total from hr_payslip_line where slip_id=hr_payslip.id and name='Overtime Allowance') as overtime_allowance,
#                         (select total from hr_payslip_line where slip_id=hr_payslip.id and name='Gross Salary') as gross_salary,
#                         (select total from hr_payslip_line where slip_id=hr_payslip.id and name='Advance Salary Recovery') as advance_salary,
#                         (select total from hr_payslip_line where slip_id=hr_payslip.id and name='Deduction of Late Checkin') as late_checkin_deduction,
#                         (select total from hr_payslip_line where slip_id=hr_payslip.id and name='Personal Loan Recovery') as loan_deduction,
#                         (select total from hr_payslip_line where slip_id=hr_payslip.id and name='Unapproved Halfday') as halfday_deduction,
#                         (select total from hr_payslip_line where slip_id=hr_payslip.id and name='Absent') as absent_deduction,
#                         (select total from hr_payslip_line where slip_id=hr_payslip.id and name='Net Salary') as net_salary
#                     from 
#                         hr_payslip Where state in ('verify','done','paid') and date_from>='"""+str(res.date_from)+"""'::date and date_to<='"""+str(res.date_to)+"""'::date AND struct_id="""+str(struct_id.id)+""" and (select department_id from hr_contract where id=hr_payslip.contract_id)="""+str(department_id.id)
#             request.env.cr.execute(query)
#             record = request.env.cr.dictfetchall()
#             net_total=0
#             for rec in record:
#                 if rec['net_salary']:
#                     net_total+=rec['net_salary']
# #             data = request.env['hr.payslip.line'].sudo().read_group(domain=domain, fields=fields, groupby=groupby,lazy=False)
# #             final_data = [{'slip':x.get('slip_id',False)[0] if x.get('slip_id',False) else False, 'rule':x['salary_rule_id'][0], 'amount':x['total'], 'employee_id':x['employee_id'][0]} for x in data]
# #             slip_rec =  {}
# #             emp_rec = {}
# #             employee_pool = request.env['hr.employee']
# #             slip_pool = request.env['hr.payslip']
# #             rule_pool = request.env['hr.salary.rule']
# #             for d in final_data:
# #                 if single_month:
# #                     slip_rec.setdefault(slip_pool.browse(d['slip']), {}).update({rule_pool.browse(d['rule']):d['amount']})
# #                 else:
# #                     emp_rec.setdefault(employee_pool.browse(d['employee_id']), {}).update({rule_pool.browse(d['rule']):d['amount']})
# #             rules_dic = defaultdict(float)
# #             for r in slip_rec.values():
# #                 for k,v in r.items():
# #                     rules_dic[k] += v
# #             for r in emp_rec.values():
# #                 for k,v in r.items():
# #                     rules_dic[k] += v
#             salary_structure=', '.join(map(lambda x: str(x.name), struct_id))
#             values = {
#                     'rules':rule_ids,
# #                     'rule_dic':rules_dic,
#                     'slip_records':record,
# #                     'emp_records':emp_rec,
#                     'total':round(net_total,2),
#                     'date_from':res.date_from.strftime('%d-%m-%Y'), 
#                     'date_to':res.date_to.strftime('%d-%m-%Y'),
#                     'structure':salary_structure or '-',
#                     'batch':batch_id.name if batch_id else ''
#                     }
#             
#             return request.render("odoo_hr.payslipdetailreport", values)