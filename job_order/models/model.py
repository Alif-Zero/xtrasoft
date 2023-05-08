# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import except_orm, ValidationError
import logging
from datetime import datetime
import math
import _sqlite3
from gevent.libev.corecext import NONE
_logger = logging.getLogger(__name__)

class JobOrder(models.Model):
    _name='job.order'
    _rec_name='container_no'
    cmb=fields.Float(string='Total CBM',required=True)
    total_cmb=fields.Float(string='Total CBM',compute='_cal_cbm')
    state=fields.Selection([('Draft','Draft'),('Confirmed','Confirmed'),('Invoiced','Invoiced'),('Receipt','Receipt')],default='Draft')
    line_ids=fields.One2many('job.order.line','order_id')
    container_no=fields.Char(string='Container Number')
    total_no_ctn=fields.Float('Total CTN Quantity',compute='_cal_total_no_ctn')
    total_ctn=fields.Float('Total CTN Quantity')
    total_weight=fields.Float('Total Weight',compute='_cal_total_weight')
    shipment_no=fields.Char('Shipment No.')
    type=fields.Selection([('Job Order','Job Order'),('Packing List','Packing List')],'Type')
    
    
    @api.constrains('cmb', 'total_cmb')
    def check_total_cbm(self):
        for each in self:
            if each.total_cmb and each.cmb:
                if each.total_cmb > each.cmb:
                    raise ValidationError('You are exceeding total limit of container. Kindly remove extra products.')
    
    @api.constrains('total_no_ctn', 'total_ctn')
    def check_total_ctn(self):
        for each in self:
            if each.total_no_ctn and each.total_ctn:
                if each.total_no_ctn > each.total_ctn:
                    raise ValidationError('You are exceeding total limit of container. Kindly remove extra products.')

    def SetToDraft(self):
        for line in self.env['account.move'].search([('order_id','=',self.id)]):
            line.unlink()
        self.state='Draft'
    @api.depends('line_ids')
    def _cal_cbm(self):
        for rec in self:
            total=0
            for line in rec.line_ids:
                total+=line.cbm
            rec.total_cmb=total

    @api.depends('line_ids')
    def _cal_total_weight(self):
        for rec in self:
            total=0
            rec.total_weight=0
            for line in rec.line_ids:
                for each in line.detail_ids:
                    total+=each.weight
            rec.total_weight=total
    @api.depends('line_ids')
    def _cal_total_no_ctn(self):
        for rec in self:
            total=0
            rec.total_no_ctn=0
            for line in rec.line_ids:
                total+=line.no_of_ctn
            rec.total_no_ctn=total

    def Confirmed(self):
        total=0
        if not self.line_ids:
            raise ValidationError('At least one order line required')

        for line in self.line_ids:
            total+=line.cbm
        if total>self.cmb:
            raise ValidationError('CBM limit Exceeds')
        self.state='Confirmed'

    def CreateInv(self):
        self.state='Invoiced'
        
        for line in self.line_ids:
            
            move_lines = [(5,0,0)]
            for detail_line in line.detail_ids:
                product_obj=self.env['product.product'].search([('product_tmpl_id','=',detail_line.product_id.id)],limit=1)
                line_vals_debit={'product_id': product_obj.id,
                                  'name': product_obj.name,
                                  'account_id': product_obj.property_account_income_id.id,
                                  'debit': detail_line.sub_total,
                                  'exclude_from_invoice_tab': True,
                                  'article': detail_line.article,
                                  'quantity': detail_line.no_of_ctn,
                                  'qty_per_ctn': detail_line.qty_per_ctn,
                                  'cbm': detail_line.cbm,
                                  'weight': detail_line.weight,
                                  'price_based': detail_line.price_based,
                                  'detail_id':detail_line.id,
                                  'product_uom_id': detail_line.uom_id.id,
#                                   'price_unit': detail_line.price,
                                  'price_subtotal':detail_line.sub_total
                                  }
                move_lines.append((0,0,line_vals_debit))
                line_vals_credit={'product_id': product_obj.id,
                                  'name': product_obj.name,
                                  'account_id': product_obj.property_account_expense_id.id,
                                  'credit': detail_line.sub_total,
                                  'exclude_from_invoice_tab': False,
                                  'article': detail_line.article,
                                  'quantity': detail_line.no_of_ctn,
                                  'qty_per_ctn': detail_line.qty_per_ctn,
                                  'cbm': detail_line.cbm,
                                  'weight': detail_line.weight,
                                  'price_based': detail_line.price_based,
                                  'detail_id':detail_line.id,
                                  'product_uom_id': detail_line.uom_id.id,
#                                   'price_unit': detail_line.price,
                                  'price_subtotal':detail_line.sub_total
                                  }
                move_lines.append((0,0,line_vals_credit))
            invoice_new = self.env['account.move'].create({'partner_id': line.partner_id.id,
                                                           'invoice_date': datetime.now(),
                                                           'move_type': 'out_invoice',
                                                           'invoice_origin': 'Job Order of '+str(self.container_no),
                                                           'order_id': self.id,
                                                           'container_no':self.container_no,
                                                           'line_ids':move_lines
                                                           })
