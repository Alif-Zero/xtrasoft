# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Web Basic',
    'category': 'Hidden',
    'version': '1.0',
    'sequence': 100,
    'description':
        """
Odoo Enterprise Web Client.
===========================

This module modifies the web addon to provide Enterprise design and responsiveness.
        """,
    'depends': ['web', 'base','web_enterprise'],
    'auto_install': True,
    'data': [
    ],
    'qweb': [
    ],
    'license': 'OEEL-1',
}
