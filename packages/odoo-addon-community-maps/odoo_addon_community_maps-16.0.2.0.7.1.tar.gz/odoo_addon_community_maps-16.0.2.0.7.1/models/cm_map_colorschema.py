from odoo import models, api, fields
from odoo.tools.translate import _


class CmMapColorschema(models.Model):
    _name = "cm.map.colorschema"

    company_id = fields.Many2one(
        'res.company', required=False, default=lambda self: self.env.company
    )
    name = fields.Char(string=_("Name"))
    color_text_base = fields.Char(string=_("Text Base [color]"))
    color_fill = fields.Char(string=_("Fill [color]"))
    color_border = fields.Char(string=_("Border [color]"))
    color_button = fields.Char(string=_("Button [color]"))
    color_button_hover = fields.Char(string=_("Button [hover color]"))
    color_button_text = fields.Char(string=_("Button Text [color]"))
    color_button_text_hover = fields.Char(
        string=_("Button Text [hover color]"))
    color_button_text_inverted = fields.Char(
        string=_("Button Text Inverted [color]"))
    color_button_text_inverted_hover = fields.Char(
        string=_("Button Text Inverted [hover color]")
    )

    def get_datamodel_dict(self):
        return {
            "textColorBase": self.color_text_base,
            "fillColor": self.color_fill,
            "borderColor": self.color_border,
            "buttonColor": self.color_button,
            "buttonColorHover": self.color_button_hover,
            "buttonTextColor": self.color_button_text,
            "buttonTextColorHover": self.color_button_text_hover,
            "buttonTextInvertedColor": self.color_button_text_inverted,
            "buttonTextInvertedColorHover": self.color_button_text_inverted_hover,
        }
