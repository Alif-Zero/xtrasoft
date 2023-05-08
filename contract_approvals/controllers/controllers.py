# -*- coding: utf-8 -*-
# from odoo import http


# class ContractApprovals(http.Controller):
#     @http.route('/contract_approvals/contract_approvals/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contract_approvals/contract_approvals/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_approvals.listing', {
#             'root': '/contract_approvals/contract_approvals',
#             'objects': http.request.env['contract_approvals.contract_approvals'].search([]),
#         })

#     @http.route('/contract_approvals/contract_approvals/objects/<model("contract_approvals.contract_approvals"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_approvals.object', {
#             'object': obj
#         })
