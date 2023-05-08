# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

# class HrEmployee(models.Model):
#     _inherit='hr.employee'
#     destination_location_id=fields.Many2one('stock.location','Destination Location')
# 
# class HrDepartment(models.Model):
#     _inherit='hr.employee'
#     destination_location_id=fields.Many2one('stock.location','Destination Location')
class ApprovalRejectionWizard(models.TransientModel):
    _name='approval.rejection.wizard'
    request_id=fields.Many2one('material.request','Material Request')
    rejection_comments=fields.Text('Rejection Comments')
    
    def reject(self):
        self.request_id.reject_request(self.rejection_comments)
class MaterialRequest(models.Model):

    _name = "material.request"
    _description = "Material Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _department_get(self):
        return self.env["hr.employee"].search([('user_id','=',self.env.uid)]).department_id.id

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("material.request")

    name = fields.Char(string="Request Reference",required=True,default=lambda self: _("New"))
    requested_by = fields.Many2one("res.users",string="Requested by",required=True,tracking=True,default=_get_default_requested_by,)
    description = fields.Text(string="Description")
    department_id = fields.Many2one("hr.department",string="Department",required=True,default=_department_get,tracking=True,)
    company_id = fields.Many2one("res.company",string="Company",required=True,default=_company_get,tracking=True,)
    line_ids = fields.One2many("material.request.line","request_id",string="Request Lines",tracking=True)
    state = fields.Selection([("draft", "Draft"),("submit", "Waiting Department Approval"),('validated','Waiting IR Approval'),("approved", "Approved"),("requested_stock", "Requested Stock"),("received",'Received'),("rejected",'Rejected')],string="Status",tracking=True,required=True,default="draft")
    request_date=fields.Date('Requisition Date',default=lambda  self:fields.Datetime.now())
    received_date=fields.Date('Received Date')
    deadline=fields.Date('Deadline')
    stock_picking_id=fields.Many2one('stock.picking','Stock Picking')
    submit_by=fields.Many2one('res.users','Submitted By')
    submit_at=fields.Date('Submission Date')
    validate_by=fields.Many2one('res.users','Department Appoval By')
    validate_at=fields.Date('Department Approval Date')
    approved_by=fields.Many2one('res.users','Approved By')
    approved_at=fields.Date('Approval Date')
    reject_by=fields.Many2one('res.users','Rejected By')
    rejected_at=fields.Date('Rejection Date')
    rejection_comments=fields.Text('Rejection Comments')
    
    def submit_request(self):
        self.write({'state':'submit',
                    'submit_by':self.env.user.id,
                    'submit_at':fields.Datetime.now(),})
        mail_server=self.env['ir.mail_server'].sudo().search([],limit=1)
        department_approver=self.env.ref('material_request.group_material_request_department_approver').users
        if department_approver:
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.requested_by.login
            email_list = [approver.login for approver in department_approver]
            if email_list:
                ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                ctx['approver_name']=self.env.user.name
                template = self.env.ref('material_request.mr_department_approval_email_template')
                template.with_context(ctx).sudo().send_mail(self.id, force_send=True, raise_exception=False)

    def validate_request(self):
        if self.env.user.has_group('material_request.group_material_request_department_approver') or self.env.user.has_group('base.group_erp_manager'):
            self.write({'state':'validated',
                    'validate_by':self.env.user.id,
                    'validate_at':fields.Datetime.now()})
            mail_server=self.env['ir.mail_server'].sudo().search([],limit=1)
            mr_approver=self.env.ref('material_request.group_material_request_manager').users
            if mr_approver:
                ctx = {}
                if mail_server:
                    ctx['email_from']=mail_server.smtp_user
                else:
                    ctx['email_from']=self.requested_by.login
                email_list = [approver.login for approver in mr_approver]
                if email_list:
                    ctx['notification_to_approvers'] = ','.join([email for email in email_list if email])
                    ctx['approver_name']=self.env.user.name
                    template = self.env.ref('material_request.mr_manager_email_template')
                    template.with_context(ctx).sudo().send_mail(self.id, force_send=True, raise_exception=False)
                ctx = {}
                if mail_server:
                    ctx['email_from']=mail_server.smtp_user
                else:
                    ctx['email_from']=self.requested_by.login
                email_list = [self.requested_by.login]
                if email_list:
                    ctx['notification_to_initiator'] = ','.join([email for email in email_list if email])
                    ctx['approver_name']=self.env.user.name
                    template = self.env.ref('material_request.mr_approval_email_to_initiator_template')
                    template.with_context(ctx).sudo().send_mail(self.id, force_send=True, raise_exception=False)
    def approve_request(self):
        if self.env.user.has_group('material_request.group_material_request_manager') or self.env.user.has_group('base.group_erp_manager'):
            self.write({'state':'approved',
                    'approved_by':self.env.user.id,
                    'approved_at':fields.Datetime.now()})
            mail_server=self.env['ir.mail_server'].sudo().search([],limit=1)
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.requested_by.login
            email_list = [self.requested_by.login]
            if email_list:
                ctx['notification_to_initiator'] = ','.join([email for email in email_list if email])
                ctx['approver_name']=self.env.user.name
                template = self.env.ref('material_request.mr_approval_email_to_initiator_template')
                template.with_context(ctx).sudo().send_mail(self.id, force_send=True, raise_exception=False)
            stock_manager_group=self.env.ref('stock.group_stock_manager').users
            stock_user_group=self.env.ref('stock.group_stock_user').users
            stock_users=set(stock_manager_group+stock_user_group)
            if stock_users:
                ctx = {}
                if mail_server:
                    ctx['email_from']=mail_server.smtp_user
                else:
                    ctx['email_from']=self.requested_by.login
                email_list = [user.login for user in stock_users]
                if email_list:
                    ctx['notification_to_stock_users'] = ','.join([email for email in email_list if email])
                    ctx['approver_name']=self.env.user.name
                    template = self.env.ref('material_request.mr_create_transfer_email_template')
                    template.with_context(ctx).sudo().send_mail(self.id, force_send=True, raise_exception=False)
    
    def reject_request(self,comments):
        if self.env.user.has_group('material_request.group_material_request_department_approver') or self.env.user.has_group('product.group_material_request_manager') or self.env.user.has_group('base.group_erp_manager'): 
            self.write({'state':'rejected',
                    'reject_by':self.env.user.id,
                    'rejected_at':fields.Datetime.now()
                    ,'rejection_comments':comments})
            mail_server=self.env['ir.mail_server'].sudo().search([],limit=1)
            ctx = {}
            if mail_server:
                ctx['email_from']=mail_server.smtp_user
            else:
                ctx['email_from']=self.requested_by.login
            email_list = [self.requested_by.login]
            if email_list:
                ctx['notification_to_initiator'] = ','.join([email for email in email_list if email])
                ctx['rejected_by']=self.env.user.name
                ctx['rejection_reason'] = comments
                template = self.env.ref('material_request.mr_approval_reject_email_template')
                template.with_context(ctx).sudo().send_mail(self.id, force_send=True, raise_exception=False)
    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._get_default_name()
        request = super(MaterialRequest, self).create(vals)
        return request

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a material request which is not draft.")
                )
        return super(MaterialRequest, self).unlink()

