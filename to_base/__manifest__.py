# -*- coding: utf-8 -*-
{
    'name': "TVTMA Base",

    'summary': """
Additional tools and utilities for other modules""",

    'description': """
Base module that provides additional tools and utilities for developers

* Check if barcode exist by passing model and barcode field name
* Generate barcode from any number
* Find the IP of the host where Odoo is running.
* Date & Time Utilities

  * Convert time to UTC
  * UTC to local time
  * Get weekdays for a given period
  * Same Weekday next week
  * Split date
* Zip a directory and return bytes object which is ready for storing in Binary fields. No on-disk temporary file is needed.
  
  * usage: zip_archive_bytes = self.env['to.base'].zip_dir(path_to_directory_to_zip)
* Sum all digits of a number (int|float)
* Finding the lucky number (digit sum = 9) which is nearest the given number
* Return remote host IP by sending http request to http(s)://base_url/my/ip/
* Replace the SQL constraint `unique_name_per_day` in res.currency.rate model with Python constraint
* Add new widget named `readonly_state_selection` to allow dropdown selection even the record is readonly to the user. To implement this

  .. code-block:: xml

    <record id="kanban_state_model_view_form" model="ir.ui.view">
        <field name="name">Form View Name</field>
        <field name="model">your.model</field>
        <field name="arch" type="xml">
            <form string="Form View Name">
                <field name="kanban_state" widget="readonly_state_selection" force_save="1" />
            </form>
        </field>
    </record>
* Replace Odoo's module icons with your own icons by

  * How to do

    * creating a new module named 'viin_brand' and place your icons in side `viin_brand/static/imp/apps/`
    * the icon name convention is `module_name.png`. For example, `mrp.png` to replace the module MRP's icon
    * upgrade all the modules (start Odoo server with option `-u all`)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': 'https://v13demo-int.erponline.vn',
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web', 'base_setup'],

    # always loaded
    'data': [
        'views/assets.xml',
        ],
#
#     'qweb': ['static/src/xml/*.xml'],
    'pre_init_hook': 'pre_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'post_load': 'post_load',
    'installable': True,
    'auto_install': ['web'],
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