#                 inv_line = self.env['account.move.line'].create([{'move_id': invoice_new.id, 'product_id': product_obj.id,
#                                                                   'name': product_obj.name,
#                                                                   'account_id': product_obj.property_account_income_id.id,
#                                                                   'debit': detail_line.sub_total,
#                                                                   'exclude_from_invoice_tab': True,
#                                                                   'article': detail_line.article,
#                                                                   'quantity': detail_line.no_of_ctn,
#                                                                   'qty_per_ctn': detail_line.qty_per_ctn,
#                                                                   'cbm': detail_line.cbm,
#                                                                   'weight': detail_line.weight,
#                                                                   'price_based': detail_line.price_based,
#                                                                   'detail_id':detail_line.id,
#                                                                   'product_uom_id': detail_line.uom_id.id,
#                                                                   'price_unit': detail_line.price,
#                                                                   'price_subtotal':detail_line.sub_total
#                                                                   },
#                                                                  {'move_id': invoice_new.id, 'product_id': product_obj.id,
#                                                                   'name': product_obj.name,
#                                                                   'account_id': product_obj.property_account_expense_id.id,
#                                                                   'credit': detail_line.sub_total,
#                                                                   'exclude_from_invoice_tab': False,
#                                                                   'article': detail_line.article,
#                                                                   'quantity': detail_line.no_of_ctn,
#                                                                   'qty_per_ctn': detail_line.qty_per_ctn,
#                                                                   'cbm': detail_line.cbm,
#                                                                   'weight': detail_line.weight,
#                                                                   'price_based': detail_line.price_based,
#                                                                   'detail_id':detail_line.id,
#                                                                   'product_uom_id': detail_line.uom_id.id,
#                                                                   'price_unit': detail_line.price,
#                                                                   'price_subtotal':detail_line.sub_total
#                                                                   }]
#                                                                 )
#                 move_lines.append((0,0,line_vals_credit))


class JobOrderLines(models.Model):
    _name = 'job.order.line'

    order_id=fields.Many2one('job.order')
    partner_id=fields.Many2one('res.partner')
    mark=fields.Char(related='partner_id.ref',string='P. Ship Mark')
    s_ship_mark=fields.Char(related='partner_id.s_ship_mark',string='S. Ship Mark',store=True)
    no_of_ctn=fields.Float(string='Total CTN',compute='cal_total_no_of_qty')
    total_qty=fields.Float(string='Total QTY/CTN',compute='_cal_qty')
    cbm=fields.Float(string='Total CBM',compute='_cal_total_cbm')
    detail_ids=fields.One2many('job.order.line.detail','line_id')
    description=fields.Char(string='Description')
    type=fields.Selection([('Job Order','Job Order'),('Packing List','Packing List')],'Type',related='order_id.type')
    @api.depends('detail_ids')
    def cal_total_no_of_qty(self):
        for each in self:
            total=0
            for line in each.detail_ids:
                total+=line.no_of_ctn
            each.no_of_ctn=total

    @api.depends('detail_ids')
    def _cal_total_cbm(self):
        for each in self:
            total=0
            for line in each.detail_ids:
                total+=line.cbm
            each.cbm=total

    @api.depends('detail_ids')
    def _cal_qty(self):
        for each in self:
            total=0
            for line in each.detail_ids:
                total+=line.qty_per_ctn
            each.total_qty=total

