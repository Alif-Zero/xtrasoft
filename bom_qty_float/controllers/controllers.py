# -*- coding: utf-8 -*-
# from odoo import http


# class BomQtyFloat(http.Controller):
#     @http.route('/bom_qty_float/bom_qty_float/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bom_qty_float/bom_qty_float/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bom_qty_float.listing', {
#             'root': '/bom_qty_float/bom_qty_float',
#             'objects': http.request.env['bom_qty_float.bom_qty_float'].search([]),
#         })

#     @http.route('/bom_qty_float/bom_qty_float/objects/<model("bom_qty_float.bom_qty_float"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bom_qty_float.object', {
#             'object': obj
#         })
