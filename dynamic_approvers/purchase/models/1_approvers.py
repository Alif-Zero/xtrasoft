# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import tools
from lxml import etree
from odoo.tools.safe_eval import safe_eval
from ... import generic as gen
from num2words import num2words


class ApprovalRejectionWizard(models.TransientModel):
    _name='approval.rejection.wizard'
    approval_id=fields.Many2one('document.approver.detail','Approval')
    rejection_comments=fields.Text('Rejection Comments')
    
    def reject(self):
        self.approval_id.reject(self.rejection_comments)
        
class document_approver(models.Model):
    _name = "document.approver"
    _order = 'sequence'
    _description ="Manage Document Approvers"
    
    
#     @api.onchange('system_user')
#     def onchange_system_user(self):
#         self.user_id = ''
#         self.name = ''
    
#     @api.depends('user_id')
#     def _get_name(self):
#         for x in self:
#             name = ''
#             if x.user_id:
#                 name = x.user_id.name
#             x.name = name
    
#     name = fields.Char(string="User", compute=_get_name, store=True)
#     system_user = fields.Boolean(string="Is System User", default=True)
    sequence = fields.Integer(string="Sequence")
    user_id = fields.Many2one('res.users', string="Approver")
    authority = fields.Char(string="Approved As")
#     user2_id = fields.Many2one('res.users',string="Delegated User", relation="res.users")
#     authority2 = fields.Char(string="Approved As")
    document_type = fields.Selection(gen.DocumentTypes, string="Document Type")
    action_taken_as = fields.Char(string="Action Taken as")


