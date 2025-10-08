from odoo import models, api, fields
from odoo.tools.translate import _


class CmPlaceCrowdfundingNotificationRequest(models.Model):
    _name = "cm.crowdfunding.notification"

    place_id = fields.Many2one(
        "cm.place", string=_("Place"), ondelete="cascade")
    percentage = fields.Integer(string=_("Percentage"))

    _order = "percentage desc"
