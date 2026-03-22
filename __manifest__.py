{
    'name': 'FenixTrace Odoo Connector',
    'summary': 'Register Odoo products on IOTA L1 blockchain via FenixTrace Integration Kit',
    'description': '''
        Connect your Odoo products to the FenixTrace blockchain traceability platform.
        Products are uploaded to IPFS and registered on the IOTA L1 blockchain
        with immutable notarization for full supply chain transparency.
    ''',
    'version': '1.0.0',
    'author': 'FenixTrace — Fenix Software Labs',
    'website': 'https://trace.fenixsoftwarelabs.com',
    'category': 'Inventory/Products',
    'license': 'LGPL-3',
    'depends': ['base', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/server_actions.xml',
        'data/ir_cron.xml',
        'views/res_config_settings_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
