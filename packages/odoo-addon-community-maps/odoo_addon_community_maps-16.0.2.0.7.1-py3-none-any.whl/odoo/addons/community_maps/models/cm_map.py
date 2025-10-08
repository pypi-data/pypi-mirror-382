import json
from datetime import datetime
from odoo import models, api, fields
from odoo.tools.translate import _
from odoo.addons.community_maps.models.cm_utils import CmUtils
from odoo.addons.queue_job.delay import chain, group
from odoo.exceptions import ValidationError


MARKER_STYLES = [
    ("slim", _("Slim")),
    ("rounded", _("Rounded")),
]
TILE_STYLES = [
    ("osm", _("Open Street Maps")),
    ("arcgisonlineLightGray", _("Arcgisonline LightGray")),
    ("stadiaOutdoors", _("Stadia Outdoors")),
    ("stadiaSmoothDark", _("Stadia SmoothDark")),
]
FONT_FAMILY = [
    ("Montserrat", _("Montserrat")),
]

class CmMap(models.Model):
    _name = "cm.map"

    _inherit = ["cm.slug.id.mixin"]

    active = fields.Boolean(string=_("Active"), default=True)
    company_id = fields.Many2one(
        'res.company', required=False, default=lambda self: self.env.company
    )
    name = fields.Char(string=_("Name"))
    colorschema_id = fields.Many2one(
        "cm.map.colorschema", string=_("Color schema"))
    allowed_form_model_mids = fields.Many2many(
        "cm.form.model",
        "cm_maps_form_models",
        "map_id",
        "form_model_id",
        string=_("Allowed forms"),
    )
    allowed_place_category_mids = fields.Many2many(
        "cm.place.category",
        "cm_maps_place_categories",
        "map_id",
        "place_category_id",
        string=_("Allowed categories"),
    )
    allowed_presenter_model_mids = fields.Many2many(
        "cm.presenter.model",
        "cm_maps_presenter_models",
        "map_id",
        "presenter_model_id",
        string=_("Allowed presenters"),
    )
    allowed_filter_group_mids = fields.Many2many(
        "cm.filter.group",
        "cm_maps_filter_groups",
        "map_id",
        "filter_group_id",
        string=_("Allowed custom filters"),
    )
    place_ids = fields.One2many("cm.place", "map_id", string=_("Places"))
    crowdfunding_type = fields.Selection(
        selection=CmUtils.get_system_crowdfunding_types_selection(),
        default="none",
        required=True,
        string=_("Crowdfunding type"),
    )
    tile_style = fields.Selection(
        selection=TILE_STYLES,
        default='osm',
        required=True,
        string=_("Tile style"),
    )
    show_progress_on_marker = fields.Boolean(
        string=_("Show progress on marker"))
    show_no_opacity_marker = fields.Boolean(
        string=_("Markers without opacity"))
    display_tooltip_on_marker = fields.Boolean(
        string=_("Display tooltip on marker"))
    country_ids = fields.Many2many(
        comodel_name="res.country",
        relation="cm_map_countries_rel",
        column1="map_id",
        column2="country_id",
        string=_("Countries"),
        default=lambda self: self.env["res.country"].search([
            ("code", "in", ["ES"])
        ]),
    )
    # filters and search
    filters_button_color_config_id = fields.Many2one(
        'cm.button.color.config', string=_("Filters button color"))
    allow_filter_by_status = fields.Boolean(string=_('"Active" filter'))
    allow_filter_by_category = fields.Boolean(string=_('"Category" filter'))
    allow_filter_by_crowdfunding = fields.Boolean(
        string=_('"Crowdfunding" filter'))
    allow_filter_by_filter = fields.Boolean(string=_('"Custom" filter'))
    searchbar_placeholder = fields.Char(
        string=_("Searchbar placeholder"), translate=True)
    searchbar_placeholder_text_color = fields.Char(
        string=_("Searchbar placeholder text color"))
    searchbar_button_color_config_id = fields.Many2one(
        'cm.button.color.config',
        string=_("Searchbar button color")
    )
    noresults_msg = fields.Text(
        string=_("No-Results filter message for popup."), translate=True
    )
    privacy_link = fields.Char(string=_("T&C: Privacy url"), translate=True)
    cookies_link = fields.Char(string=_("T&C: Cookies url"), translate=True)
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
    crowdfunding_notification_request_ids = fields.One2many(
        "cm.crowdfunding.notification.request",
        "map_id",
        string=_("Notification requests"),
    )
    admins_to_notify = fields.Many2many(
        "res.users",
        string=_("Admins to notify")
    )
    # Proposal
    has_proposal = fields.Boolean(
        string=_("Proposal form enabled"), compute="_get_has_proposal"
    )
    proposal_cta_title = fields.Char(
        string=_("Proposal cta title"), translate=True)
    proposal_cta_button_color_config_id = fields.Many2one(
        'cm.button.color.config',
        string=_("Proposal cta button color")
    )
    proposal_form_title = fields.Char(
        string=_("Proposal form title"), translate=True)
    proposal_form_subtitle_step_category = fields.Char(
        string=_("Proposal form subtitle (category selection)"), translate=True
    )
    proposal_form_subtitle_step_address = fields.Char(
        string=_("Proposal form subtitle (address selection)"), translate=True
    )
    proposal_form_subtitle_step_form = fields.Char(
        string=_("Proposal form subtitle (form selection)"), translate=True
    )
    proposal_form_model_id = fields.Many2one(
        "cm.form.model", string=_("Proposal submission form")
    )
    allowed_place_category_inproposal_mids = fields.Many2many(
        "cm.place.category",
        "cm_maps_place_categories_inpropsal",
        "map_id",
        "place_category_id",
        string=_("Allowed categories in proposal"),
    )
    # Categories
    categories_filter_title = fields.Char(
        string=_('"Category" filter title'), translate=True
    )
    # Interaction method
    # TODO: To be deleted
    external_link_cta_txt = fields.Char(
        string=_("Call-to-action text for external link button (default)"),
        help=_(
            'It will be used when place interaction method is set to "External link"'
        ),
        translate=True,
    )
    # end TODO
    # Center calculation
    lat_default = fields.Char(string=_("Default Latitude"))
    lng_default = fields.Char(string=_("Default Longitude"))
    zoom_default = fields.Integer(string=_("Default Center"),default=8)
    centering_mode = fields.Selection([('static',_("Use always default values")),('fit-bounds',_("Calculate zoom and center dynamically in order to display all markers"))],string=("Centering mode"),default="static")
    # CRM team for submission creation
    crm_team_id = fields.Many2one(
        'crm.team',
        string=_("CRM Team for place submissions (leads)")
    )
    marker_style = fields.Selection(
        selection=MARKER_STYLES,
        default='slim',
        required=True,
        string=_("Marker style"),
    )
    listview_button_color_config_id = fields.Many2one(
        'cm.button.color.config', string=_("ListView button color"))

    controlbar_bg_color = fields.Char(string=_("Controlbar background color"))
    controlbar_border_color = fields.Char(
        string=_("Controlbar border color (lower)"))

