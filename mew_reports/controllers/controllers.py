# -*- coding: utf-8 -*-
# from odoo import http


# class MewReports(http.Controller):
#     @http.route('/mew_reports/mew_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mew_reports/mew_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mew_reports.listing', {
#             'root': '/mew_reports/mew_reports',
#             'objects': http.request.env['mew_reports.mew_reports'].search([]),
#         })

#     @http.route('/mew_reports/mew_reports/objects/<model("mew_reports.mew_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mew_reports.object', {
#             'object': obj
#         })
