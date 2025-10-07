# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sync Sale Picking Cost",
    "summary": "Sync Sale Picking Cost",
    "version": "15.0.2.0.0",
    "category": "Stock",
    "development_status": "Alpha",
    "website": "https://github.com/sygel-technology/sy-margin-analysis",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "sale_margin",
        "stock_account",
        "stock_valuation_fifo_lot",  # Soft dependency. Explained in README
    ],
}
