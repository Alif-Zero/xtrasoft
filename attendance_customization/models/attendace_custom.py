# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import datetime as dt
from datetime import datetime
from datetime import datetime, date, time, timedelta
from datetime import date, datetime
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone

import datetime
from odoo.exceptions import UserError, ValidationError



class Attendance(models.Model):
    _name = 'hr.attendance'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', required=True)
    roll_number = fields.Char(related='employee_id.identification_id')

    attendance_date = fields.Date(string='Attendance Date', required=True, default=fields.Date.context_today)
    job_title = fields.Char(string='Job Title', compute='get_jobtitle')
    status = fields.Char(string='Status')
    custom_ID = fields.Char(string='ID')
    title = fields.Char(string='Title')
    a_stat = fields.Char(string='Status', default="A")

    first_check_in = fields.Char(string='Check In(1st)')
    first_check_out = fields.Char(string='Check Out(1st)')
    first_shift_total_hours = fields.Char(compute='onchangefirst_checkin_checkout', string='Hrs(1st)')
    working = fields.Char(compute='get_workingtime', string='Working')
    second_check_in = fields.Char(string='Check In(2nd)')
    second_check_out = fields.Char(string='Check Out(2nd)')
    second_shift_total_hours = fields.Char(compute='onchangesecond_checkin_checkout', string='Hrs(2nd)')
    job_code = fields.Char(string='JobCode')
    site = fields.Char(string='Site')
    late_in = fields.Char(string='Late In')
    early_in = fields.Char(string='Early In')
    early_out = fields.Char(string='Early Out')
    ot_125 = fields.Char(string='OT 1.25', compute='get_ot_hours')
    ot_15 = fields.Char(string='OT 1.5', compute='get_ot_hours')
    no_attend = fields.Char(string='No Attend')
    ignored = fields.Char(string='Ingored')
    exception_approved = fields.Boolean(string='Exception Approved')
    apply_latein_deduction = fields.Boolean(compute='apply_latein', store=True, string='Apply Latein deduction')
    sick_leave = fields.Boolean(string="Sick leave", default=False)
    absent = fields.Boolean(string="Absent", default=False)
    sick_from = fields.Date(string="Leave From")
    sick_to = fields.Date(string="Leave To")
    leave = fields.Boolean(string="leave", default=False)
    leave_from = fields.Date(string="Leave From")
    leave_to = fields.Date(string="Leave To")

    Emerg = fields.Boolean(string="Emergency leave", default=False)
    emerg_from = fields.Date(string="Emergency From")
    # emerg_to = fields.Date(string="Emergency To")

    Unpaid = fields.Boolean(string="un-paid leaves", default=False)
    unpaid_from = fields.Date(string="Un-paid From")
    unpaid_to = fields.Date(string="Un-paid To")

    Mater = fields.Boolean(string="Maternity Leaves", default=False)
    mater_from = fields.Date(string="Maternity From")
    mater_to = fields.Date(string="Maternity To")

    Busi = fields.Boolean(string="Buissness Leaves", default=False)
    busi_from = fields.Date(string="Buissness From")
    busi_to = fields.Date(string="buissness To")

    check_ot_lunch = fields.Boolean(default=False, string="Allow OT Lunch")
    allow_viewotf = fields.Boolean("allow", compute='chk_allowed', default=False)
    allow_viewoto = fields.Boolean("allow", compute='chk_allowed', default=False)

    check_ot_normal = fields.Boolean(default=False, string="Allow OT Normal")