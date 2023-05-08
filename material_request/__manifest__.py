# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Material Request",
    "author": "Ali Akbar",
    "version": "14.0.1",
    "summary": "Use this module to create material request of "
    "and keep track of such "
    "requests.",
    "website": "",
    "category": "Material Request",
    "depends": ['base','stock'],
    "data": [
        "security/material_request.xml",
        "security/ir.model.access.csv",
        "data/material_request_sequence.xml",
        "data/mr_approval_email_template.xml",
#         "data/purchase_request_data.xml",
#         "reports/report_purchase_request.xml",
#         "wizard/purchase_request_line_make_purchase_order_view.xml",
        "views/material_request_view.xml",
#         "views/purchase_request_line_view.xml",
#         "views/purchase_request_report.xml",
#         "views/product_template.xml",
#         "views/purchase_order_view.xml",
#         "views/stock_move_views.xml",
#         "views/stock_picking_views.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
