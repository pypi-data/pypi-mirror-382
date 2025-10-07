# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    apply_sync_sale_picking_cost = fields.Boolean(
        compute="_compute_apply_sync_sale_picking_cost"
    )

    @api.depends("tracking", "categ_id")
    def _compute_apply_sync_sale_picking_cost(self):
        products_to_apply = self.filtered(
            lambda a: a.tracking in ["serial", "lot"]
            and a.categ_id.property_cost_method == "fifo"
        )
        products_to_apply.apply_sync_sale_picking_cost = True
        (self - products_to_apply).apply_sync_sale_picking_cost = False
