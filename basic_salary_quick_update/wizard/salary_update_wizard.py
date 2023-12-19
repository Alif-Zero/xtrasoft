# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SalaryUpdateWizard(models.TransientModel):
    _name = 'salary.update.wizard'

    type = fields.Selection(
        string='Type',
        selection=[('fixed', 'Fixed Amount'),
                   ('percent', 'Percent'), ],
        required=True,default='percent' )

    percent = fields.Float(
        string='Percent',
        required=False)
    amount = fields.Float(
        string='Amount',
        required=False)

    contract_ids = fields.Many2many(
        comodel_name='hr.contract',
        string='Contracts')

    def apply_update(self):
        for contract in self.contract_ids:
            if self.type == 'fixed':
                contract.sudo().update({'wage': contract.wage + self.amount})
            elif self.type == 'percent':
                wage_addition = contract.wage * (self.percent / 100)
                contract.sudo().update({'wage': contract.wage + wage_addition})

