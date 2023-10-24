from odoo import models, api

import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _create_packed_picking(
            self,
            operation_type,
            stock_move_data,
            owner=None,
            location=None,
            location_dest_id=None,
            package_name=None,
            create_lots=False,
            set_ready=False,
    ):
        """ Create a picking and put its product into a a package.
            This is equal to the following sequence:
            - Create a new picking
            - Assign an owner
            - Add products and set qty_done
            - Mark as "Todo"
            - Put in pack
            Args:
            operation_type (stock.picking.type): Operation type
            stock_move_data (List of tuples): [(product_id, qty_done, serial)]
            - (Integer) product_id: id of the product
            - (float) qty_done: quantity done
            - (Char, optional) serial: serial number to assign.
            Default lot names will be used if is None or == False
            Used only if 'create_lots==True'
            owner (res.partner, optional): Owner of the product
            location (stock.location, optional): Source location if differs from the
            operation type one
            location_dest (stock.location, optional): Destination location if differs
            from the operation type one
            package_name (Char, optional): Name to be assigned to the package. Default
            name will be used if not provided.
            set_ready (bool, optional): Try to set picking to the "Ready" state.
            Returns:
            stock.picking: Created picking
        """
        if not location:
            location = operation_type.default_location_src_id
        if not location_dest_id:
            location_dest_id = operation_type.default_location_dest_id
        if not owner:
            owner = self.env.user.partner_id
        vals = {
            'picking_type_id': operation_type.id,
            'location_id': location.id,
            'location_dest_id': location_dest_id.id,
            'owner_id': owner.id,
        }
        stock_picking_id = self.env['stock.picking'].create(vals)
        for product_id, qty_done, serial in stock_move_data:
            product = self.env['product.product'].browse(product_id)
            stock_move_vals = {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': qty_done,
                'product_uom': product.uom_id.id,
                'location_id': location.id,
                'location_dest_id': location_dest_id.id,
                'picking_id': stock_picking_id.id,
            }
            if create_lots and serial:
                stock_move_vals.update({
                    'lot_ids': [(0, 0, {
                        'name': serial,
                        'product_id': product.id,
                    })]
                })
            self.env['stock.move'].create(stock_move_vals)
        stock_picking_id.action_confirm()
        stock_picking_id.action_set_quantities_to_reservation()
        if package_name:
            package_id = self.env['stock.quant.package'].create({
                'name': package_name,
            })
            self.env['stock.package_level'].create({
                'package_id': package_id.id,
                'picking_id': stock_picking_id.id,
                'location_id': location_dest_id.id,
                'location_dest_id': location_dest_id.id,
                'move_line_ids': [(6, 0, stock_picking_id.move_line_ids.ids)],
                'company_id': stock_picking_id.company_id.id,
            })
        else:
            stock_picking_id.action_put_in_pack()
        if set_ready:
            stock_picking_id.button_validate()
        return stock_picking_id