class JobOrderLinesDetails(models.Model):
    _name = 'job.order.line.detail'
    
    partner_id=fields.Many2one('res.partner','Partner',related='line_id.partner_id',store=True)
    ship_mark=fields.Char('P. Ship Mark',related='line_id.partner_id.ref',store=True)
    s_ship_mark=fields.Char(related='partner_id.s_ship_mark',string='S. Ship Mark',store=True)
    product_ids=fields.Many2many('product.template','Products',compute='_cal_valid_products')
    product_id=fields.Many2one('product.template',required=1,domain="[('id','in',product_ids)]")
    lot_id=fields.Many2one('stock.production.lot','Lot No.')
    on_hand_qty=fields.Float('On Hand QTY',compute='_cal_on_hand_qty')
    article=fields.Char('Article')
    no_of_ctn=fields.Float(string='CTN Qty',required=1)
    qty_per_ctn=fields.Float('Qty/CTN',required=1)
    uom_id=fields.Many2one('uom.uom',required=1)
    cbm=fields.Float(string='CBM')
    weight=fields.Float(string='Weight')
    price_based=fields.Selection([('CTN Qty','CTN Qty'),('Qty/CTN','Qty/CTN'),('CBM','CBM'),('Weight','Weight')],'Price Based On')
    price=fields.Float(string='Price')
    sub_total=fields.Float(string='Sub Total')
    line_id=fields.Many2one('job.order.line')
    job_order_id=fields.Many2one('job.order','Container No.',related='line_id.order_id',store=True)
    stock_receipt_date=fields.Datetime('Stock in Date',related='product_id.picking_id.date_done',store=True)
    type=fields.Selection([('Job Order','Job Order'),('Packing List','Packing List')],'Type',related='job_order_id.type')
    
    @api.onchange('product_id')
    def get_product_details(self):
        if self.product_id:
            self.article=self.product_id.article
            self.qty_per_ctn=self.product_id.qty_per_ctn
            self.uom_id=self.product_id.uom_id.id
            self.cbm=self.product_id.cbm
            self.weight=self.product_id.weight
            self.price=self.product_id.price
            stock_move_obj=self.env['stock.move'].search([('product_id.product_tmpl_id','=',self.product_id.id),('picking_id','=',self.product_id.picking_id.id)])
            if stock_move_obj:
                self.no_of_ctn=stock_move_obj.quantity_done
            else:
                self.no_of_ctn=0
        
    @api.onchange('product_id')
    def get_lot(self):
        res={}
        if self.product_id:
            lot_list=self.env['stock.production.lot'].search([('product_id.product_tmpl_id','=',self.product_id.id),('product_id.product_tmpl_id.product_owner_id','=',self.partner_id.id)]).ids
            if lot_list:
                res['domain']={'lot_id':[('id','in',lot_list)]}
                return res
            else:
                res['domain']={'lot_id':[('id','=',-1)]}
                return res
        else:
            res['domain']={'lot_id':[('id','=',-1)]}
            return res
        
    @api.depends('partner_id')
    def _cal_valid_products(self):
        for each in self:
            if each.partner_id:
                product_obj=self.env['product.template'].search([('product_owner_id','=',each.partner_id.id)]).ids
                if product_obj:
                    each.product_ids=product_obj
                else:
                    each.product_ids=None
            else:
                each.product_ids=None
    @api.depends('lot_id','product_id')
    def _cal_on_hand_qty(self):
        for each in self:
            if each.lot_id and each.product_id:
                each.on_hand_qty=each.lot_id.product_qty
            else:
                each.on_hand_qty=0
    @api.onchange('price_based','no_of_ctn','qty_per_ctn','cbm','weight','price')
    def _cal_sub_price(self):
        if self.price_based=='CTN Qty' and self.price:
            self.sub_total= (self.no_of_ctn*self.price)
        elif self.price_based=='Qty/CTN' and self.price and self.qty_per_ctn:
            self.sub_total= self.qty_per_ctn*self.no_of_ctn*self.price
        elif self.price_based=='CBM' and self.price:
            self.sub_total= (self.cbm*self.price)
        elif self.price_based=='Weight' and self.price:
            self.sub_total= (self.weight*self.price)
            

class InheritAccountMOve(models.Model):
    _inherit = 'account.move'

    order_id=fields.Many2one('job.order')
    container_no=fields.Char(string='Container Number')
    
