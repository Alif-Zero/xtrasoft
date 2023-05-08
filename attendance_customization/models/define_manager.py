from collections import defaultdict

import pytz
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict
from datetime import datetime, date, time, timedelta
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class hr_def_main(models.Model):
    _name = 'hr.define.emp'
    _rec_name = 'department_id'

    employee_id = fields.Many2one('hr.employee', string="Department Head", required=True)
    department_id = fields.Many2one(related="employee_id.department_id", readonly=True,
                                    string="Department")
    members = fields.One2many('hr.define.members', 'new_id', String="Members")


    @api.constrains('employee_id', 'department_id')
    def _check_unique_sequence_number(self):
        head = self.filtered(lambda move: move.employee_id.id == self.employee_id.id)
        if len(head)>1:
            raise UserError("Record with same head already exist. Delete/Update it first")




            # self.no_of_days = int(d3.days)

    # @api.depends('name')
    # def default_value(self):
    #     if self.name:
    #           self.reason=str("expired Employee List") + self.name


class line_item_member(models.Model):
    _name = 'hr.define.members'

    new_id = fields.Many2one('hr.define.emp', string="Type ID")
    employee_id = fields.Many2one('hr.employee', string="Member")
    department_id = fields.Many2one(related="employee_id.department_id", readonly=True,
                                    string="Department")

    @api.onchange('employee_id')
    def employee_id_onchng(self):
        if self.employee_id:
            if self.new_id.employee_id:
                if self.employee_id.department_id.id == self.new_id.department_id.id:
                    pass
                else:
                    raise UserError("Member should belong to the same department as of head")
            else:
                raise UserError("Please select Head of dept first")

    #         d1 = datetime.strptime(str(self.date), '%Y-%m-%d')
    #         d2 = datetime.strptime(str(self.current_date), '%Y-%m-%d')
    #         d3 = d2 - d1
    #         self.no_of_days = int(d3.days)
