from odoo import models, api, fields
from odoo.tools.translate import _


class CmFormSubmissionMetadata(models.Model):
    _name = "cm.form.submission.metadata"
    _inherit = 'metadata.line'

    submission_id = fields.Many2one(
        "crm.lead", string=_("Submission"), ondelete="cascade"
    )
    mapped_to = fields.Char(string=_("Mapped to"))
