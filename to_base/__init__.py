import logging
import os
import ast

import odoo

from odoo import tools
from odoo.tools import config, pycompat
from odoo.modules import module
from odoo.addons.base.models.res_currency import CurrencyRate

_logger = logging.getLogger(__name__)

from . import controllers
from . import models

get_module_path = module.get_module_path
module_manifest = module.module_manifest
get_module_icon = module.get_module_icon


def _get_branding_module(branding_module='viin_brand'):
    """
    Wrapper for others to override
    """
    return branding_module


def test_installable(module, mod_path=None):
    """
    :param module: The name of the module (sale, purchase, ...)
    :param mod_path: Physical path of module, if not providedThe name of the module (sale, purchase, ...)
    """
    if module == 'general_settings':
        module = 'base'
    if not mod_path:
        mod_path = get_module_path(module, downloaded=True)
    manifest_file = module_manifest(mod_path)
    if manifest_file:
        info = {
            'installable': True,
        }
        f = tools.file_open(manifest_file, mode='rb')
        try:
            info.update(ast.literal_eval(pycompat.to_text(f.read())))
        finally:
            f.close()
        return info
    return {}


viin_brand_manifest = test_installable(_get_branding_module())


def get_viin_brand_module_icon(module):
    """
    This overrides default module icon with
        either '/viin_brand_originmodulename/static/description/icon.png'
        or '/viin_brand/static/img/apps/originmodulename.png'
        where originmodulename is the name of the module whose icon will be overridden
    provided that either of the viin_brand_originmodulename or viin_brand is installable
    """
    branding_module = _get_branding_module()
    brand_originmodulename = '%s_%s' % (branding_module, module if module not in ('general_settings', 'modules') else 'base')
    
    # load manifest of the overriding modules
    viin_brand_originmodulename_manifest = test_installable(brand_originmodulename)

    # /viin_brand/static/img/apps_icon_override/originmodulename.png
    originmodulename_iconpath = os.path.join(branding_module, 'static', 'img', 'apps', '%s.png' % (module if module not in ('general_settings', 'modules') else module == 'general_settings' and 'settings' or 'modules'))

    # /viin_brand_originmodulename'/static/description/icon.png
    iconpath = os.path.join(brand_originmodulename, 'static', 'description', 'icon.png')

    module_icon = False
    for adp in odoo.addons.__path__:
        if viin_brand_originmodulename_manifest.get('installable', False) and os.path.exists(os.path.join(adp, iconpath)):
            module_icon = iconpath
            break
        elif viin_brand_manifest.get('installable', False) and os.path.exists(os.path.join(adp, originmodulename_iconpath)):
            module_icon = originmodulename_iconpath
            break
    if module_icon:
        return module_icon
    else:
        return get_module_icon(module)


def _test_if_loaded_in_server_wide():
    config_options = config.options
    if 'to_base' in config_options.get('server_wide_modules', '').split(','):
        return True
    else:
        return False


if not _test_if_loaded_in_server_wide():
    _logger.warn("The module `to_base` should be loaded in server wide mode using `--load`"
                 " option when starting Odoo server (e.g. --load=base,web,to_base)."
                 " Otherwise, some of its functions may not work properly.")


def _disable_currency_rate_unique_name_per_day():
    # Remove unique_name_per_day constraint in res.currency.rate model in base module
    # It doesn't delete constraint on database server
    for el in CurrencyRate._sql_constraints:
        if el[0] == 'unique_name_per_day':
            _logger.info("Removing the default currency rate's SQL constraint `unique_name_per_day`")
            CurrencyRate._sql_constraints.remove(el)
            break


def pre_init_hook(cr):
    module.get_module_icon = get_viin_brand_module_icon


def uninstall_hook(cr, registry):
    module.get_module_icon = get_module_icon


def post_load():
    _disable_currency_rate_unique_name_per_day()
    module.get_module_icon = get_viin_brand_module_icon
