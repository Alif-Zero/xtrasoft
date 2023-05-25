from  odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError


class ContractApprovalWizard(models.TransientModel):
    _name = 'contract.approval.wizard'

    contract_ids = fields.Many2many('hr.contract', string="Contracts")
    state = fields.Selection([
        ('waiting_for_approval_1','Finance'),
        ('waiting_for_approval_2','CEO Approval'),
    ])
    def action_appove(self):
        model_id = self.env['ir.model'].search([('model', '=', 'hr.contract')], limit=1).id
        activty_type = self.env.ref('odoo_hr.advance_laon_activity').id
        user_id = self.env.user.id
        for rec in self.contract_ids:
            if rec.state2 == 'waiting_for_approval_1' and self.state == 'waiting_for_approval_1':
                rec.submit_for_approval_2()
                activities = self.env['mail.activity'].search([
                    ('res_id','in', rec.ids),
                    ('res_model_id', '=', model_id),
                    ('activity_type_id', '=', activty_type),
                    ('user_id', '=', user_id),
                    
                    ])
                activities.action_done()
            elif rec.state2 == 'waiting_for_approval_2' and self.state == 'waiting_for_approval_2':
                rec.approved()
                activities = self.env['mail.activity'].search([
                    ('res_id','in', rec.ids),
                    ('res_model_id', '=', model_id),
                    ('activity_type_id', '=', activty_type),
                    ('user_id', '=', user_id),
                    
                    ])
                activities.action_done()
    
    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)

        model = self.env.context.get('active_model')
        if not model == 'hr.contract':
            return
        state = self.env.context.get('contract_state2')
        if not state:
            return
        if state == 'waiting_for_approval_1' and not self.env.user.has_group('contract_approvals.group_contract_approval_1'):
            raise ValidationError(_("Finance user can perform this action."))
        if state == 'waiting_for_approval_1' and not self.env.user.has_group('contract_approvals.group_contract_approval_2'):
            raise ValidationError(_("Finance user can perform this action."))
        ids = self.env.context.get('active_ids')

        contract_ids = self.env['hr.contract'].sudo().search([
            ('id' ,'in', ids),
            ('state2', '=', state)
            ]
        )
        result['contract_ids'] = [(6,0,contract_ids.ids)]
        result['state'] = state

        return result