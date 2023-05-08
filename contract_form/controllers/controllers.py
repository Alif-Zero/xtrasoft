# -*- coding: utf-8 -*-
# from odoo import http


# class ContractForm(http.Controller):
#     @http.route('/contract_form/contract_form/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contract_form/contract_form/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_form.listing', {
#             'root': '/contract_form/contract_form',
#             'objects': http.request.env['contract_form.contract_form'].search([]),
#         })

#     @http.route('/contract_form/contract_form/objects/<model("contract_form.contract_form"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_form.object', {
#             'object': obj
#         })
