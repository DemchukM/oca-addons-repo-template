{
    'name': 'Test Task Packed Picking',
    'version': '1.0',
    'category': 'Test',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'stock',
    ],

    'data': [
        'security/ir.model.access.csv',

        'wizards/test_task_packed_picking_wizard_views.xml',
    ],

    'installable': True,
}
