import json
import re
from odoo import models, api, fields
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.community_maps.models.cm_utils import CmUtils


class CmFormSubmission(models.Model):
    _name = "crm.lead"
    _inherit = ["crm.lead"]

    submission_type = fields.Selection(
        [
            ("none", _("None")),
            ("place_submission", _("Place submission")),
            ("place_proposal_submission", _("Place proposal")),
        ],
        string=_("Submission type (maps)"),
        default='none'
    )
    form_submission_metadata_ids = fields.One2many(
        "cm.form.submission.metadata",
        "submission_id",
        string=_("Submission metadata")
    )
    crowdfunding_type = fields.Selection(
        selection=CmUtils.get_system_crowdfunding_types_selection(),
        default="none",
        compute="_get_crowdfunding_type",
        string=_("Crowdfunding type"),
        store=True,
    )
    shareable_url_base = fields.Char(_("Base shareable url"))
    shareable_url = fields.Char(
        _("Shareable url"), compute="_get_shareable_url", store=True
    )
    place_id = fields.Many2one("cm.place", string=_("Place"))
    child_place_id = fields.Many2one("cm.place.child", string=_("Child Place"))
    form_submission_transfer_request_ids = fields.One2many(
        'cm.form.submission.transfer.request',
        'submission_id',
        string=_("Submission transfer requests"),
    )
    submission_lang_code = fields.Char(compute="_compute_submission_lang_code",store=False)

    _order = "id desc"

    _sql_constraints = [
        (
            "check_probability",
            "check(probability >= 0)",
            "The probability of closing the deal should be bigger than 0%",
        )
    ]

    @api.depends('lang_id')
    def _compute_submission_lang_code(self):
        for record in self:
            record.submission_lang_code = False
            if record.lang_id:
                record.submission_lang_code = record.lang_id.code
            else:
                record.submission_lang_code = self.env.user.lang

    def unlink(self):
        for record in self:
            related_proposal_places = self.env["cm.place"].search(
                [("proposal_form_submission_id", "=", record.id)]
            )
            if record.place_id or related_proposal_places:
                raise ValidationError(
                    _(
                        "You can't delete. Some Places relate on this info. Archive instead."
                    )
                )
            return super(CmFormSubmission, record).unlink()

    @api.depends("place_id")
    def _get_crowdfunding_type(self):
        for record in self:
            try:
                crowdfunding_type = record.place_id.map_id.crowdfunding_type
            except:
                crowdfunding_type = False
            record.crowdfunding_type = crowdfunding_type

    @api.depends("shareable_url_base")
    def _get_shareable_url(self):
        for record in self:
            try:
                place_slug = record.place_id.slug_id
            except:
                place_slug = False
            if record.shareable_url_base and place_slug:
                record.shareable_url = (
                    record.shareable_url_base + "?mapPlace=" + place_slug + "#map"
                )

    @api.constrains("expected_revenue")
    def constrain_revenue(self):
        for record in self:
            if record.place_id:
                record.place_id._get_total_committed_invoicing()
                record.place_id._get_completed_percentage()
            record.recompute_probability()

    def recompute_probability(self):
        if self.place_id:
            for submission in self.place_id.form_submission_ids:
                submission.update_probability()
        else:
            submissions = self.env["crm.lead"].search(
                [("submission_type", "=", "place_submission")])
            if submissions:
                for submission in submissions:
                    submission.update_probability()
        self.update_probability()

    def update_probability(self):
        probability = 0
        if self.place_id:
            probability = self.place_id.completed_percentage
        self.write({"probability": probability})

    def _crowdfunding_notify_if_must(self):
        if self.place_id:
            self.place_id.crowdfunding_notify_if_must()

    def create_submission_metadata(self, data, fields_map=False):
        model_update_dict = {}
        for key in data:
            if key != "address":
                # metadata
                metadata = {
                    "key": key,
                    "value": str(data[key]),
                    "submission_id": self.id,
                }
                # model map
                if fields_map:
                    jfields_map = json.loads(fields_map)
                    if key in jfields_map.keys():
                        if jfields_map[key]["type"] == "number":
                            value = float(data[key])
                        elif jfields_map[key]["type"] == "number_in_cents":
                            value = float(data[key]) / 100
                        elif jfields_map[key]["type"] == "number_integer":
                            value = int(data[key])
                        elif jfields_map[key]["type"] == "currency_text":
                            value = [
                                float(s) for s in re.findall(r"-?\d+\.?\d*", data[key])
                            ][0]
                        else:  # string
                            value = str(data[key])
                        model_update_dict[jfields_map[key]
                                          ["model_field"]] = value
                        metadata["mapped_to"] = (
                            "submission." + jfields_map[key]["model_field"]
                        )
                # write metadata
                metadata = self.env["cm.form.submission.metadata"].create(
                    metadata)
        if model_update_dict:
            self.write(model_update_dict)

    def _get_metadata_as_msg(self):
        msg = "<ul>"
        for meta in self.form_submission_metadata_ids:
            msg += "<li>"+meta.key+": "+meta.value+"</li>"
        msg += "</ul>"
        return msg
