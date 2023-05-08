from collections import defaultdict

import pytz
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict
from datetime import datetime, date, time, timedelta
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class hr_expiry(models.Model):
    _name = 'hr.expiry.alert'
    _rec_name = 'name'

    name = fields.Char(string="name", default="Expiry Dates")
    alert = fields.One2many('hr.expiry.lineitem', 'new_id', String="Alert")

    def update_recors(self):
        self.alert = [(5,)]
        dtoday = fields.Date.today()
        if dtoday:
            get_emps = self.env['hr.employee'].search([('active', '=', True)])
            for rec in get_emps:
                if rec.cpr_exp_date:
                    d1 = datetime.strptime(str(dtoday), '%Y-%m-%d')
                    d2 = datetime.strptime(str(rec.cpr_exp_date), '%Y-%m-%d')
                    d3 = d2 - d1
                    if int(d3.days) <= 35 and int(d3.days) > 0:
                        chkk2 = self.env['hr.expiry.lineitem'].search(
                            [('employee_id', '=', rec.id), ('reason', '=', "CPR EXPIRY")])
                        if not chkk2:
                            crt = self.env['hr.expiry.lineitem'].create({
                                'new_id': self.id,
                                'employee_id': rec.id,
                                'reason': "CPR EXPIRY",
                                'date': d2,
                                'no_of_days': int(d3.days),

                            })
                if rec.rp_exp_date:
                    d1 = datetime.strptime(str(dtoday), '%Y-%m-%d')
                    d2 = datetime.strptime(str(rec.rp_exp_date), '%Y-%m-%d')
                    d3 = d2 - d1
                    if int(d3.days) <= 35 and int(d3.days) > 0:
                        chkk3 = self.env['hr.expiry.lineitem'].search(
                            [('employee_id', '=', rec.id), ('reason', '=', "RP EXPIRY")])
                        if not chkk3:
                            crt = self.env['hr.expiry.lineitem'].create({
                                'new_id': self.id,
                                'employee_id': rec.id,
                                'reason': "RP EXPIRY",
                                'date': d2,
                                'no_of_days': int(d3.days),

                            })
                if rec.passport_exp_date:
                    d1 = datetime.strptime(str(dtoday), '%Y-%m-%d')
                    d2 = datetime.strptime(str(rec.passport_exp_date), '%Y-%m-%d')
                    d3 = d2 - d1
                    print("date diff",d3)
                    print("date d1",d1)

                    print("date d2",d2)

                    if int(d3.days) <= 35 and int(d3.days) > 0:
                        chkk1 = self.env['hr.expiry.lineitem'].search(
                            [('employee_id', '=', rec.id), ('reason', '=', "PASSPORT EXPIRY")])
                        if not chkk1:
                            crt = self.env['hr.expiry.lineitem'].create({
                                'new_id': self.id,
                                'employee_id': rec.id,
                                'reason': "PASSPORT EXPIRY",
                                'date': d2,
                                'no_of_days': int(d3.days),

                            })
            # self.no_of_days = int(d3.days)

    # @api.depends('name')
    # def default_value(self):
    #     if self.name:
    #           self.reason=str("expired Employee List") + self.name


class line_item(models.Model):
    _name = 'hr.expiry.lineitem'

    new_id = fields.Many2one('hr.expiry.alert', string="Type ID")
    employee_id = fields.Many2one('hr.employee', string="Employee ID")
    reason = fields.Char(String="Reason")
    date = fields.Date(string="Date Expiry")
    # current_date = fields.Date(string='Your string', default=datetime.today())
    no_of_days = fields.Integer(string="No. of Days")

    # @api.onchange('date')
    # def calculate_date(self):
    #     if self.date and self.current_date:
    #         d1 = datetime.strptime(str(self.date), '%Y-%m-%d')
    #         d2 = datetime.strptime(str(self.current_date), '%Y-%m-%d')
    #         d3 = d2 - d1
    #         self.no_of_days = int(d3.days)
