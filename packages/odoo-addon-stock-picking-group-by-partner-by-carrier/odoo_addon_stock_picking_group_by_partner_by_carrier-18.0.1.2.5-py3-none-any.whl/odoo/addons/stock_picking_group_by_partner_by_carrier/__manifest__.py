# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking: group by partner and carrier",
    "Summary": "Group sales deliveries moves in 1 picking per partner and carrier",
    "version": "18.0.1.2.5",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse",
    "depends": [
        "delivery_procurement_group_carrier",
        "sale_stock",
        "stock_delivery",
        "stock_picking_group_by_base",
        "stock_warehouse_out_pull",
    ],
    "data": [
        "views/res_partner.xml",
        "views/stock_picking_type.xml",
        "views/stock_warehouse.xml",
        "report/report_delivery_slip.xml",
        "wizards/stock_picking_merge_wiz.xml",
        "wizards/stock_picking_merge_wiz_info_template.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.report_assets_common": [
            "stock_picking_group_by_partner_by_carrier/static/src/scss/report_delivery_slip.scss"
        ]
    },
    "installable": True,
    "license": "AGPL-3",
}
