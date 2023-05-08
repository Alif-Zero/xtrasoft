# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import datetime as dt

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone

import datetime
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

# class Employee(models.Model):
#     _inherit = 'hr.payslip'
#
#     register_id=fields.Many2one('hr.contribution.register',string="Contribution Register")


# class Employee_contractsx(models.Model):
#     _inherit = 'hr.contract'


    # @api.model
    # def comp_gross_salery(self, employee_id, input, catg,payslip):
    #     if employee_id:
    #         nis = 0.0
    #
    #         if payslip.dict.register_id.name in ['Employees', 'Employers']:
    #             chk = (catg.GROSS)
    #         else:
    #             return 0
    #         if chk > 125000:
    #             nis = 3750
    #         else:
    #             nis = str((catg.GROSS * 3) / 100)
    #         return nis
    #     else:
    #         return 0
    #
    # @api.model
    # def comp_nhs_salery(self, employee_id, input, catg,payslip):
    #     if employee_id:
    #         print(payslip)
    #         _logger.info(payslip)
    #         _logger.info(payslip.dict)
    #
    #         nis = 0.0
    #         if payslip.dict.register_id.name == 'Employees':
    #             nis = str((catg.GROSS * 2) / 100)
    #         elif payslip.dict.register_id.name == 'Employers':
    #             nis = str((catg.GROSS * 3) / 100)
    #         else:
    #             return 0
    #         return nis
    #     else:
    #         return 0
    #
    # @api.model
    # def comp_edu_salery(self, employee_id, input, catg, niss,payslip):
    #     if employee_id:
    #         nis = 0.0
    #         if payslip.dict.register_id.name == 'Employees':
    #             nis = ((catg.GROSS - niss) * 2.25) / 100
    #         elif payslip.dict.register_id.name == 'Employers':
    #             nis = str((catg.GROSS - niss) * 3.5 / 100)
    #         else:
    #             return 0
    #         return nis
    #     else:
    #         return 0
    #
    # @api.model
    # def comp_payp_salery(self, employee_id, input, catg, niss,payslip):
    #     if employee_id:
    #         nis = 0.0
    #         netnew = 0
    #         if payslip.dict.register_id.name == 'Employees':
    #             gros = catg.GROSS * 12
    #             if gros > 1500000:
    #                 net = gros - 1500000
    #                 netnew = net
    #                 nis = ((gros - (niss *12) - 1500000) * 25) / 100
    #                 nis=nis/12
    #             else:
    #                 return 0
    #         else:
    #             return 0
    #         return nis
    #     else:
    #         return 0
    #
    # @api.model
    # def comp_heart_salery(self, employee_id, input, catg, niss,payslip):
    #     if employee_id:
    #         nis = 0.0
    #         if payslip.dict.register_id.name == 'Employers':
    #             nis = ((catg.GROSS) * 3) / 100
    #         else:
    #             return 0
    #
    #         return nis
    #     else:
    #         return 0
