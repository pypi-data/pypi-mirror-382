from odoo import models, api, fields
from odoo.tools.translate import _


class CmPresenterModel(models.Model):
    _name = "cm.presenter.model"

    company_id = fields.Many2one(
        'res.company', required=False, default=lambda self: self.env.company
    )
    name = fields.Char(string=_("Name"))
    text_color = fields.Char(string=_("Text Color"))
    display_tooltip_on_presenter = fields.Boolean(
        string=_("Display tooltip on presenter")
    )
    allowed_in_map_mids = fields.Many2many(
        "cm.map",
        "cm_maps_presenter_models",
        "presenter_model_id",
        "map_id",
        string=_("Allowed in maps"),
    )
    json_dataschema = fields.Text(string=_("Schema Data"), translate=True)
    json_schema = fields.Text(string=_("Schema"))
    json_uischema = fields.Text(string=_("UiSchema"), translate=True)
