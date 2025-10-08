from odoo import models, fields, api
from odoo.tools.translate import _


class CmPartner(models.Model):
    _inherit = "res.partner"
    _name = "res.partner"

    # App Person Contact fields
    type = fields.Selection(selection_add=[("map_contact", _("Map contact"))])
