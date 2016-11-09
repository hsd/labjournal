# -*- coding: utf-8 -*-

{
    'name': 'Laboratory journal',
    'summary': 'Manager lab journals; production lot usage logs',
    'version': '2.0',
    'category': 'chemical',
    'description': """Implementation of personalized lab log journals""",
    'author': 'HS-Development BV',
    'website': 'https://partners.hsdev.com',
    'license': 'AGPL-3',
    'depends': ['stock'],
    'data': [
        'data/res.groups.csv',
        'security/ir.model.access.csv',
        'labjournal_view.xml',
        'labjournal_sequence.xml',
        'stock_production_lot_view.xml',
        ]
}
