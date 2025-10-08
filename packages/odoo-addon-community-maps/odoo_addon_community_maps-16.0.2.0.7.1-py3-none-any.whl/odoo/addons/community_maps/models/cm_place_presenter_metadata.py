from odoo import models, api, fields
from odoo.tools.translate import _


class CmPlacePresenterMetadata(models.Model):
    _name = "cm.place.presenter.metadata"
    _inherit = 'metadata.line'

    place_id = fields.Many2one(
        "cm.place", string=_("Place"), ondelete="cascade")
    type = fields.Char(string=_("Type"))
    format = fields.Char(string=_("Format"))
