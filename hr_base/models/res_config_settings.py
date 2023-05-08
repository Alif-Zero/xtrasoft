# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expiry_notification_days = fields.Char(string="Expiry Notification Days",
                                           config_parameter="hr_base.expiry_notification_days")


class dialog_box_confirm(models.TransientModel):
    _name = 'confirm.dialog'

    name = fields.Char(
        default="Are you surer you want to confirm , After confirmation all the modification records for selected dates will be Validated!")
    
    
    def validate(self):
        return {'type': 'ir.actions.act_window_close'}

