# -*- coding: utf-8 -*-

from odoo import models, fields, api


class mewJournalreports(models.Model):
    _inherit = 'account.move'

    voucher_type = fields.Selection(
        string='Voucher type',
        selection=[('bank_receive', 'Bank Receipt Voucher'),
                   ('bank_send', 'Bank Payment Voucher'),
                   ('cash_receive', 'Cash Receipt Voucher'),
                   ('cash_send', 'Cash Payment Voucher'),
                   ('journal_voucher', 'Journal Voucher')],
        required=False,default="journal_voucher" )

    cheque_bank = fields.Char(
        string='Cheque',
        required=False)
