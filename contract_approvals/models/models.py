# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MultiPurchaseApprovals(models.Model):
    _inherit = 'hr.contract'

    state2 = fields.Selection([
        ('draft', 'New'),
        ('waiting_for_approval_1', 'Finance'),
        ('waiting_for_approval_2', 'CEO Approval'),
        ('probation', 'Probation'),
        ('open', 'Permanent'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', readonly=False, related='hr_state')

    hr_state = fields.Selection([

        ('draft', 'New'),
        ('waiting_for_approval_1', 'Finance'),
        ('waiting_for_approval_2', 'CEO Approval'),
        ('probation', 'Probation'),
        ('open', 'Permanent'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
    ], string='Status', )

    # def HrStatus(self):
    #     if self.state2 == 'probation':
    #         self.hr_state = 'probation'
    #     else:
    #         self.hr_state = ''

    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
        required=True,
        copy=False,
        track_visibility="onchange",
        default=lambda self: self.env.user

    )

    def submit_for_approval_1(self, template_xmlid=None):
        if self.state2 == 'draft':
            self.state2 = 'waiting_for_approval_1'

        # self.write({"state": "waiting_for_approval_1"})

        mail_server = self.env['ir.mail_server'].sudo().search([], limit=1)
        contract_manager = self.env.ref('contract_approvals.group_contract_approval_1').users
        for user in contract_manager:
            activty_type = self.env.ref('contract_approvals.contract_approval_activity').id
            activity_id = self.env['mail.activity'].create({
                'res_id': self.id,
                'summary': 'Please confirm Contract {} request'.format(self.name),
                'activity_type_id': activty_type,
                'res_model_id': self.env['ir.model'].search([('model', '=', 'hr.contract')], limit=1).id,
                'user_id': user.id,
            })
        # if contract_manager:
        #     ctx = {}
        #     if mail_server:
        #         ctx['email_from'] = mail_server.smtp_user
        #     else:
        #         pass
        #         ctx['email_from'] = self.requested_by.login
        #     email_list = [approver.login for approver in contract_manager]
        #     if email_list:
        #         ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
        #         ctx['approver_name'] = self.env.user.name
        #         template = self.env.ref('contract_approvals.first_contract_approval_email_template')
        #         template.with_context(ctx).sudo().send_mail(self.id, force_send=True, raise_exception=False)

        # # form_view = self.env.ref('module.view_form_application')
        # # approve_template = self.env.ref(template_xmlid)
        #     colors = {
        #         'needsAction': 'grey',
        #         'approved': 'green',
        #         'tentative': '#FFFF00',
        #     }
        #     rendering_context = dict(self._context)

        #     rendering_context.update({
        #         'color': colors,
        #         'action_id': self.env['ir.actions.act_window'].search([('view_id', '=', template.id)], limit=1).id,
        #         'dbname': self._cr.dbname,
        #         'base_url': self.env['ir.config_parameter'].get_param('web.base.url', default='http://localhost:8069')

        #     })

    def submit_for_approval_2(self):
        if self.state2 == 'waiting_for_approval_1':
            self.state2 = 'waiting_for_approval_2'
            contract_manager = self.env.ref('contract_approvals.group_contract_approval_2').users
            for user in contract_manager:
                activty_type = self.env.ref('contract_approvals.contract_approval_activity').id
                activity_id = self.env['mail.activity'].create({
                    'res_id': self.id,
                    'summary': 'Please confirm Contract {} request'.format(self.name),
                    'activity_type_id': activty_type,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'hr.contract')], limit=1).id,
                    'user_id': user.id,
                })

    def approved(self):
        if self.state2 == 'waiting_for_approval_2':
            self.state2 = 'probation'

        # self.write({"state": "to_2_approve"})

        # mail_server = self.env['ir.mail_server'].sudo().search([], limit=1)
        # contract_manager = self.env.ref('contract_approvals.group_contract_approval_2').users
        # if contract_manager:
        #     ctx = {}
        #     if mail_server:
        #         ctx['email_from'] = mail_server.smtp_user
        #     else:
        #         pass
        #         ctx['email_from'] = self.requested_by.login
        #     email_list = [approver.login for approver in contract_manager]
        #     if email_list:
        #         ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
        #         ctx['approver_name'] = self.env.user.name
        #         template = self.env.ref('contract_approvals.second_contract_approval_email_template')
        #         template.with_context(ctx).sudo().send_mail(self.id, force_send=True, raise_exception=False)

    def button_rejected(self):
        self.write({"state2": "cancel"})

        mail_server = self.env['ir.mail_server'].sudo().search([], limit=1)
        ctx = {}
        if mail_server:
            ctx['email_from'] = mail_server.smtp_user
        else:
            ctx['email_from'] = self.requested_by.login
        email_list = [self.requested_by.login]
        if email_list:
            ctx['notification_to_initiator'] = ','.join([email for email in email_list if email])
            ctx['rejected_by'] = self.env.user.name
            template = self.env.ref('contract_approvals.contract_approval_reject_email_template')
            template.with_context(ctx).sudo().send_mail(self.id, force_send=True, raise_exception=False)

    def button_probation(self):
        self.write({"state2": "probation"})

    def button_open(self):
        self.write({"state2": "open"})

    def button_close(self):
        self.write({"state2": "close"})

    def button_cancel(self):
        self.write({"state2": "cancel"})