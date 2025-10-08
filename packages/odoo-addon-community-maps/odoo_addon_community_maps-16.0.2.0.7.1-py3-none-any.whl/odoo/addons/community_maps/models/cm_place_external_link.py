from odoo import models, api, fields
from odoo.tools.translate import _


class CmPlaceExternalLink(models.Model):
    _name = "cm.place.external.link"

    place_id = fields.Many2one(
        'cm.place', string=_("Related place")
    )
    name = fields.Char(string=_("Label"), translate=True)
    url = fields.Char(string=_("Url"), translate=True)
    target = fields.Selection(selection=[
        ('_blank', _('Open in a new tab')),
        ('_top', _('Open in the same page'))
    ], default='_blank', required=True, string=_("Target link"))
    button_color_config_id = fields.Many2one(
        'cm.button.color.config',
        string=_("Button Color"))
    sort_order = fields.Integer(string=_("Sort order"))

    _order = "sort_order asc"

    def get_datamodel_dict(self):
        return {
            'label': self.name,
            'url': self.url,
            'target': self.target,
            'buttonColor': self.button_color_config_id.get_datamodel_dict()
        }
