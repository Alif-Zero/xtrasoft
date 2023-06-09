from odoo import models, fields,api, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class HRContract(models.Model):
    _inherit = 'hr.contract'

    def calc_overtime_allowance_1(self, rule, contract, payslip):
        ot_allowance = 0.0
        try:
            ot_records = self.env['hr.overtime'].search([('employee_id', '=', payslip.employee_id),
                                                             ('state', '=', 'approved'),
                                                             ('type','=','cash')
                                                             ])
            for ot in ot_records:
                if ot.date_from.date()<=payslip.date_to and ot.date_from.date()>=payslip.date_from:
                    ot_allowance+=ot.cash_hrs_amount
        except Exception as e:
            _logger.exception("Salary Rule Information: Allowance of Overtime Rule (calc_overtime_allowance), Rule Code %s Error Message: %s" % (rule, str(e)))
        return ot_allowance

    def calc_overtime_allowance_type(self, rule, contract, payslip,type_id=[]):
        ot_allowance = 0.0
        try:
            if type_id:
                overtime_type = self.env['overtime.type'].search([('id', 'in', type_id)])
            else:
                overtime_type = self.env['overtime.type'].search([])

            ot_records = self.env['hr.overtime'].search([('employee_id', '=', payslip.employee_id),
                                                             ('state', '=', 'approved'),
                                                             ('type','=','cash'),
                                                             ('overtime_type_id','in',overtime_type.ids),
                                                             ])
            for ot in ot_records:
                if ot.date_from.date()<=payslip.date_to and ot.date_from.date()>=payslip.date_from:
                    ot_allowance+=ot.cash_hrs_amount
        except Exception as e:
            _logger.exception("Salary Rule Information: Allowance of Overtime Rule (calc_overtime_allowance), Rule Code %s Error Message: %s" % (rule, str(e)))
        return ot_allowance
    

    over_hour = fields.Monetary('Hour Wage')
    over_day = fields.Monetary('Day Wage')
    
   

class InheritPayslip1(models.Model):
    _inherit='hr.payslip'
    
    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id: # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        lang = employee.sudo().address_home_id.lang or self.env.user.lang
        context = {'lang': lang}
        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        del context

        self.name = '%s - %s - %s' % (
            payslip_name,
            self.employee_id.name or '',
            format_date(self.env, self.date_to, date_format="MMMM y", lang_code=lang)
        )

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _(
                "This payslip can be erroneous! Work entries may not be generated for the period from %(start)s to %(end)s.",
                start=date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1),
                end=date_to,
            )
        else:
            self.warning_message = False

        self.worked_days_line_ids = self._get_new_worked_days_lines()
