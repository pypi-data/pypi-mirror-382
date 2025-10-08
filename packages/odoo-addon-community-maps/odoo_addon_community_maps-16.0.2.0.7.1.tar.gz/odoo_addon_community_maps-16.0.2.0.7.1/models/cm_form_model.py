import json
from odoo import models, api, fields
from odoo.tools.translate import _


class CmFormModel(models.Model):
    _name = "cm.form.model"

    _inherit = ["cm.slug.id.mixin"]

    company_id = fields.Many2one(
        'res.company', required=False, default=lambda self: self.env.company
    )
    name = fields.Char(string=_("Name"))
    description = fields.Char(string=_("Description"), translate=True)
    submission_ok_message = fields.Text(
        string=_("Successful message"), translate=True)
    submission_ok_email_template_id = fields.Many2one(
        "mail.template", string=_("Successful email template")
    )
    follower_partner_id = fields.Many2one(
        "res.partner", string=_("Partner to be notified on form submission")
    )
    generate_submission_in_proposal = fields.Boolean(
        string=_("Create a crowdfunding submission if form used as proposal")
    )

    allowed_in_map_mids = fields.Many2many(
        "cm.map",
        "cm_maps_form_models",
        "form_model_id",
        "map_id",
        string=_("Allowed in maps"),
    )

    # Json schema
    json_initial_data = fields.Text(string=_("Initial Data"), translate=True)
    json_schema = fields.Text(string=_("Schema"), translate=True)
    json_uischema = fields.Text(string=_("UiSchema"), translate=True)
    json_submission_fields_map = fields.Text(string=_("Submission fields map"))
    json_place_proposal_submission_fields_map = fields.Text(
        string=_("Place proposal submission fields map")
    )
    json_place_proposal_fields_map = fields.Text(
        string=_("Place proposal fields map"))

    # Form button
    button_label = fields.Char(string=_("Button Label"), translate=True)
    button_color_config_id = fields.Many2one(
        'cm.button.color.config', string=_("Form button color"))

    # Cta button
    cta_button_label = fields.Char(
        string=_("Cta Button Label"), translate=True)
    cta_button_color_config_id = fields.Many2one(
        'cm.button.color.config', string=_("Cta button color"))

    def get_datamodel_dict(self):
        datamodel = {
            "slug": self.slug_id,
            "formButtonLabel": self.button_label,
            "formButtonColor": self.button_color_config_id.get_datamodel_dict(),
            "ctaButtonLabel": None,
            "ctaButtonColor": None,
            "description": None,
            "initialData": json.loads(self.json_initial_data),
            "jsonSchema": json.loads(self.json_schema),
            "uiSchema": json.loads(self.json_uischema)
        }
        if self.cta_button_label:
            datamodel['ctaButtonLabel'] = self.cta_button_label
        if self.cta_button_color_config_id:
            datamodel['ctaButtonColor'] = \
                self.cta_button_color_config_id.get_datamodel_dict()
        if self.description:
            datamodel["description"] = self.description
        return datamodel
