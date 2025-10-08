from odoo import models, api, fields
from odoo.tools.translate import _
from odoo.addons.mail.models import mail_template
from jinja2 import Template

_ITEM_TYPE = [
    ("link", _("Link")),
    ("one_social", _("One social network")),
    ("multiple_social",_("Multiple social networks"))
]
_SOCIAL_NETWORKS = [
    ("email", "Email"),
    ("facebook", "Facebook"),
    ("whatsapp", "WhatsApp"),
    ("telegram", "Telegram"),
    ("x", "X"),
    ("mastodon","Mastodon"),
]

class CmMapSocialItem(models.Model):
    _name = "cm.map.social.item"

    type = fields.Selection(
        selection=_ITEM_TYPE,
        string=_("Item type"),
        default="link"
    )
    social_network = fields.Selection(
        selection=_SOCIAL_NETWORKS,
        string=_("Social Network")
    )
    use_email = fields.Boolean("Email")
    use_facebook = fields.Boolean("Facebook")
    use_whatsapp = fields.Boolean("Whatsapp")
    use_telegram = fields.Boolean("Telegram")
    use_x = fields.Boolean("X")
    use_mastodon = fields.Boolean("Mastodon")
    map_id = fields.Many2one('cm.map',string="Related map")
    message_on_presenter = fields.Text(string="Message on presenter", translate=True)
    message_on_form_submit = fields.Text(string="Message on form submit", translate=True)
    social_networks = fields.Char(string="Social Networks",compute="_compute_social_networks",store=False)
    sort_order = fields.Integer(string=_("Sort order"))

    _order = "sort_order asc"

    @api.depends('type')
    def _compute_social_networks(self):
        for record in self:
            record.social_networks = False
            if record.use_email:
                record.social_networks = "email"
            if record.use_facebook:
                if not record.social_networks:
                    record.social_networks = "facebook"
                else:
                    record.social_networks += ", facebook"
            if record.use_whatsapp:
                if not record.social_networks:
                    record.social_networks = "whatsapp"
                else:
                    record.social_networks += ", whatsapp"
            if record.use_telegram:
                if not record.social_networks:
                    record.social_networks = "telegram"
                else:
                    record.social_networks += ", telegram"
            if record.use_x:
                if not record.social_networks:
                    record.social_networks = "x"
                else:
                    record.social_networks += ", x"
            if record.use_mastodon:
                if not record.social_networks:
                    record.social_networks = "mastodon"
                else:
                    record.social_networks += ", mastodon"

    def get_datamodel_dict(self,place):
        if self.type == 'link':
            return {'link': True}
        else:
            # setup messages
            if self.message_on_form_submit:
                message_on_form_submit = Template(self.message_on_form_submit).render(place.get_datamodel_dict(False))
            else:
                message_on_form_submit = None
            if self.message_on_presenter:
                message_on_presenter = Template(self.message_on_presenter).render(place.get_datamodel_dict(False))
                if not message_on_form_submit:
                    message_on_form_submit = message_on_presenter
            else:
                message_on_presenter = None
            # setup social keys
            if self.type == 'one_social':
                return {
                    self.social_network: {
                        'message_on_presenter': message_on_presenter,
                        'message_on_form_submit': message_on_form_submit,
                    }
                }
            elif self.type == 'multiple_social':
                multiple_array = []
                if self.use_email:
                    multiple_array.append({
                        'email': {
                            'message_on_presenter': message_on_presenter,
                            'message_on_form_submit': message_on_form_submit,
                        }
                    })
                if self.use_facebook:
                    multiple_array.append({
                        'facebook': {
                            'message_on_presenter': message_on_presenter,
                            'message_on_form_submit': message_on_form_submit,
                        }
                    })
                if self.use_whatsapp:
                    multiple_array.append({
                        'whatsapp': {
                            'message_on_presenter': message_on_presenter,
                            'message_on_form_submit': message_on_form_submit,
                        }
                    })
                if self.use_telegram:
                    multiple_array.append({
                        'telegram': {
                            'message_on_presenter': message_on_presenter,
                            'message_on_form_submit': message_on_form_submit,
                        }
                    })
                if self.use_x:
                    multiple_array.append({
                        'x': {
                            'message_on_presenter': message_on_presenter,
                            'message_on_form_submit': message_on_form_submit,
                        }
                    })
                if self.use_mastodon:
                    multiple_array.append({
                        'mastodon': {
                            'message_on_presenter': message_on_presenter,
                            'message_on_form_submit': message_on_form_submit,
                        }
                    })
                return multiple_array
        return None

