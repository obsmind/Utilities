{
    'name': 'Trikdis B2B Registration',
    'version': '18.0.1.1.0',
    'category': 'Website',
    'license': 'LGPL-3',
    'depends': ['website', 'portal', 'mail', 'website_sale', 'account'],
    'data': ['views/templates.xml'],
    'assets': {
        'web.assets_frontend': [
            'trikdis_b2b/static/src/js/postcode_check.js',
            'trikdis_b2b/static/src/css/custom.css',
        ],
    },
    'installable': True,
    'auto_install': False,
}
