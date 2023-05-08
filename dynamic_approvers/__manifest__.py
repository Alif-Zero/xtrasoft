# -*- coding: utf-8 -*-
{
    'name': "Dynamic Approvers",
    'shortdesc':'Dynamic-Approvers',
    'summary': """
        Approval Workflow""",

    'description': """
        Approval Workflow
    """,

    'author': "Ali Akbar",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Other',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','purchase_request','odoo_hr'],

    # always loaded
    'data': [
        'purchase/data/po_approval_email_template.xml',
        'purchase/data/pr_approval_email_template.xml',
        'purchase/data/hr_loan_approval_email_template.xml',
        'purchase/security/groups.xml',
        'purchase/security/ir.model.access.csv',
        'purchase/views/approvers_views.xml',
        'purchase/views/purchase_order_views.xml',
        'purchase/views/purchase_request_views.xml',  
        'purchase/views/hr_loan_views.xml',    
        
        
        
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
        
    ],
}