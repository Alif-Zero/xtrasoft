# -*- coding: utf-8 -*-
from num2words import num2words

from odoo import models, fields, api, _
class RegisterPaymentFieldabc(models.TransientModel):
    _inherit = 'account.payment.register'

    register_payment_check_number = fields.Char(string='Cheque # ')





class MewAccountInheritVoucher(models.Model):
    _inherit = 'account.payment'

    voucher_seq = fields.Char(string="Voucher Number", readonly=True, required=True, copy=False, )
    check_number_one_check_box = fields.Boolean()
    check_number_one = fields.Char(string='Cheque # ')


    @api.onchange('payment_type', 'journal_id')
    def _onchange_payment_type(self):
        for rec in self:
            if rec.journal_id.type == 'cash':
                rec.check_number_one_check_box = True
            if rec.journal_id.type == 'bank':
                rec.check_number_one_check_box = False

    @api.model
    def create(self, vals):
        record = super(MewAccountInheritVoucher, self).create(vals)
        journal_id = record.journal_id.id
        move_id = record.move_id.id
        journal_id_data = self.env['account.journal'].browse(journal_id)
        move_id_data = self.env['account.move'].browse(move_id)
        seq_number = self.env['ir.sequence'].next_by_code('self.voucher.seq') or ('New')

        if journal_id_data.type == 'cash' and record['payment_type'] == 'inbound':
            record['voucher_seq'] = 'CRV-' + seq_number
            move_id_data.write({
                'journal_voucher_seq': record['voucher_seq']
            })


        elif journal_id_data.type == 'cash' and record['payment_type'] == 'outbound':
            record['voucher_seq'] = 'CPV-' + seq_number
            move_id_data.write({
                'journal_voucher_seq': record['voucher_seq']
            })

        elif journal_id_data.type == 'bank' and record['payment_type'] == 'inbound':
            record['voucher_seq'] = 'BRV-' + seq_number
            move_id_data.write({
                'journal_voucher_seq': record['voucher_seq']
            })

        elif journal_id_data.type == 'bank' and record['payment_type'] == 'outbound':
            record['voucher_seq'] = 'BPV-' + seq_number
            move_id_data.write({
                'journal_voucher_seq': record['voucher_seq']
            })

        else:
            pass

        return record


class MewVoucherSeq(models.Model):
    _inherit = 'account.move'

    int_to_word = fields.Char(compute='_get_account_move_line_total')
    journal_voucher_seq = fields.Char(string="Voucher Number", required=True, copy=False, )

    purchase_voucher_seq = fields.Char(string="Voucher Number", )

    @api.model
    def create(self, vals):
        record = super(MewVoucherSeq, self).create(vals)
        record['purchase_voucher_seq'] = self.env['ir.sequence'].next_by_code('self.service.ref') or _('New')
        record['journal_voucher_seq'] = self.env['ir.sequence'].next_by_code('self.journal.ref.no') or _('New')
        if record['voucher_type'] == 'cash_receive':
            record['journal_voucher_seq'] = 'CRV-' + record['journal_voucher_seq']

        elif record['voucher_type'] == 'cash_send':
            record['journal_voucher_seq'] = 'CPV-' + record['journal_voucher_seq']

        elif record['voucher_type'] == 'bank_send':
            record['journal_voucher_seq'] = 'BPV-' + record['journal_voucher_seq']

        elif record['voucher_type'] == 'bank_receive':
            record['journal_voucher_seq'] = 'BRV-' + record['journal_voucher_seq']

        elif record['voucher_type'] == 'journal_voucher':
            record['journal_voucher_seq'] = 'JV-' + record['journal_voucher_seq']

        else:
            pass
        return record

    def _get_account_move_line_total(self):
        total_amount = num2words(self.amount_total).title()
        if total_amount:
            self.int_to_word = total_amount
        else:
            self.int_to_word = 'Null'


class MewResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    mew_ntn = fields.Char(string='NTN')
    mew_srb = fields.Char(string='SRB')
    mew_gst = fields.Char(string='GST')

class MewPurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    mew_cp = fields.Char(string='Contact Person')
    mew_cp_no = fields.Char(string='Contact Number')
