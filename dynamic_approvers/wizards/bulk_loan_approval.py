from  odoo import models, fields, api, _ 


class LoanApprovalWizard(models.TransientModel):
    _name = 'loan.approval.wizard'

    loan_approval_ids = fields.Many2many('document.approver.detail', string="Loan Request")
    def loan_appove(self):
        model_id = self.env['ir.model'].search([('model', '=', 'hr.loan')], limit=1).id
        activty_type = self.env.ref('odoo_hr.advance_laon_activity').id
        for rec in self.loan_approval_ids:
            rec.accept()
            user_id = rec.user_id.id
            activities = self.env['mail.activity'].search([
                ('res_id','in', rec.loan_id.ids),
                ('res_model_id', '=', model_id),
                ('activity_type_id', '=', activty_type),
                ('user_id', '=', user_id),
                
                ])
            activities.action_done()
    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)

        model = self.env.context.get('active_model')
        if model == 'hr.loan':
            loan_ids = self.env.context.get('active_ids')
            loan_approval_ids = self.env['document.approver.detail'].sudo().search([
                ('loan_id' ,'in', loan_ids),
                ('loan_id.state' ,'=', 'Waiting Approval'),
                ('user_id', '=', self.env.user.id)
                ]
            )
            result['loan_approval_ids'] = [(6,0,loan_approval_ids.ids)]

        return result