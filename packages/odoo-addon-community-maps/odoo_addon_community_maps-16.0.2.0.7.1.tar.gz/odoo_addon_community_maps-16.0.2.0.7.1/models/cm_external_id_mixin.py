import hashlib

from odoo import api, fields, models


class CmExternalIdMixin(models.AbstractModel):
    _name = "cm.external.id.mixin"
    _description = "External ID Mixin"

    cm_external_id = fields.Char(
        string="External ID", compute="_compute_external_id", store=True
    )

    @api.depends("name")
    def _compute_external_id(self):
        for record in self:
            record.cm_external_id = hashlib.sha1(str(record.id).encode()).hexdigest()
