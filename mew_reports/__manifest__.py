# -*- coding: utf-8 -*-
{
    'name': "mew_reports",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','purchase','contacts'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/bank_receipt.xml',
        'reports/report_journal_entries.xml',
        'reports/report_journal_entries_view.xml',
        # 'reports/report_menu.xml',
        'reports/report_purchase_order.xml',
        'reports/bill_report_template.xml',
        'reports/voucher_report_seq.xml',

    ],
    'demo': [
        'demo/demo.xml',
    ],
}
