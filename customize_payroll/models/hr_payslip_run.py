# -*- coding: utf-8 -*-

from odoo import models, api, fields
import logging
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class HRPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def _get_period_id(self):
        month = date.today().month
        period = self.env['payslip.period'].search([('month_from', '=', month)], limit=1)
        return period

    period_id = fields.Many2one('payslip.period', default=_get_period_id,string="Payslip Month")

    @api.onchange('period_id')
    def _onchange_period_id(self):
        for rec in self:
            if rec.state == 'draft' and rec.period_id:
                year = date.today().year
                date_from = date(year,int(rec.period_id.month_from),int(rec.period_id.day_from))
                rec.date_start = date_from
                if rec.period_id.month_to < rec.period_id.month_from:
                    year += 1
                date_to = date(year,int(rec.period_id.month_to),int(rec.period_id.day_to))
                rec.date_end = date_to 
                # fields.Date.to_string(date.today().replace(day=1))
                # date_to = fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())