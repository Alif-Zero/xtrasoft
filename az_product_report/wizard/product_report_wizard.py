# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductReportWizard(models.TransientModel):
    _name = 'product.report.wizard'
    _description = 'Product Report wizard'

    search_by = fields.Selection([
        ('product','Product'),
        ('category','Category'),
        ], default='category')
    company = fields.Many2many('res.company', default=lambda self: self.env.user.company_id, string="Company")
    warehouse = fields.Many2many('stock.warehouse', string="Warehouse")
    product_ids = fields.Many2many('product.product')
    category_ids = fields.Many2many('product.category')
    
    def print_report(self):
        company_id = []
        warehouse_id = []

        if self.company:
            for val in self.company:
                company_id.append(val.id)
        else:
            company = self.env['res.company'].search([])
            for val in company:
                company_id.append(val.id)

        if self.warehouse:
            for val in self.warehouse:
                warehouse_id.append(val.id)
        else:
            warehouse = self.env['stock.warehouse'].search([])
            for val in warehouse:
                warehouse_id.append(val.id)

        data = {
            'company': company_id, 
            'search_by': self.search_by,
            'product_ids': self.product_ids.ids,
            'category_ids': self.category_ids.ids,
            }

        return self.env.ref('az_product_report.product_move_pdf_report').report_action(self, data=data)
