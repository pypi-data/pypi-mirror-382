from odoo import models, api, fields
from odoo.tools.translate import _


class CmPlaceCategory(models.Model):
    _name = "cm.place.category"

    _inherit = ["cm.slug.id.mixin"]

    company_id = fields.Many2one(
        'res.company', required=False, default=lambda self: self.env.company
    )
    name = fields.Char(string=_("Name"), translate=True)
    icon = fields.Char(string=_("Icon"))
    color = fields.Char(string=_("Color"))
    description = fields.Char(string=_("Description"), translate=True)
    proposal_form_model_id = fields.Many2one(
        "cm.form.model", string=_("Proposal submission form")
    )
    allowed_in_map_mids = fields.Many2many(
        "cm.map",
        "cm_maps_place_categories",
        "place_category_id",
        "map_id",
        string=_("Allowed in maps"),
    )
    submission_ok_message = fields.Text(
        string=_("Successful message"),
        compute="_get_submission_ok_message",
        store=False,
    )
    submission_ok_email_template_id = fields.Many2one(
        "mail.template",
        compute="_get_submission_ok_email_template_id",
        string=_("Successful email template"),
        store=False,
    )
    marker_color = fields.Char(string=_("Marker main color (hex)"))
    marker_text_color = fields.Char(string=_("Marker text color (hex)"))
    marker_bg_color = fields.Char(string=_("Marker background color (hex)"))
    marker_border_color = fields.Char(string=_("Marker border color (hex)"))

    def get_datamodel_dict(self):
        datamodel = {
            "slug": self.slug_id,
            "name": self.name,
            "iconKey": None,
            "icon_class": None,
            "description": None,
            "markerColor": {
                "markerText": self.marker_text_color,
                "markerColor": self.marker_color,
                "markerBg": self.marker_bg_color,
                "markerBorder": self.marker_border_color
            }
        }
        if self.icon:
            datamodel["iconKey"] = self.icon
            datamodel["icon_class"] = self.icon.replace('_', '-')

        if self.description:
            datamodel["description"] = self.description
        return datamodel

    @api.depends("proposal_form_model_id")
    def _get_submission_ok_message(self):
        for record in self:
            try:
                ok_message = record.proposal_form_model_id.submission_ok_message
            except:
                ok_message = False
            record.submission_ok_message = ok_message

    @api.depends("proposal_form_model_id")
    def _get_submission_ok_email_template_id(self):
        for record in self:
            try:
                mail_template = (
                    record.proposal_form_model_id.submission_ok_email_template_id
                )
            except:
                mail_template = False
            record.submission_ok_email_template_id = mail_template.id
