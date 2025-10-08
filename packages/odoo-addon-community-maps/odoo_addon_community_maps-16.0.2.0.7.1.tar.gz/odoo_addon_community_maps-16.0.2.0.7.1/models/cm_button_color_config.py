from odoo import models, api, fields
from odoo.tools.translate import _


class CmButtonColorConfig(models.Model):
    _name = "cm.button.color.config"

    company_id = fields.Many2one(
        'res.company', required=False, default=lambda self: self.env.company
    )
    name = fields.Char(string=_("Name"))
    bg_color = fields.Char(string=_("Background color"))
    text_color = fields.Char(string=_("Text color"))
    border_color = fields.Char(string=_("Border color"))
    bg_hover_color = fields.Char(
        string=_("Background color (hover)"))
    text_hover_color = fields.Char(
        string=_("Text color (hover)"))
    border_hover_color = fields.Char(
        string=_("Text color (hover)"))

    def get_datamodel_dict(self):
        return {
            "bgColor": self.bg_color,
            "textColor": self.text_color,
            "borderColor": self.border_color,
            "bgHoverColor": self.bg_hover_color,
            "textHoverColor": self.text_hover_color,
            "borderHoverColor": self.text_hover_color
        }
