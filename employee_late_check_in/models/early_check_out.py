# -*- coding: utf-8 -*-
###################################################################################

from odoo import models, fields, api


class EarlyCheckOut(models.Model):
    _name = 'early.check_out'

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee', string="Employee")
    early_minutes = fields.Integer(string="Early Minutes")
    date = fields.Date(string="Date")
    amount = fields.Float(string="Amount", compute="get_penalty_amount")
    state = fields.Selection([('draft', 'Draft'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused'),
                              ('deducted', 'Deducted')], string="state",
                             default="draft")
    attendance_id = fields.Many2one('hr.attendance', string='attendance')

    # current_user_boolean = fields.Boolean()
    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('early.check_out') or '/'
        values['name'] = seq
        return super(EarlyCheckOut, self.sudo()).create(values)

    def get_penalty_amount(self):
        for rec in self:
            amount = float(self.env['ir.config_parameter'].sudo().get_param('early_deduction_amount'))
            rec.amount = amount
            if self.env['ir.config_parameter'].sudo().get_param('early_deduction_type') == 'minutes':
                rec.amount = amount * rec.early_minutes

    def approve(self):
        self.state = 'approved'

    def reject(self):
        self.state = 'refused'
    
    def set_approve(self):
        for each in self:
            each.state = 'approved'
    
    def set_reject(self):
        for each in self:
            each.state = 'refused'
