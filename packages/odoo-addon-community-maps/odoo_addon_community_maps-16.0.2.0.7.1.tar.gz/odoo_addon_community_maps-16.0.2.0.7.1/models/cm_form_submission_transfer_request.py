from datetime import datetime
from odoo import models, api, fields
from odoo.tools.translate import _


class CmFormSubmissionTransferRequest(models.Model):
    _name = "cm.form.submission.transfer.request"
    _inherit = ["cm.external.id.mixin"]

    name = fields.Char(string=_("Name"),compute="_compute_name")
    company_id = fields.Many2one(
        'res.company', required=False, default=lambda self: self.env.company
    )
    submission_id = fields.Many2one(
        "crm.lead", string=_("Submission"), required=True
    )
    origin_place_id = fields.Many2one(
        "cm.place", string=_("Origin"), required=True
    )
    destination_place_id = fields.Many2one(
        "cm.place", string=_("Destination"), required=True
    )
    child_place_id = fields.Many2one(
        "cm.place.child", string=_("Related Child"), required=True,
    )
    status = fields.Selection(
        [('pending',_('Pending')),('accepted',_('Accepted')),('rejected',_('Rejected'))],
        string=_("Status"),
        default="pending"
    )
    request_date = fields.Datetime(string=_("Request date"))
    transfer_date = fields.Datetime(string=_("Transfer date"))
    rejected_date = fields.Datetime(string=_("Rejected date"))
    reject_confirmation_url = fields.Char(compute="_compute_reject_confirmation_url",store=False)
    email_from = fields.Char(compute="_compute_email_from",store=False)

    @api.depends('submission_id')
    def _compute_email_from(self):
        for record in self:
            record.email_from = record.submission_id.email_from

    @api.depends('submission_id','origin_place_id','destination_place_id')
    def _compute_name(self):
        for record in self:
            record.name = _("Transfer request for submission [{submission_name}] from [{origin_name}] to [{destination_name}]").format(
                submission_name=record.submission_id.name,
                origin_name=record.origin_place_id.name,
                destination_name=record.destination_place_id.name
            )

    @api.depends("cm_external_id")
    def _compute_reject_confirmation_url(self):
        for record in self:
            url = record.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if record.submission_id.lang_id:
                url += "/{}".format(record.submission_id.lang_id.url_code)
            url += "/reject-submission-transfer?request={}".format(record.cm_external_id)
            record.reject_confirmation_url = url

    def request_transfer_reject(self):
        if self.origin_place_id.map_id.custom_child_place_submissions_email_template_id:
            email_tmpl = self.origin_place_id.map_id.custom_child_place_submissions_email_template_id
        else:
            email_tmpl = self.origin_place_id.map_id.child_place_submissions_email_template_id
        email_tmpl.send_mail(
            res_id=self.id,
            force_send=True,
            email_layout_xmlid="mail.mail_notification_layout",
        )
        self.submission_id.message_post(
            body=_("Submission tranfer REQUEST: Reject link [{reject_link}] has been sent for request: {request_name}").format(
                reject_link=self.reject_confirmation_url, request_name=self.name
            ),
        )
        self.write({
            'request_date': datetime.now()
        })

    def reject_request_transfer_reject(self):
        self.submission_id.message_post(
            body=_("Submission tranfer REJECTED: {request_name}").format(
                request_name=self.name
            ),
        )
        self.write({
            'status': 'rejected',
            'rejected_date': datetime.now()
        })

    def accept_request_transfer(self):
        self.submission_id.write({
            'place_id': self.destination_place_id.id
        })
        self.submission_id.constrain_revenue()
        self.write({
            'status': 'accepted',
            'transfer_date': datetime.now()
        })
        if self.origin_place_id.map_id.custom_child_place_submissions_successful_email_template_id:
            email_tmpl = self.origin_place_id.map_id.custom_child_place_submissions_successful_email_template_id
        else:
            email_tmpl = self.origin_place_id.map_id.child_place_submissions_successful_email_template_id
        email_tmpl.send_mail(
            res_id=self.id,
            force_send=True,
            email_layout_xmlid="mail.mail_notification_layout",
        )
        self.submission_id.message_post(
            body=_("Submission tranfer ACCEPTED: {request_name}").format(
                request_name=self.name
            ),
        )

