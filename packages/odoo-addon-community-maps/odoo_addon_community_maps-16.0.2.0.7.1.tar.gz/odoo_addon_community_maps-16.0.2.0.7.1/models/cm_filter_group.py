from odoo import models, api, fields
from odoo.tools.translate import _


class CmFilterGroup(models.Model):
    _name = "cm.filter.group"

    _inherit = ["cm.slug.id.mixin"]

    company_id = fields.Many2one(
        'res.company', required=False, default=lambda self: self.env.company
    )
    name = fields.Char(string=_("Name"), translate=True)
    filter_ids = fields.One2many(
        "cm.filter", "filter_group_id", string="Filters")

    allowed_in_map_mids = fields.Many2many(
        "cm.map",
        "cm_maps_filter_groups",
        "filter_group_id",
        "map_id",
        string=_("Allowed in maps"),
    )

    def get_datamodel_dict(self,map_id):
        datamodel = {
            "slug": self.slug_id,
            "name": self.name,
            "filters": self._get_filters_datamodel_dict(map_id),
        }
        return datamodel

    def _get_filters_datamodel_dict(self,map_id):
        filters = []
        for filter in self.filter_ids:
            if filter.has_related_places(map_id):
                filters.append(filter.get_datamodel_dict())
        if not filters:
            return False
        return filters

    def has_related_places(self,map_id):
        for filter in self.filter_ids:
            if filter.has_related_places(map_id):
                return True
        return False
