# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, exceptions

#
# class PurchaseReportBill(models.AbstractModel):
#     _name = 'report.mew_reports.report_bill_button'
#
#     def _get_report_values(self, docids, data=None):
#         # get the report action back as we will need its data
#         report = self.env['ir.actions.report']._get_report_from_name('mew_reports.report_bill_button')
#         # get the records selected for this rendering of the report
#         obj = self.env[report.model].browse(docids)
#         # return a custom rendering context
#         return {
#             'lines': docids.get_lines()}
