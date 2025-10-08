from odoo import api, fields, models, _


class CmPlaceImage(models.Model):
    _name = "cm.place.image"
    _inherit = "image.mixin"

    company_id = fields.Many2one(
        "res.company", required=False, default=lambda self: self.env.company
    )
    sequence = fields.Integer(string=_("Sequence"), default=20)
    image_1920 = fields.Image("Image", max_width=1920, max_height=1920, required=True)
    place_id = fields.Many2one(comodel_name="cm.place", string=_("Place"))
    url = fields.Char(string="URL", compute="_compute_url", store=True, readonly=True)

    @api.depends("image_1920")
    def _compute_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self:
            record.url = "%s/web/image/cm.place.image/%s/image_1920" % (
                base_url,
                record.id,
            )

    def get_datamodel_dict(self):
        images = []
        for record in self.sorted(key=lambda r: r.sequence):
            images.append({
                "sequence": record.sequence,
                "url": record.url,
            })
        return images
