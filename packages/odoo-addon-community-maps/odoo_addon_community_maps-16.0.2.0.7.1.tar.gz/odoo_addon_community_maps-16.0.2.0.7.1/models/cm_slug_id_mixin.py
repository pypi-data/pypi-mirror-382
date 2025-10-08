from slugify import slugify
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class CmSlugIdMixin(models.AbstractModel):
    _slug_models = ["cm.form.model", "cm.place.category", "cm.place", "cm.map"]

    _name = "cm.slug.id.mixin"
    _description = "Slug ID Mixin"

    # do not access directly, always use get_api_external_id method
    slug_id = fields.Char(string="External slug ID")

    @api.onchange("name")
    def setup_slug_id(self):
        for record in self:
            if not record.slug_id:
                record.slug_id = record._generate_slug()

    @api.constrains("slug_id")
    def _check_slug_uniqueness(self):
        for record in self:
            if record._is_slug_unique(slug=record.slug_id, exclude_self=True) is False:
                raise ValidationError(_("Your slug is not unique in the system"))

    def _generate_slug(self):
        if self.name:
            original_slug = slugify(self.name)
            proposed_slug = original_slug
            unique = self._is_slug_unique(proposed_slug)
            i = 1
            while unique is False:
                proposed_slug = original_slug + "-" + str(i)
                unique = self._is_slug_unique(proposed_slug)
                i += 1
            return proposed_slug
        return ""

    def _is_slug_unique(self, slug=False, exclude_self=False):
        for model in self._slug_models:
            search_query = [("slug_id", "=", slug)]
            if self._name == model and exclude_self:
                search_query.append(("id", "!=", self.id))
            existing_model = self.env[model].search(search_query)
            if existing_model:
                return False
        return True
