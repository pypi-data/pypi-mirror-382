# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "move_ids",
        "move_ids.stock_valuation_layer_ids",
        "move_ids.picking_id.state",
        "qty_delivered",
    )
    def _compute_purchase_price(self):
        """
        The purchase_price, which is the cost this module is syncing,
        is already being computed the super() this function.
        The function has a "is_returned" context parameter, and it
        should be passed if the line is being returned to compute correctly
        the purchase price.

        :precondition:  A dependency of the purchase_price has been edited
                        and it should be recomputed
        :postcondition: The purchase_price has been computed using the
                        'is_returned' context, and its value will be correct
                        even when returning a move_id.
        """
        res = None
        for line in self:
            returned = not line.qty_delivered and any(
                line.move_ids.filtered(
                    lambda m: m.state == "done"
                ).origin_returned_move_id
            )
            res = super(
                SaleOrderLine, line.with_context(is_returned=returned)
            )._compute_purchase_price()
        return res
