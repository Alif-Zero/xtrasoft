# -*- coding: utf-8 -*-

from odoo import models, fields, api


class contract_form(models.Model):
    _inherit = 'hr.contract'

    job_description = fields.Html()
    # no_onss = fields.Boolean()
    # no_withholding_taxes = fields.Boolean()
    # rd_percentage = fields.Integer()
    badge_id = fields.Char(related='employee_id.barcode')


class PaySlipFilter(models.Model):
    _inherit = 'hr.payslip'

    badge_id = fields.Char(related='employee_id.barcode')

