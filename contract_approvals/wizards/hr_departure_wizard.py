# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import UserError


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    set_date_end = fields.Boolean(string="Set Contract End Date", default=True)

    def action_register_departure(self):
        self.employee_id.contract_ids.write(
            {'state': 'cancel','state2':'cancel'}
            )
        return super().action_register_departure()