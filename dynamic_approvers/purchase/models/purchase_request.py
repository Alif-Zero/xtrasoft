from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import tools
from lxml import etree
from odoo.tools.safe_eval import safe_eval
from ... import generic as gen
from num2words import num2words


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"  
        
    def adjust_approval_seq(self):
        previous = ''
        current = ''
        for x in self.approver_ids:
            if x.user_id:
                if current:
                    previous = current
                current = x.id 
                if previous:
                    x.previous_approval = previous 
    
    def _get_approvers(self):
        data = []
        result = self.env['document.approver'].search([('document_type','=','Purchase Request')], order="sequence")
        if result:
            for x in result:
                user_id = False
                authority = ''
#                 if x.user2_id:
#                     user_id = x.user2_id.id or ''
#                     authority = x.authority2 or ''
#                 else:
                user_id = x.user_id.id or ''
                authority = x.authority or ''
                
                data.append((0,0,dict(
                    name = x.user_id.name,
                    sequence = x.sequence,
                    document_type = 'Purchase Request',
                    user_id= user_id, 
                    authority = authority,
                    action_taken_as = x.action_taken_as
                    )))
            
        return data
    approver_ids = fields.One2many('document.approver.detail', 'pr_id')
    
    def button_to_approve(self):
        approver=self._get_approvers()
        self.approver_ids=approver
        ctx = {}
        mail_server=self.env['ir.mail_server'].sudo().search([],limit=1)
        if mail_server:
            ctx['email_from']=mail_server.smtp_user
        else:
            ctx['email_from']=self.po_id.user_id.login
        
        first_approver=self.approver_ids.search([],order='sequence asc',limit=1)
        email_list = [approver.user_id.login for approver in first_approver]
        if email_list:
            ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
            template = self.env.ref('dynamic_approvers.pr_initial_approval_email_template')
            template.with_context(ctx).sudo().send_mail(self.id, force_send=True, raise_exception=False)
        if self.approver_ids:
            self.adjust_approval_seq()
        return super(PurchaseRequest, self).button_to_approve()