# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'


    def session_info(self):
        ICP = request.env['ir.config_parameter'].sudo()
        User = request.env['res.users']

        if User.has_group('base.group_system'):
            warn_enterprise = 'admin'
        elif User.has_group('base.group_user'):
            warn_enterprise = 'user'
        else:
            warn_enterprise = False

        result = super(Http, self).session_info()
        if warn_enterprise:
            import xmlrpc.client

            url = 'http://localhost:8069'
            db =  'theme_set'
            username = 'client_sub'
            password = '1aa07b1235907d8006c4eacdf2026c6bf974d2d7'

            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            common.version()
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            data = models.execute_kw(db, uid, password, 'client.subscription', 'search',[[['name','=','xtrasoft']]],{'limit': 1})
            data =  models.execute_kw(db, uid, password, 'client.subscription', 'read', data, {'fields': ['expiry_date','skip']})
            print(data)
            if not data[0]['skip']:
                result['expiration_date'] = data[0]['expiry_date']


        return result
