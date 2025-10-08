from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    gender = fields.Selection(
        selection_add=[
            ("nobinary", "No Binary"),
            ("noanswer", "No Answer"),
        ],
    )
