# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from collections import defaultdict

import pytz
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict
from datetime import datetime, date, time, timedelta
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    date_of_join = fields.Date('Joining Date')
    resign = fields.Boolean(default=False, string="Resign?")
    terminate = fields.Boolean(default=False, string="Terminate?")
    runaway = fields.Boolean(default=False, string="Runaway?")

    manager_log = fields.Many2one('res.users', string="Manager")

    date_of_leave = fields.Date('Resign/Leave/Terminate Date')
    bank_name = fields.Char(string="Bank Name")
    Ac_number = fields.Char(string="A/C Number")

    consider_days = fields.Integer(string="Total Work Day(s)", compute="_get_days_calculation")
    absents = fields.Integer(string="Absents", compute="_get_days_calculation")
    is_notice_period_served=fields.Boolean('Notice Period Served')
    is_np_waive_served=fields.Boolean('Notice Period Waive Off')
    
    @api.onchange('is_notice_period_served')
    def _cal_termination_date(self):
        if self.is_notice_period_served:
            self.date_of_leave=fields.Datetime.now()
        else:
            self.date_of_leave=None
    
    @api.onchange('is_np_waive_served')
    def _cal_notice_period_served(self):
        if self.is_np_waive_served:
            self.date_of_leave=fields.Datetime.now()
            self.is_notice_period_served=True
        else:
            self.date_of_leave=None
            self.is_notice_period_served=False

            
    def _get_days_calculation(self):
        payslip = self.env['hr.payslip.run'].browse(self._context.get('active_ids'))

        t_date_month = datetime.now().date().month
        for rec in self:
            if payslip.date_start and payslip.date_end and rec.id:
                total = self.env['attendance.custom'].search_count(
                    [('attendance_date', '>=', payslip.date_start), ('attendance_date', '<=', payslip.date_end),
                     ('employee_id', '=',
                      rec.id)
                     ])
                if payslip.date_end.day == 31:
                    if total > 30:
                        total -= 1
                if payslip.date_end.month == 2:
                    if payslip.date_end.day in [28, 29]:
                        total += 2

                df = payslip.date_start
                dt = payslip.date_end
                absnt = 0

                delta = timedelta(days=1)
                while df <= dt:
                    print(df)
                    check_attendence = self.env['attendance.custom'].search(
                        [('absent', '=', True),
                         ('attendance_date', '=', df), ('employee_id', '=', rec.id)])
                    if check_attendence:
                        absnt += 1
                    df += delta

                rec.absents = absnt
                if not total <= 0:
                    rec.consider_days = total - absnt
                else:
                    rec.consider_days = 0
            else:
                rec.consider_days = 30
                rec.absents = 0

    @api.onchange('resign', 'terminate', 'runaway')
    def resign_lv(self):
        if self.resign or self.terminate or self.runaway:
            self.manager_log = self.env.user.id
            self.active = False
        else:
            self.active = True


