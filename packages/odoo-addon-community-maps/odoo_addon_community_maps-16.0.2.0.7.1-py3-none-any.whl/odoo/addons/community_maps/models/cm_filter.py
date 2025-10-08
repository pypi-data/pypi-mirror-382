from odoo import models, api, fields
from odoo.tools.translate import _


class CmFilter(models.Model):
    _name = "cm.filter"
    _inherit = ["cm.slug.id.mixin"]
    _slug_models = ["cm.filter"]

    name = fields.Char(string=_("Name"), translate=True)
    icon = fields.Char(string=_("Icon"))
    color = fields.Char(string=_("Color"))
    marker_color = fields.Char(string=_("Marker main color (hex)"))
    marker_text_color = fields.Char(string=_("Marker text color (hex)"))
    marker_bg_color = fields.Char(string=_("Marker background color (hex)"))
    marker_border_color = fields.Char(string=_("Marker border color (hex)"))
    description = fields.Char(string=_("Description"), translate=True)
    filter_group_id = fields.Many2one("cm.filter.group", string="Filter Group")
    places_mids = fields.Many2many(
        "cm.place",
        "cm_places_filters",
        "filter_id",
        "place_id",
        string=_("Related places"),
    )

    def get_datamodel_dict(self):
        datamodel = {
            "slug": self.slug_id,
            "title": self.name,
            "name": self.name,
            "group": self.filter_group_id.slug_id,
            "icon_class": None,
            "iconKey": None,
            "markerColor": {
                "markerText": self.marker_text_color,
                "markerColor": self.marker_color,
                "markerBg": self.marker_bg_color,
                "markerBorder": self.marker_border_color
            },
            "description": None,
        }
        if self.icon:
            datamodel["iconKey"] = self.icon
            datamodel["icon_class"] = self.icon.replace('_', '-')
        if self.description:
            datamodel["description"] = self.description
        return datamodel

    def has_related_places(self,map_id):
        return bool(self.env["cm.place"].search([("filter_mids","in",[self.id]),("map_id","=",map_id),("status","=","published")]))
