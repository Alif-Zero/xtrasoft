from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import datetime as dt
from datetime import datetime
from datetime import datetime, date, time, timedelta
from datetime import date, datetime
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone

import datetime
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class logs_atendance_changes(models.Model):
    _name = 'attendance.logs.changes'

    timestamp = fields.Datetime(string='Timestamp', required=True, index=True)
    date=fields.Date(string="Attendance Date")
    responsible=fields.Many2one('res.users',string="Modifier",required=1)
    manager=fields.Many2one('res.users',string="Manager",required=1)


    att_cus = fields.Many2one('attendance.custom', ondelete='cascade')
    note = fields.Text(string="Note")


    def button_open_record(self):
        if self.att_cus:
            return {'type': 'ir.actions.act_window',
                    'res_model': 'attendance.custom',
                    'view_mode': 'form',
                    'res_id': self.att_cus.id,
                    'target': 'current',
                    }


    # @api.onchange('timestamp')
    # def onchng_timestamp(self):
    #     if self.timestamp:
    #         self.check = self.get_minute_hmformat(
    #             self.timestamp.second + (self.timestamp.hour * 60 * 60) + (self.timestamp.hour * 60))
    #         self.status = 'checkin'
    #         msg = _("changed the Check Ins %s") % str(self.env.user.name)
    #         self.att_cus.message_notify(subject="Check Ins changed", body=msg)
    #
    # def get_minute_hmformat(self, seconds):
    #     seconds = seconds % (24 * 3600)
    #     hour = seconds // 3600
    #     seconds %= 3600
    #     minutes = seconds // 60
    #     seconds %= 60
    #
    #     return "%d:%02d" % (hour + 3, minutes)


