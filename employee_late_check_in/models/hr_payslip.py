# -*- coding: utf-8 -*-

from odoo import models, api, fields

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'
        
    def _get_available_contracts_domain(self):
        super(HrPayslipEmployees,self)._get_available_contracts_domain()
        return [('contract_ids.state', 'in', ('open', 'probation')), ('company_id', '=', self.env.company.id)]

class PayslipLateCheckIn(models.Model):
    _inherit = 'hr.payslip'

    late_check_in_ids = fields.Many2many('late.check_in')
    early_check_out_ids = fields.Many2many('early.check_out')

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """
        function used for writing late check-in record in payslip
        input tree.

        """
        res = super(PayslipLateCheckIn, self).get_inputs(contracts, date_to, date_from)
        late_check_in_type = self.env.ref('employee_late_check_in.late_check_in')
        contract = self.contract_id
        late_check_in_id = self.env['late.check_in'].search([('employee_id', '=', self.employee_id.id),
                                                             ('date', '<=', self.date_to),
                                                             ('date', '>=', self.date_from),
                                                             ('state', '=', 'approved'),
                                                             ])
        
        amount = late_check_in_id.mapped('amount')
        cash_amount = sum(amount)
        if late_check_in_id:
            self.late_check_in_ids = late_check_in_id
            input_data = {
                'name': late_check_in_type.name,
                'code': late_check_in_type.code,
                'amount': cash_amount,
                'contract_id': contract.id,
            }
            
        early_check_out_type = self.env.ref('employee_late_check_in.early_check_out')
        contract = self.contract_id
        early_check_out_id = self.env['early.check_out'].search([('employee_id', '=', self.employee_id.id),
                                                             ('date', '<=', self.date_to),
                                                             ('date', '>=', self.date_from),
                                                             ('state', '=', 'approved'),
                                                             ])
        
        amount = early_check_out_id.mapped('amount')
        cash_amount = sum(amount)
        if early_check_out_id:
            self.early_check_out_ids = early_check_out_id
            input_data = {
                'name': early_check_out_id.name,
                'code': early_check_out_id.code,
                'amount': cash_amount,
                'contract_id': contract.id,
            }
            res.append(input_data)
        return res
    
    

    def action_payslip_done(self):
        """
        function used for marking deducted Late check-in
        request.

        """
        for recd in self.late_check_in_ids:
            recd.state = 'deducted'
        return super(PayslipLateCheckIn, self).action_payslip_done()