class InheritAccountMove(models.Model):
    _inherit = 'account.move.line'

    detail_id=fields.Many2one('job.order.line.detail')
    cbm=fields.Float(string='CBM',related='detail_id.cbm')

    article=fields.Char('Article',related='detail_id.article')
    no_of_ctn=fields.Float(string='CTN Qty',related='detail_id.no_of_ctn')
    qty_per_ctn=fields.Float('Qty/CTN',related='detail_id.qty_per_ctn')
    weight=fields.Float(string='Weight',related='detail_id.weight')
    price_based=fields.Selection([('CTN Qty','CTN Qty'),('Qty/CTN','Qty/CTN'),('CBM','CBM'),('Weight','Weight')],'Price Based On',related='detail_id.price_based')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    
#     @api.depends('price_based','quantity','qty_per_ctn','cbm','weight','price_unit')
#     def _cal_sub_price(self):
#         for each in self:
#             if each.detail_id:
#                 each.price_unit=each.detail_id.price
#             else:
#                 each.price_unit=0
            
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    product_owner_id=fields.Many2one('res.partner','Prodcut Owner')
    article=fields.Char('Article')
    qty_per_ctn=fields.Float('Qty/CTN')
    weight=fields.Float(string='Weight')
    cbm=fields.Float(string='CBM')
    picking_id=fields.Many2one('stock.picking','Stock Picking')
class StockPicking(models.Model):
    _inherit='stock.picking'
    picking_partner_id=fields.Many2one('res.partner','Receive From',related='partner_id',store=True)
    ship_mark=fields.Char('P. Ship Mark',related='picking_partner_id.ref',store=True)
    s_ship_mark=fields.Char(related='picking_partner_id.s_ship_mark',string='S. Ship Mark',store=True)
    def button_validate(self):
        for each in self.move_ids_without_package:
            if each.picking_type_id.code == 'incoming':
                each.product_id.write({'product_owner_id':self.partner_id.id,
                                       'article':each.article,
                                       'qty_per_ctn':each.qty_per_ctn,
                                       'weight':each.weight,
                                       'cbm':each.cbm,
                                       'picking_id':self.id,})
            
        return super(StockPicking, self).button_validate()
    
class StockMove(models.Model):
    _inherit='stock.move'
    
    article=fields.Char('Article')
    qty_per_ctn=fields.Float('Qty/CTN')
    weight=fields.Float(string='Weight')
    cbm=fields.Float(string='CBM')
    total_qty=fields.Float('Total QTY',compute='_cal_total_qty',store=True)
    
    @api.depends('qty_per_ctn','quantity_done')
    def _cal_total_qty(self):
        for each in self:
            if each.qty_per_ctn and each.quantity_done:
                each.total_qty=(each.qty_per_ctn)*(each.quantity_done)
            else:
                each.total_qty=0.0
                
class StockMoveLine(models.Model):
    _inherit='stock.move.line'
    
    article=fields.Char('Article',related='move_id.article',store=True)
    qty_per_ctn=fields.Float('Qty/CTN',related='move_id.qty_per_ctn',store=True)
    weight=fields.Float(string='Weight',related='move_id.weight',store=True)
    cbm=fields.Float(string='CBM',related='move_id.cbm',store=True)
    total_qty=fields.Float('Total QTY',related='move_id.total_qty',store=True)
    picking_partner_id=fields.Many2one('res.partner','Receive From',related='picking_id.partner_id',store=True)
    picking_origin=fields.Char('Source Document',related='picking_id.origin',store=True)
    picking_type_id=fields.Many2one('stock.picking.type',related='picking_id.picking_type_id',store=True)
    ship_mark=fields.Char('P. Ship Mark',related='picking_partner_id.ref',store=True)
    s_ship_mark=fields.Char(related='picking_partner_id.s_ship_mark',string='S. Ship Mark',store=True)
    dest_location_id=fields.Many2one('stock.location',related='picking_id.location_dest_id',string='Warehouse',store=True)
    
class Partner(models.Model):
    _inherit='res.partner'
    s_ship_mark=fields.Char('S. Ship Mark')

class AccountMove(models.Model):
    _inherit='account.move'
    ship_mark=fields.Char('P. Ship Mark',related='partner_id.ref',store=True)
    s_ship_mark=fields.Char(related='partner_id.s_ship_mark',string='S. Ship Mark',store=True)