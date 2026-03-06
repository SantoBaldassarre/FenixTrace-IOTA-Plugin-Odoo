{
    'name': 'FenixTrace Odoo Connector',
    'summary': 'Invio prodotti Odoo verso FenixTrace Integration Kit',
    'version': '1.0.0',
    'author': 'FenixTrace',
    'license': 'LGPL-3',
    'depends': ['base', 'product'],
    'data': [
        'data/server_actions.xml',
        'views/res_config_settings_views.xml',
        'views/product_template_views.xml'
    ],
    'installable': True,
    'application': False
}
