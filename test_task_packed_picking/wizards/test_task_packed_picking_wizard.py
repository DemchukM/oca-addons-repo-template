from odoo import models, fields

import logging

_logger = logging.getLogger(__name__)


class TestTaskPackedPickingWizard(models.TransientModel):
    _name = 'test.task.packed.picking.wizard'
    _description = 'Test Task Packed Picking Wizard'

    operation_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Operation Type',
        required=True, )
    create_lots = fields.Boolean(
        string='Create Lots',
        default=False, )
    owner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Owner', )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Source Location', )
    location_dest_id = fields.Many2one(
        comodel_name='stock.location',
        string='Destination Location', )
    package_name = fields.Char(
        string='Package Name', )
    set_ready = fields.Boolean(
        string='Set Ready',
        default=False, )
    line_ids = fields.One2many(
        comodel_name='test.task.packed.picking.line.wizard',
        inverse_name='wizard_id',
        string='Lines', )

    def action_create_picking(self):
        self.ensure_one()
        stock_move_data = [(line.product_id.id, line.qty_done, line.serial) for line in self.line_ids]
        stock_picking_id = self.env['stock.picking']._create_packed_picking(
            operation_type=self.operation_type_id,
            stock_move_data=stock_move_data,
            owner=self.owner_id,
            location=self.location_id,
            location_dest_id=self.location_dest_id,
            package_name=self.package_name,
            create_lots=self.create_lots,
            set_ready=self.set_ready,
        )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Picking',
            'res_model': 'stock.picking',
            'res_id': stock_picking_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class TestTaskPackedPickingLineWizard(models.TransientModel):
    _name = 'test.task.packed.picking.line.wizard'
    _description = 'Test Task Packed Picking Line Wizard'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True, )
    qty_done = fields.Float(
        string='Quantity Done',
        required=True, )
    serial = fields.Char(
        string='Serial', )
    wizard_id = fields.Many2one(
        comodel_name='test.task.packed.picking.wizard',
        string='Wizard', )
