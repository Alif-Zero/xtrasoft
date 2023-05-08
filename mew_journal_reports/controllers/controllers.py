# -*- coding: utf-8 -*-
# from odoo import http


# class MewJournalReports(http.Controller):
#     @http.route('/mew_journal_reports/mew_journal_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mew_journal_reports/mew_journal_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mew_journal_reports.listing', {
#             'root': '/mew_journal_reports/mew_journal_reports',
#             'objects': http.request.env['mew_journal_reports.mew_journal_reports'].search([]),
#         })

#     @http.route('/mew_journal_reports/mew_journal_reports/objects/<model("mew_journal_reports.mew_journal_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mew_journal_reports.object', {
#             'object': obj
#         })
