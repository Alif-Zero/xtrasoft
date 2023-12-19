# -*- coding: utf-8 -*-
from datetime import timedelta, date

import dateutil.relativedelta
from dateutil.relativedelta import relativedelta

from odoo import models


class ProductMoveReport(models.AbstractModel):
    _name = "report.az_product_report.product_move_report_doc"
    _description = "Top selling products report"

    def _get_report_values(self, docids, data=None):
        
        company_id = data['company']
        search_by = data['search_by']
        product_ids = data['product_ids']
        category_ids = data['category_ids']
        from_date = date.today() - dateutil.relativedelta.relativedelta(years=100)
        to_date = date.today() + dateutil.relativedelta.relativedelta(days=1)

        domain = []
        if search_by == 'product':
            domain = [('id', 'in', product_ids)]
        elif search_by == 'category':
            domain = [('categ_id', 'in', category_ids)]

        product_ids = self.env['product.product'].search(domain)
        data = []
        for product in product_ids:
            sml = self.env['stock.move.line'].search([('product_id', '=', product.id)], order='date desc')
            if not sml:
                continue
            dic = {}
            stock_move = []
            total_in = 0
            total_out = 0
            for rec in sml:
                qty_in = 0
                qty_out = 0
                qty = rec.qty_done
                location_id = rec.location_id.display_name
                location_dest_id = rec.location_dest_id.display_name
                if rec.picking_code == 'outgoing':
                    qty_out = rec.qty_done
                    qty = 0
                    if rec.location_dest_id.usage == 'customer':
                        location_dest_id = rec.location_dest_id.name
                elif rec.picking_code == 'incoming':
                    qty = 0
                    qty_in = rec.qty_done
                    if rec.location_id.usage == 'supplier':
                        location_id = rec.location_id.name

                elif rec.picking_code == False:
                    if rec.location_dest_id.usage == 'inventory':
                        location_dest_id = rec.location_dest_id.name
                        qty_out = rec.qty_done
                        qty = 0
                    elif rec.location_id.usage == 'inventory':
                        location_id = rec.location_id.name
                        qty = 0
                        qty_in = rec.qty_done
                total_in += qty_in
                total_out += qty_out
                ml = {
                    'date': rec.date.date(),
                    'location_id': location_id,
                    'location_dest_id':location_dest_id,
                    'picking_id': rec.picking_id.name,
                    'partner_id': rec.picking_id.partner_id.name,
                    'qty_done': qty,
                    'qty_in': qty_in,
                    'qty_out': qty_out,
                    'picking_code':rec.picking_code,
                    'product_uom_id': rec.product_uom_id.name,
                }
                stock_move.append(ml)
            dic['product'] = {
                    'name': product.display_name,
                    'qty_hand': product.qty_available,
                    'uom_name': product.uom_name,
                    'qty_in': total_in,
                    'qty_out': total_out,
            }
            dic['sml'] = stock_move
            data.append(dic)
        # stock_move_line = self.env['stock.move.line'].read_group([],['product_id'])
        return {
            'data': data,
            'other': [],
        }
        other_details.update({

            'limit': limit_value,
            'least': 10,
            'range': date_selected,
            'date_selected_from': date_selected_from,
            'date_selected_to': date_selected_to,
        })

        cr = self._cr
        order = 'asc' if 10 else 'desc'
        company_id = str(tuple(company_id)) if len(company_id) > 1 else "(" + str(company_id[0]) + ")"
        warehouse_id = str(tuple(warehouse_id)) if len(warehouse_id) > 1 else "(" + str(warehouse_id[0]) + ")"
        limit_clause = " limit'%s'" % limit_value if limit_value else ""

        query = ("""select sl.name as product_name,sum(product_uom_qty),pu.name from sale_order_line sl 
                   JOIN sale_order so ON sl.order_id = so.id 
                   JOIN uom_uom pu on sl.product_uom = pu.id
                   where so.date_order::DATE >= '%s'::DATE and 
                   so.date_order::DATE <= '%s'::DATE and 
                   sl.state = 'sale' and so.company_id in %s 
                   and so.warehouse_id in %s
                   group by sl.name,pu.name order by sum %s""" % (
            from_date, to_date, company_id, warehouse_id, order)) + limit_clause
        cr.execute(query)
        dat = cr.dictfetchall()

        return {
            'data': dat,
            'other': other_details,
        }
