# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Contract(models.Model):
    _inherit = 'hr.contract'

    def action_open_salary_update_wizard(self):
        active_contract_ids = self.env['hr.contract'].sudo().browse(self._context['active_ids'])
        view = self.env.ref('basic_salary_quick_update.salary_update_wizard_form')
        view_id = view and view.id or False
        context = {'default_contract_ids': active_contract_ids.ids}
        return {
            'name': 'Salary Update',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'salary.update.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context}
