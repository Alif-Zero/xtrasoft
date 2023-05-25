from odoo import models, api, fields, _ 

MONTH = [
    ('1','Jan'),
    ('2','Feb'),
    ('3','Mar'),
    ('4','Apr'),
    ('5','May'),
    ('6','Jun'),
    ('7','Jul'),
    ('8','Aug'),
    ('9','Sep'),
    ('10','Oct'),
    ('11','Nov'),
    ('12','Dec'),
]
DATE = [
    ('1','1'),
    ('2','2'),
    ('3','3'),
    ('4','4'),
    ('5','5'),
    ('6','6'),
    ('7','7'),
    ('8','8'),
    ('9','9'),
    ('10','10'),
    ('11','11'),
    ('12','12'),
    ('13','13'),
    ('14','14'),
    ('15','15'),
    ('16','16'),
    ('17','17'),
    ('18','18'),
    ('19','19'),
    ('20','20'),
    ('21','21'),
    ('22','22'),
    ('23','23'),
    ('24','24'),
    ('25','25'),
    ('26','26'),
    ('27','27'),
    ('28','28'),
    ('29','29'),
    ('30','30'),
    ('31','31'),
]
class PayslipPeriod(models.Model):
    _name = 'payslip.period'

    name = fields.Char()
    day_from = fields.Selection(DATE,string="Day From")
    month_from = fields.Selection(MONTH, string="Month From")
    day_to = fields.Selection(DATE,string="Day To")
    month_to = fields.Selection(MONTH, string="Month To")

    @api.onchange('day_from','month_from','day_to','month_to')
    def onchange_get_name(self):
        for rec in self:
            month_from = dict(self._fields['month_from'].selection).get(self.month_from)
            month_to = dict(self._fields['month_to'].selection).get(self.month_to)
            rec.name = "{} {} - {} {}".format(rec.day_from,month_from, rec.day_to, month_to)