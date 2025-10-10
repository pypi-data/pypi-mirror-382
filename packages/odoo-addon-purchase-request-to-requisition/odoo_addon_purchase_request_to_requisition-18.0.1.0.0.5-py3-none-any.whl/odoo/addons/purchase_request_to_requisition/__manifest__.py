# Copyright 2016 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request to Purchase Agreement",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, Acsone SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": [
        "purchase_request",
        "purchase_requisition_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_request_line_make_purchase_requisition_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_requisition_view.xml",
        "views/purchase_order_view.xml",
    ],
    "maintainer": ["Saran440"],
    "license": "AGPL-3",
    "installable": True,
}