class MaterialRequestLine(models.Model):

    _name = "material.request.line"
    name = fields.Char(string="Description", tracking=True,related='product_id.name')
    product_id = fields.Many2one("product.product",string="Product",tracking=True)
    product_uom_id = fields.Many2one("uom.uom",string="UoM",tracking=True,related='product_id.uom_id')
    product_qty = fields.Float(string="Quantity", tracking=True, digits="Product Unit of Measure")
    request_id = fields.Many2one("material.request",string="Material Request",ondelete="cascade",readonly=True,)
    company_id = fields.Many2one("res.company",related="request_id.company_id",string="Company",store=True,)
    description = fields.Text(related="request_id.description",string="PR Description",store=True,readonly=False,)
    remarks=fields.Char(string='Remarks')

class StockPickingWizard(models.Model):
    _name='stock.picking.create.wizard'

    company_id=fields.Many2one('res.company','Company')
    request_id=fields.Many2one('material.request','Material Request')
    picking_type_id=fields.Many2one('stock.picking.type','Operation Type',required=True,domain="[('company_id','=',company_id)]")
    source_location_id=fields.Many2one('stock.location','Source Location',required=True,domain="[('company_id','=',company_id)]")
    destination_location_id=fields.Many2one('stock.location','Destination Location',required=True,domain="[('company_id','=',company_id)]")
    
    def create_stock_request (self):
        picking_lines = []
        for each in self.request_id.line_ids:
            picking_lines.append((0,0,
                {
                    'name': 'internal transfer',
                    'location_id': self.source_location_id.id,
                    'location_dest_id': self.destination_location_id.id,
                    'product_id': each.product_id.id,
                    'product_uom': each.product_uom_id.id,
                    'product_uom_qty': each.product_qty,
                })
                )
        picking_obj = self.env['stock.picking'].create({
                        'partner_id': self.request_id.requested_by.partner_id.id,
                        'picking_type_id': self.picking_type_id.id,
                        'location_id': self.source_location_id.id,
                        'location_dest_id': self.destination_location_id.id,
                        'material_request_id':self.request_id.id,
                        'origin':self.request_id.name,
#                         'ship_to':self.request_id.requested_by.partner_id.id,
                        'move_ids_without_package':picking_lines
                    })
        self.request_id.write({'state':'requested_stock',
                             'stock_picking_id':picking_obj.id,})
        
class StockPicking(models.Model):
    _inherit='stock.picking'
    material_request_id=fields.Many2one('material.request','Material Request')
    
    
    def button_validate(self):
        if self.material_request_id:
            self.material_request_id.write({'state':'received',
                                            'received_date':fields.Datetime.now()})
        return super(StockPicking,self).button_validate()