class document_approver_detail(models.Model):
    _name = "document.approver.detail"
    _order = 'sequence'
    _description ="Manage Document Approvers Detail"
    
    name = fields.Char(string="User")
    sequence = fields.Integer(string="Sequence")
    model = fields.Char(string="Model")
    res_id = fields.Integer(string="Record")
    document_type = fields.Char(string="Document Type")
    user_id = fields.Many2one('res.users', string="Approver")
    authority = fields.Char(string="Approved As") 
    action = fields.Selection([('Accept','Accept'),('Reject','Reject')], string="Action")
    date = fields.Datetime(string="Approved Date")
    comment = fields.Text(string="Comment")
    po_id = fields.Many2one('purchase.order', ondelete='cascade')
    image_128 = fields.Binary(related="user_id.image_128", readonly=False, relation="res.users")
    previous_approval = fields.Many2one('document.approver.detail')
    valid_user = fields.Integer(compute="_check_validity", default=0)
    action_taken_as = fields.Char(string="Action Taken as")
    pr_id=fields.Many2one('purchase.request','Purchase Request')
    loan_id=fields.Many2one('hr.loan','HR Loan')
    
    def _check_validity(self):
        for x in self:
            valid = 0
            if x.user_id.id == x.env.user.id:
                if x.previous_approval:
                    if x.previous_approval.action == 'Accept' and x.action not in ('Accept','Reject'):
                        valid = 1
                else:
                    if x.action in ('Accept','Reject'):
                        valid = 0
                    else:
                        valid = 1
            x.valid_user = valid
    
    def accept(self):
        self.write({'action': 'Accept','date':fields.Datetime.now()})
        mail_server=self.env['ir.mail_server'].sudo().search([],limit=1)
        if self.po_id and self.sequence==1:
            next_approver=self.search([('action','!=','Accept'),('po_id','=',self.po_id.id)],order='sequence asc',limit=1)
            if next_approver:
                ctx = {}
                if mail_server:
                    ctx['email_from']=mail_server.smtp_user
                else:
                    ctx['email_from']=self.po_id.user_id.login
                email_list = [approver.user_id.login for approver in next_approver]
                if email_list:
                    ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                    ctx['approver_name']=self.user_id.name
                    template = self.env.ref('dynamic_approvers.po_next_approval_email_template')
                    template.with_context(ctx).sudo().send_mail(self.po_id.id, force_send=True, raise_exception=False)
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.po_id.user_id.login
            email_list = [self.po_id.user_id.login]
            if email_list:
                ctx['notification_to_initiator'] = ','.join([email for email in email_list if email])
                ctx['approver_name']=self.user_id.name
                template = self.env.ref('dynamic_approvers.po_approval_email_to_initiator_template')
                template.with_context(ctx).sudo().send_mail(self.po_id.id, force_send=True, raise_exception=False)
            remaining_approval=self.env['document.approver.detail'].sudo().search([('action','!=','Accept'),('po_id','=',self.po_id.id)],order='sequence asc')
            if not remaining_approval:
                self.po_id.write({'state':'purchase'})
        elif self.po_id and self.sequence!=1:
            next_approver=self.search([('action','!=','Accept'),('po_id','=',self.po_id.id)],order='sequence asc',limit=1)
            if next_approver:
                ctx = {}
                if mail_server:
                    ctx['email_from']=mail_server.smtp_user
                else:
                    ctx['email_from']=self.po_id.user_id.login
                email_list = [approver.user_id.login for approver in next_approver]
                if email_list:
                    ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                    ctx['approver_name']=self.user_id.name
                    template = self.env.ref('dynamic_approvers.po_next_approval_email_template')
                    template.with_context(ctx).sudo().send_mail(self.po_id.id, force_send=True, raise_exception=False)
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.po_id.user_id.login
            email_list = [self.po_id.user_id.login]
            if email_list:
                ctx['notification_to_initiator'] = ','.join([email for email in email_list if email])
                ctx['approver_name']=self.user_id.name
                template = self.env.ref('dynamic_approvers.po_approval_email_to_initiator_template')
                template.with_context(ctx).sudo().send_mail(self.po_id.id, force_send=True, raise_exception=False)
            self.write({'action': 'Accept','date':fields.Datetime.now()})
            remaining_approval=self.env['document.approver.detail'].sudo().search([('action','!=','Accept'),('po_id','=',self.po_id.id)],order='sequence asc')
            if not remaining_approval:
                self.po_id.write({'state':'purchase'})
        elif self.pr_id and self.sequence==1:
            next_approver=self.search([('action','!=','Accept'),('pr_id','=',self.pr_id.id)],order='sequence asc',limit=1)
            if next_approver:
                ctx = {}
                if mail_server:
                    ctx['email_from']=mail_server.smtp_user
                else:
                    ctx['email_from']=self.pr_id.requested_by.login
                email_list = [approver.user_id.login for approver in next_approver]
                if email_list:
                    ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                    ctx['approver_name']=self.user_id.name
                    template = self.env.ref('dynamic_approvers.pr_next_approval_email_template')
                    template.with_context(ctx).sudo().send_mail(self.pr_id.id, force_send=True, raise_exception=False)
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.pr_id.requested_by.login
            email_list = [self.pr_id.requested_by.login]
            if email_list:
                ctx['notification_to_initiator'] = ','.join([email for email in email_list if email])
                ctx['approver_name']=self.user_id.name
                template = self.env.ref('dynamic_approvers.pr_approval_email_to_initiator_template')
                template.with_context(ctx).sudo().send_mail(self.pr_id.id, force_send=True, raise_exception=False)
            remaining_approval=self.env['document.approver.detail'].sudo().search([('action','!=','Accept'),('po_id','=',self.po_id.id)],order='sequence asc')
            if not remaining_approval:
                self.pr_id.write({'state':'approved'})
        elif self.pr_id and self.sequence!=1:
            next_approver=self.search([('action','!=','Accept'),('pr_id','=',self.pr_id.id)],order='sequence asc',limit=1)
            if next_approver:
                ctx = {}
                if mail_server:
                    ctx['email_from']=mail_server.smtp_user
                else:
                    ctx['email_from']=self.pr_id.user_id.login
                email_list = [approver.user_id.login for approver in next_approver]
                if email_list:
                    ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                    ctx['approver_name']=self.user_id.name
                    template = self.env.ref('dynamic_approvers.pr_next_approval_email_template')
                    template.with_context(ctx).sudo().send_mail(self.pr_id.id, force_send=True, raise_exception=False)
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.pr_id.requested_by.login
            email_list = [self.pr_id.requested_by.login]
            if email_list:
                ctx['notification_to_initiator'] = ','.join([email for email in email_list if email])
                ctx['approver_name']=self.user_id.name
                template = self.env.ref('dynamic_approvers.pr_approval_email_to_initiator_template')
                template.with_context(ctx).sudo().send_mail(self.pr_id.id, force_send=True, raise_exception=False)
            self.write({'action': 'Accept','date':fields.Datetime.now()})
            remaining_approval=self.env['document.approver.detail'].sudo().search([('action','!=','Accept'),('pr_id','=',self.pr_id.id)],order='sequence asc')
            if not remaining_approval:
                self.pr_id.write({'state':'approved'})
                
                
        elif self.loan_id and self.sequence==1:
            next_approver=self.search([('action','!=','Accept'),('loan_id','=',self.loan_id.id)],order='sequence asc',limit=1)
            if next_approver:
                ctx = {}
                if mail_server:
                    ctx['email_from']=mail_server.smtp_user
                else:
                    ctx['email_from']=self.loan_id.employee_id.user_id.login
                email_list = [approver.user_id.login for approver in next_approver]
                if email_list:
                    ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                    ctx['approver_name']=self.user_id.name
                    template = self.env.ref('dynamic_approvers.hr_loan_next_approval_email_template')
                    template.with_context(ctx).sudo().send_mail(self.loan_id.id, force_send=True, raise_exception=False)
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.loan_id.submitted_by.login
            email_list = [self.loan_id.employee_id.user_id.login]
            if email_list:
                ctx['notification_to_initiator'] = ','.join([email for email in email_list if email])
                ctx['approver_name']=self.user_id.name
                template = self.env.ref('dynamic_approvers.hr_loan_approval_email_to_initiator_template')
                template.with_context(ctx).sudo().send_mail(self.loan_id.id, force_send=True, raise_exception=False)
            remaining_approval=self.env['document.approver.detail'].sudo().search([('action','!=','Accept'),('loan_id','=',self.loan_id.id)],order='sequence asc')
            if not remaining_approval:
                self.loan_id.write({'state':'Approved'})
                self.loan_id.create_installments()
        elif self.loan_id and self.sequence!=1:
            next_approver=self.search([('action','!=','Accept'),('loan_id','=',self.loan_id.id)],order='sequence asc',limit=1)
            if next_approver:
                ctx = {}
                if mail_server:
                    ctx['email_from']=mail_server.smtp_user
                else:
                    ctx['email_from']=self.loan_id.employee_id.user_id.login
                email_list = [approver.user_id.login for approver in next_approver]
                if email_list:
                    ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                    ctx['approver_name']=self.user_id.name
                    template = self.env.ref('dynamic_approvers.hr_loan_next_approval_email_template')
                    template.with_context(ctx).sudo().send_mail(self.loan_id.id, force_send=True, raise_exception=False)
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.loan_id.employee_id.user_id.login
            email_list = [self.loan_id.employee_id.user_id.login]
            if email_list:
                ctx['notification_to_initiator'] = ','.join([email for email in email_list if email])
                ctx['approver_name']=self.user_id.name
                template = self.env.ref('dynamic_approvers.hr_loan_approval_email_to_initiator_template')
                template.with_context(ctx).sudo().send_mail(self.loan_id.id, force_send=True, raise_exception=False)
            self.write({'action': 'Accept','date':fields.Datetime.now()})
            remaining_approval=self.env['document.approver.detail'].sudo().search([('action','!=','Accept'),('loan_id','=',self.loan_id.id)],order='sequence asc')
            if not remaining_approval:
                self.loan_id.write({'state':'Approved'})
    def reject(self,comments):
        self.write({'action': 'Reject','date':fields.Datetime.now(),'comment':comments})
        mail_server=self.env['ir.mail_server'].sudo().search([],limit=1)
        if self.po_id:
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.po_id.user_id.login
            email_list = [self.user_id.login]
            email_list.append(self.po_id.user_id.login)
            if email_list:
                ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                ctx['rejected_by'] = self.user_id.name
                ctx['rejection_reason'] = self.comment
                
                template = self.env.ref('dynamic_approvers.pr_approval_reject_email_template')
                template.with_context(ctx).sudo().send_mail(self.po_id.id, force_send=True, raise_exception=False)
            self.po_id.button_cancel()
        elif self.pr_id:
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.pr_id.requested_by.login
            email_list = [self.user_id.login]
            email_list.append(self.pr_id.requested_by.login)
            if email_list:
                ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                ctx['rejected_by'] = self.user_id.name
                ctx['rejection_reason'] = self.comment
                
                template = self.env.ref('dynamic_approvers.pr_approval_reject_email_template')
                template.with_context(ctx).sudo().send_mail(self.pr_id.id, force_send=True, raise_exception=False)
            self.pr_id.button_rejected()
        
        elif self.loan_id:
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.loan_id.employee_id.user_id.login
            email_list = [self.user_id.login]
            email_list.append(self.loan_id.employee_id.user_id.login)
            if email_list:
                ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                ctx['rejected_by'] = self.user_id.name
                ctx['rejection_reason'] = self.comment
                
                template = self.env.ref('dynamic_approvers.hr_loan_approval_reject_email_template')
                template.with_context(ctx).sudo().send_mail(self.loan_id.id, force_send=True, raise_exception=False)
            self.loan_id.set_rejected()
