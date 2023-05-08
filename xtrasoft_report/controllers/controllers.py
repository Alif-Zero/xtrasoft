# -*- coding: utf-8 -*-
# from odoo import http


# class XtrasoftReport(http.Controller):
#     @http.route('/xtrasoft_report/xtrasoft_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/xtrasoft_report/xtrasoft_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('xtrasoft_report.listing', {
#             'root': '/xtrasoft_report/xtrasoft_report',
#             'objects': http.request.env['xtrasoft_report.xtrasoft_report'].search([]),
#         })

#     @http.route('/xtrasoft_report/xtrasoft_report/objects/<model("xtrasoft_report.xtrasoft_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('xtrasoft_report.object', {
#             'object': obj
#         })
