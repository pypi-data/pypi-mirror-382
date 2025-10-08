from odoo import models, api, fields
from odoo.tools.translate import _


class CmPlaceCrowdfundingNotificationRequest(models.Model):
    _name = "cm.crowdfunding.notification.request"
    _order = "percentage desc"

    map_id = fields.Many2one("cm.map", string=_("Map"), ondelete="cascade")
    percentage = fields.Integer(string=_("Percentage"))
    notify_admins = fields.Boolean(string=_("Notify admins"))
    notify_submissions = fields.Boolean(string=_("Notify submissions"))
    template_admins = fields.Many2one(
        "mail.template",
        string=_("Template admins"),
        domain=[("model", "=", "cm.place")]
    )
    template_submissions = fields.Many2one(
        "mail.template",
        string=_("Template submissions"),
        domain=[("model", "=", "crm.lead")]
    )