#     font_family = fields.Selection(
#         selection=FONT_FAMILY,
#         default='Montserrat',
#         required=True,
#         string=_("Font family")
#     )
    font_family_code = fields.Char(string=_("Font family"))
    # social items
    social_item_ids = fields.One2many(
        "cm.map.social.item",
        "map_id",
        string=_("Social items"),
    )
    # collect child_place_ids
    child_place_submissions_email_template_id = fields.Many2one(
        'mail.template',
        string=_("Child place submission transfer request email template (official - fallback)"),
        compute="_get_child_place_submissions_email_template_id",
        store=False
    )
    child_place_submissions_successful_email_template_id = fields.Many2one(
        'mail.template',
        string=_("Child place submission transfer successful email template (official - fallback)"),
        compute="_get_child_place_submissions_successful_email_template_id",
        store=False
    )
    custom_child_place_submissions_email_template_id = fields.Many2one(
        'mail.template',
        string=_("Child place submission transfer request email template (custom)"),
    )
    custom_child_place_submissions_successful_email_template_id = fields.Many2one(
        'mail.template',
        string=_("Child place submission transfer successful email template (custom)"),
    )

    # TODO: add constrains to not allow map creation without categories and presenters.
    @api.constrains(
        "allow_filter_by_crowdfunding",
        "crowdfunding_type",
        "show_progress_on_marker"
    )
    def _validate_crowdfunding_config(self):
        for record in self:
            if (
                record.allow_filter_by_crowdfunding is True
                and record.crowdfunding_type == "none"
            ):
                raise ValidationError(
                    _(
                        "We can't have a crowdfunding filter if crowdfunding type is none"
                    )
                )
            if (
                record.show_progress_on_marker is True
                and record.crowdfunding_type == "none"
            ):
                raise ValidationError(
                    _("We can't show progress on marker if crowdfunding type is none")
                )

    @api.depends(
        "proposal_form_model_id",
        "allowed_place_category_inproposal_mids"
    )
    def _get_has_proposal(self):
        for record in self:
            if record.allowed_place_category_inproposal_mids:
                record.has_proposal = True
                for category in record.allowed_place_category_inproposal_mids:
                    if (
                        not category.proposal_form_model_id
                        and not record.proposal_form_model_id
                    ):
                        record.has_proposal = False
            else:
                record.has_proposal = False

    @api.depends("proposal_form_model_id")
    def _get_submission_ok_message(self):
        for record in self:
            try:
                ok_message = \
                    record.proposal_form_model_id.submission_ok_message
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

    def get_config_datamodel_dict(self):
        return {
            "theme": self._get_theme_datamodel_dict(),
            "fontFamily": self.font_family_code,
            "crowdfunding": self._get_crowdfunding_datamodel_dict(),
            "centering": self._get_centering_datamodel_dict(),
            "displayTooltipOnMarker": self.display_tooltip_on_marker,
            "showFilters": self._get_filters_datamodel_dict(),
            "filtersButtonColor": self.filters_button_color_config_id.get_datamodel_dict(),
            "legal": self._get_legal_datamodel_dict(),
            "forms": self._get_form_models_datamodel_dict(),
            "suggestPlaceForms": self._get_proposal_form_models_datamodel_dict(),
            "categories": self._get_categories_datamodel_dict(),
            "countries": self._get_countries_datamodel_dict(),
            "filterGroups": self._get_filter_groups_datamodel_dict(),
            "categoriesInProposal": self._get_categories_inproposal_datamodel_dict(),
            "categoriesFilterLabel": self.categories_filter_title,
            "searchBar": self._get_searchbar_datamodel_dict(),
            "controlBar": self._get_controlbar_datamodel_dict(),
            "noResultsMsg": self.noresults_msg,
            "noMarkerOpacity": self.show_no_opacity_marker,
            "hasProposal": self.has_proposal,
            "proposalCtaLabel": self.proposal_cta_title,
            "proposalCtaButtonColor": self.proposal_cta_button_color_config_id.get_datamodel_dict(),
            "proposalFormLabel": self.proposal_form_title,
            "proposalFormStepCategoryLabel": self.proposal_form_subtitle_step_category,
            "proposalFormStepAddressLabel": self.proposal_form_subtitle_step_address,
            "proposalFormStepFormLabel": self.proposal_form_subtitle_step_form,
            "markerStyle": self.marker_style,
            "listViewButtonColor": self.listview_button_color_config_id.get_datamodel_dict()
        }

    def _get_centering_datamodel_dict(self):
        return {
            "latDefault": self.lat_default,
            "lngDefault": self.lng_default,
            "zoomDefault": self.zoom_default,
            "centeringMode": self.centering_mode,
        }

    def _get_controlbar_datamodel_dict(self):
        return {
            "bgColor": self.controlbar_bg_color,
            "lowerBorderColor": self.controlbar_border_color
        }

    def _get_searchbar_datamodel_dict(self):
        return {
            "placeholder": self.searchbar_placeholder,
            "placeholderTextColor": self.searchbar_placeholder_text_color,
            "buttonColor": self.searchbar_button_color_config_id.get_datamodel_dict(),
        }

    def get_places_datamodel_dict(self):
        places = []
        for place in self.place_ids:
            if place.status == "published" and place.type == "place":
                places.append(place.get_datamodel_dict(single_view=False))
                if place.child_place_ids:
                    for child_place in place.child_place_ids:
                        if child_place.lat and child_place.lng:
                            places.append(
                                place.get_datamodel_dict(
                                    single_view=False,
                                    child=child_place)
                                )
        return places

    def _get_theme_datamodel_dict(self):
        return {
            "color": self.colorschema_id.get_datamodel_dict(),
            "tileStyle": self.tile_style,
        }

    def _get_crowdfunding_datamodel_dict(self):
        return {
            "showMarkerProgress": self.show_progress_on_marker,
        }

    def _get_legal_datamodel_dict(self):
        legal = {"privacyLink": None, "cookiesLink": None}
        if self.privacy_link:
            legal["privacyLink"] = self.privacy_link
        if self.privacy_link:
            legal["cookiesLink"] = self.cookies_link
        return legal

    def _get_filters_datamodel_dict(self):
        return {
            "status": self.allow_filter_by_status,
            "crowdfunding": self.allow_filter_by_crowdfunding,
            "categories": self.allow_filter_by_category,
            "customFilters": self.allow_filter_by_filter,
        }

    def _get_form_models_datamodel_dict(self):
        form_models = {}
        for form_model in self.allowed_form_model_mids:
            form_models[form_model.slug_id] = form_model.get_datamodel_dict()
        if not form_models:
            return False
        return form_models

    def _get_proposal_form_models_datamodel_dict(self):
        form_models = {}
        if self.proposal_form_model_id:
            form_models[
                "suggest_place_generic"
            ] = self.proposal_form_model_id.get_datamodel_dict()
        for place_category in self.allowed_place_category_mids:
            if place_category.proposal_form_model_id:
                form_models[
                    place_category.slug_id
                ] = place_category.proposal_form_model_id.get_datamodel_dict()
        if not form_models:
            return False
        return form_models

    def _get_categories_datamodel_dict(self):
        categories = {}
        for place_category in self.allowed_place_category_mids:
            categories[place_category.slug_id] = \
                place_category.get_datamodel_dict()
        if not categories:
            return False
        return categories

    def _get_countries_datamodel_dict(self):
        countries = []
        for country in self.country_ids:
            countries.append({"name": country.name, "code": country.code})
        if not countries:
            return False
        return countries

    def _get_filter_groups_datamodel_dict(self):
        groups = []
        for group in self.allowed_filter_group_mids:
            if group.has_related_places(self.id):
                groups.append(group.get_datamodel_dict(self.id))
        if not groups:
            return False
        return groups

    def _get_categories_inproposal_datamodel_dict(self):
        categories = {}
        for place_category in self.allowed_place_category_inproposal_mids:
            categories[place_category.slug_id] = \
                place_category.get_datamodel_dict()
        if not categories:
            return False
        return categories

    def _get_child_place_submissions_email_template_id(self):
        for record in self:
            record.child_place_submissions_email_template_id = self.env.ref("community_maps.email_templ_request_submissions_transfer").id

    def _get_child_place_submissions_successful_email_template_id(self):
        for record in self:
            record.child_place_submissions_successful_email_template_id = self.env.ref("community_maps.email_templ_lead_request_submissions_transfer_successful").id

    # Form Submission
    def submit_place_proposal(self, data, category):
        # place creation
        place_creation_data = {
            "name": self.name + " (Place proposal)",
            "type": "place_proposal",
            "map_id": self.id,
            "place_category_id": category.id,
            "company_id": self.company_id.id
        }
        if "address" in data.keys():
            if "latitude" in data["address"].keys():
                place_creation_data["lat"] = data["address"]["latitude"]
            if "longitude" in data["address"].keys():
                place_creation_data["lng"] = data["address"]["longitude"]
            if "address" in data["address"].keys():
                place_creation_data["address_txt"] = data["address"]["address"]
        place = self.env["cm.place"].create(place_creation_data)
        place.message_subscribe([self.env.user.partner_id.id])
        #  submission creation
        submission_creation_data = {
            "name": self.name + " (Place Proposal Submission)",
            "submission_type": "place_proposal_submission",
            "place_id": place.id,
            "team_id": self.crm_team_id.id,
            "company_id": self.crm_team_id.company_id.id
        }
        # shareable url base
        shareable_url_base = data.get("shareable_url_base", False)
        if shareable_url_base:
            submission_creation_data["shareable_url_base"] = shareable_url_base
        submission = self.env["crm.lead"].create(submission_creation_data)
        submission.write({"name": submission.name + " #" + str(submission.id)})
        # metadata & fields mapping
        # submission
        if category.proposal_form_model_id:
            proposal_form = category.proposal_form_model_id
            fields_map = proposal_form.json_place_proposal_submission_fields_map
            proposal_fields_map = (
                category.proposal_form_model_id.json_place_proposal_fields_map
            )
        else:
            proposal_form = self.proposal_form_model_id
            fields_map = proposal_form.json_place_proposal_submission_fields_map
            proposal_fields_map = (
                self.proposal_form_model_id.json_place_proposal_fields_map
            )
        submission.create_submission_metadata(
            data=data, fields_map=str(fields_map))
        # place
        proposal_update_dict = {
            "name": place.name + " #" + str(place.id),
            "proposal_form_submission_id": submission.id,
        }
        if proposal_fields_map:
            jproposal_fields_map = json.loads(proposal_fields_map)
            for key in data.keys():
                if key in jproposal_fields_map.keys():
                    if jproposal_fields_map[key]["model_field"] == "number":
                        value = float(data[key])
                    else:  # string
                        value = str(data[key])
                    proposal_update_dict[
                        jproposal_fields_map[key]["model_field"]
                    ] = value
                    metadata = self.env["cm.form.submission.metadata"].search(
                        [("submission_id", "=", submission.id), ("key", "=", key)]
                    )
                    if metadata:
                        metadata.write(
                            {
                                "mapped_to": "proposal."
                                + jproposal_fields_map[key]["model_field"]
                            }
                        )
        place.write(proposal_update_dict)
        place.setup_slug_id()
        # Notifications
        if proposal_form.follower_partner_id:
            place.message_subscribe([proposal_form.follower_partner_id.id])
        place.message_post(
            subject=place.name + " notification",
            body="A new proposal has been made!",
            subtype_id=None,
            message_type="notification",
            subtype_xmlid='mail.mt_comment'
        )
        return {
            "submission": submission,
            "place": place,
            "proposal_form": proposal_form,
        }

    # ACTIONS
    def archive_workflow_action(self):
        for record in self:
            record.write({'active': False})

    def unarchive_workflow_action(self):
        for record in self:
            record.write({'active': True})

    # CRONS
    def cron_submission_transfer(self):
        childs_in_process = self.env['cm.place.child'].search([('request_date','!=',False),('transfer_date','=',False)])
        transfer_jobs = []
        for child in childs_in_process:
            if (datetime.now() - child.request_date).days >= 7:
                transfer_jobs.append(child.delayable().complete_transfer())
        notification_jobs = []
        for destination in childs_in_process.mapped('parent_place_id'):
            notification_jobs.append(destination.delayable().crowdfunding_notify_if_must())
        if transfer_jobs:
            chain(group(*transfer_jobs), group(*notification_jobs)).delay()
