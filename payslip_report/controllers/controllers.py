# -*- coding: utf-8 -*-
# from odoo import http


# class PayslipReport(http.Controller):
#     @http.route('/payslip_report/payslip_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payslip_report/payslip_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payslip_report.listing', {
#             'root': '/payslip_report/payslip_report',
#             'objects': http.request.env['payslip_report.payslip_report'].search([]),
#         })

#     @http.route('/payslip_report/payslip_report/objects/<model("payslip_report.payslip_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payslip_report.object', {
#             'object': obj
#         })
