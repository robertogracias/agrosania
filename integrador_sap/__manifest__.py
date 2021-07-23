# -*- coding: utf-8 -*-
{
    'name': "integrador_sap",

    'summary': """
        Permite realizar una intregracion entre SAP y ODOO""",

    'description': """
        Pemite mediante la invocacion de servicios REST la intregración entre ODOO y SAP
    """,

    'author': "Exelity",
    'website': "https://exelitycorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['crm','sale_management','base_automation'],

    # always loaded
    'data': [
        'views/views.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
