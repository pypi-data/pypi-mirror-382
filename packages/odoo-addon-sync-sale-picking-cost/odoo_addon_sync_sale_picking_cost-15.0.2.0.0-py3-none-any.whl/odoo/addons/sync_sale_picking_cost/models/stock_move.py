# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_out_svl(self, forced_quantity=None):
        layers = super()._create_out_svl(forced_quantity)
        for layer in layers.filtered(
            lambda a: a.stock_move_id
            and a.stock_move_id.sale_line_id
            and a.stock_move_id.sale_line_id.product_id.apply_sync_sale_picking_cost
        ):
            line_id = layer.stock_move_id.sale_line_id
            if line_id.purchase_price != layer.unit_cost:
                line_id.write({"purchase_price": layer.unit_cost})
        return layers
