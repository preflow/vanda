# -*- coding: utf-8 -*-
{
    'name': 'Vanda Client',
    'summary': """Vanda Client""",
    'description': """Vanda Client""",
    'author': 'vanda.minhng.info',
    'maintainer': 'vanda.minhng.info',
    'website': 'https://vanda.minhng.info',
    'category': 'Uncategorized', # https://github.com/odoo/odoo/blob/17.0/odoo/addons/base/data/ir_module_category_data.xml
    'version': '0.1',
    'depends': [],
    'data': [
        # 'security/vanda_client_security.xml',
        'security/ir.model.access.csv',
        'views/vanda_connector_views.xml',
        # 'wizard/toy_add_views.xml',
        # 'wizard/toy_clear_views.xml',
        # 'wizard/cage_update_views.xml',
        # 'views/zoo_creature_views.xml',
        # 'views/zoo_cage_views.xml',
        # 'views/zoo_dummy_views.xml',
        # 'dummy_data/categ.xml',
        # 'dummy_data/dummy.xml',
        # 'views/templates.xml',
        'data/vanda_connector_data.xml',
        'data/vanda_connector_setup.xml',
        # 'data/cron_feed.xml',
        # 'views/report_animal.xml',
        # 'views/zoo_report.xml',
        # 'views/report_animal_inherit.xml',
    ],
    "assets": {
        # 'web.assets_backend': [
        #     #'zoo/static/src/components/**/*',
        #     'zoo/static/src/components/counter/*',
        #     'zoo/static/src/components/mytable/*',
        # ]
    },
    'demo': [],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