class HrPayslip_inherits(models.Model):
    _inherit = "hr.payslip"

    total_work_day = fields.Integer(string="Total Work Day(s)", compute="_get_days_calculation")
    absents = fields.Integer(string="Absents", compute="_get_days_calculation")
    sick_leaves = fields.Integer(string="Sick Leave(s)", compute="_get_days_calculation")
    consider_days = fields.Integer(string="Consider Days", compute="_get_days_calculation")
    absents_payslip=fields.Integer(string="Absent Payslip", compute="_get_days_calculation")

    def check_modif_records(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.employee_id:
                total = self.env['attendance.custom'].search_count(
                    [('attendance_date', '>=', rec.date_from), ('attendance_date', '<=', rec.date_to),
                     ('employee_id', '=',
                      rec.employee_id.id)
                        , ('is_modif', '=', True)
                     ])
                if total > 0:
                    self.Validatex()

    def Validatex(self):
        payslip = self.env['hr.payslip'].browse(self.id)
        if payslip:
            total = self.env['attendance.custom'].search(
                [('attendance_date', '>=', payslip.date_from),
                 ('attendance_date', '<=', payslip.date_to),
                 ('employee_id', '=',
                  payslip.employee_id.id),
                 ('is_modif', '=', True)
                 ])
            for rec in total:
                rec.state = 'Validated'
                rec.absent = True
                rec.note = str(payslip.name) + " Has validated them"

    @api.depends('date_from', 'date_to', 'employee_id')
    def _get_days_calculation(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.employee_id:
                total = self.env['attendance.custom'].search_count(
                    [('attendance_date', '>=', rec.date_from), ('attendance_date', '<=', rec.date_to),
                     ('employee_id', '=',
                      rec.employee_id.id),
                     ('sick_leave', '=',
                      False)

                     ])
                total_sick = self.env['attendance.custom'].search_count(
                    [('attendance_date', '>=', rec.date_from), ('attendance_date', '<=', rec.date_to),
                     ('employee_id', '=',
                      rec.employee_id.id),
                     ('sick_leave', '=',
                      True)
                     ])
                if rec.date_to.day == 31:
                    if total > 30:
                        total -= 1
                if rec.date_to.month == 2:
                    if rec.date_to.day in [28, 29]:
                        total += 2

                df = rec.date_from
                dt = rec.date_to
                absnt = 0

                delta = timedelta(days=1)
                while df <= dt:
                    print(df)
                    check_attendence = self.env['attendance.custom'].search(
                        [('absent', '=', True),
                         ('attendance_date', '=', df), ('employee_id', '=', rec.employee_id.id)])
                    if check_attendence:
                        absnt += 1
                    df += delta

                rec.total_work_day = total
                rec.absents = absnt
                rec.absents_payslip = absnt
                rec.sick_leaves = total_sick
                if not total <= 0:
                    rec.consider_days = total - absnt
                else:
                    rec.consider_days = 0
            else:
                rec.sick_leaves = 0
                rec.consider_days = 30
                rec.total_work_day = 30
                rec.absents = 0
                rec.absents_payslip = 0

    def compute_sheet(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            payslip.check_modif_records()

            df = payslip.date_from
            dt = payslip.date_to
            delta = timedelta(days=1)
            while df <= dt:
                print(df)
                check_attendence = self.env['attendance.custom'].search(
                    [('attendance_date', '=', df), ('employee_id', '=', payslip.employee_id.id)])
                if not check_attendence:
                    day = df.strftime('%A')
                    if day != 'Friday':
                        pass
                        # raise UserError(
                        #     _("Attendance of %s not found in system . Please mark attendance first") % (str(df)))
                df += delta

            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
            payslip.write({'line_ids': lines, 'number': number, 'state': 'verify', 'compute_date': fields.Date.today()})
        return True




class leaveallocation_inherit(models.Model):
    _inherit = "hr.leave.allocation"

    def update_paid_days(self):
        for rec in self.search([]):
            if rec.holiday_status_id.name == 'Paid Time Off':
                rec.number_of_days += 2.5


class HrPayslipEmployees_inheritx(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _get_available_contracts_domain(self):
        return [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]

    def _get_employees(self):
        # YTI check dates too
        t_date_month = datetime.now().date().month

        emp = self.env['hr.employee']
        lst = self.env['hr.employee'].search(self._get_available_contracts_domain())
        for rec in lst:
            line = rec.slip_ids.filtered(lambda r: r.date_from.month == t_date_month)
            if not line:
                emp += rec

        return emp

    def _check_undefined_slots(self, work_entries, payslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            calendar_start = pytz.utc.localize(
                datetime.combine(max(contract.date_start, payslip_run.date_start), time.min))
            calendar_end = pytz.utc.localize(
                datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), time.max))
            outside = contract.resource_calendar_id._attendance_intervals(calendar_start,
                                                                          calendar_end) - work_entries._to_intervals()
            if outside:
                pass
                # raise UserError(_("Some part of %s's calendar is not covered by any work entry. Please complete the schedule.") % contract.employee_id.name)

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        if not self.employee_ids:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = self.employee_ids._get_contracts(payslip_run.date_start, payslip_run.date_end,
                                                     states=['open', 'close'])
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', self.employee_ids.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        validated = work_entries.action_validate()
        if not validated:
            pass
            # raise UserError(_("Some work entries could not be validated."))

        default_values = Payslip.default_get(Payslip.fields_get())
        for contract in contracts:
            values = dict(default_values, **{
                'employee_id': contract.employee_id.id,
                'credit_note': payslip_run.credit_note,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslip = self.env['hr.payslip'].new(values)
            payslip._onchange_employee()
            payslip.check_modif_records()
            values = payslip._convert_to_write(payslip._cache)
            payslips += Payslip.create(values)
        payslips.compute_sheet()
        payslip_run.state = 'verify'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
