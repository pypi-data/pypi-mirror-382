# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_valuation_fifo_lot.tests.common import (
    TestStockValuationFifoCommon,
)


class TestSyncSalePickingCost(TestStockValuationFifoCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Test Customer"})

    def create_sale_pick(self):
        so = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "partner_invoice_id": self.customer.id,
                "partner_shipping_id": self.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        so.action_confirm()

        pick = so.picking_ids
        pick.move_lines.write({"quantity_done": 1})
        pick.button_validate()
        return so, pick

    def test_sale(self):
        in_pick, in_moves = self.create_picking("in", self.lot1, ml_qty=5, price=10)
        self.create_landed_cost(in_pick, 10)
        sale, out_pick = self.create_sale_pick()
        self.assertEqual(12, sale.order_line.purchase_price)

    def test_return(self):
        in_pick, in_moves = self.create_picking("in", self.lot1, ml_qty=5, price=10)
        self.create_landed_cost(in_pick, 10)
        sale, out_pick = self.create_sale_pick()
        self.return_picking(out_pick, 1)
        self.assertEqual(12, sale.order_line.purchase_price)
