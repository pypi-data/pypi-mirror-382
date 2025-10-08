import json
from datetime import datetime
from jinja2 import Template
from odoo import models, api, fields
from odoo.tools.translate import _
from odoo.addons.community_maps.models.cm_utils import CmUtils
from odoo.exceptions import UserError, ValidationError


class CmPlace(models.Model):
    _name = 'cm.place'

    _inherit = ["cm.slug.id.mixin", "mail.thread"]

    _labeled_meta_formats = ['uri', 'progress']

    _order = "id desc"

    name = fields.Char(string=_("Name"), required=True)
    active = fields.Boolean(string=_("Active"), default=True)
    company_id = fields.Many2one(
        'res.company', required=False, default=lambda self: self.env.company
    )
    type = fields.Selection([
        ('place', _("Place")),
        ('place_proposal', _("Place proposal"))
    ], string=_("Type"), default=lambda self: self.env.context.get('type'))
    lat = fields.Char(string=_("Latitude"))
    lng = fields.Char(string=_("Longitude"))
    status = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('movement_request','Movement request'),
        ('published', 'Published')
    ], default='draft', required=True, string=_("Status"))
    map_id = fields.Many2one('cm.map', string=_("Related map"))
    form_model_id = fields.Many2one('cm.form.model', string=_("Form"))
    place_category_id = fields.Many2one(
        'cm.place.category', string=_("Category"))
    presenter_model_id = fields.Many2one(
        'cm.presenter.model', string=_("Presenter"))
    place_presenter_metadata_ids = fields.One2many(
        'cm.place.presenter.metadata',
        'place_id',
        string=_("Presenter metadata"))
    crowdfunding_type = fields.Selection(
        selection=CmUtils.get_system_crowdfunding_types_selection(),
        string=_("Crowdfunding type"),
        compute="_get_crowdfunding_type",
        store=True)
    form_submission_ids = fields.One2many(
        'crm.lead',
        'place_id',
        string=_("Submissions"),
        domain=[('submission_type', '=', 'place_submission')]
    )
    completed_percentage = fields.Integer(
        string=_("% Completed"),
        compute="_get_completed_percentage",
        store=True)
    completed_percentage_live = fields.Integer(
        string=_("% Completed"),
        compute="_get_completed_percentage_live",
        store=True)
    submissions_target = fields.Integer(string=_("Submission target"))
    allow_contributions_beyond_goal = fields.Boolean(
        string=_("Allow submissions/contributions after target goal is reached"),
        default=False
    )
    has_active_service = fields.Boolean(string=_("Place with active service"))
    address_txt = fields.Char(string=_("Address text"))
    allow_filter_by_status = fields.Boolean(
        string=_('"Active" filter'),
        compute="_get_allow_filter_by_status",
        store=True)
    invoiced_target = fields.Float(
        string=_("Invoicing target")
    )
    total_committed_invoicing = fields.Float(
        string=_("Total amount commited (invoicing)"),
        compute="_get_total_committed_invoicing",
        store=True)
    total_committed_submissions = fields.Float(
        string=_("Total amount commited (submissions)"),
        compute="_get_total_committed_submissions",
        store=True)
    proposal_form_submission_id = fields.Many2one(
        'crm.lead',
        string=_("Proposal submission"),
        ondelete='restrict')
    submission_ok_message = fields.Text(
        string=_("Successful message"),
        compute='_get_submission_ok_message',
        store=False)
    submission_ok_email_template_id = fields.Many2one(
        'mail.template',
        compute='_get_submission_ok_email_template_id',
        string=_("Successful email template"),
        store=False)
    crowdfunding_notification_ids = fields.One2many(
        'cm.crowdfunding.notification',
        'place_id',
        string=_("Notifications"))
    filter_mids = fields.Many2many(
        'cm.filter',
        'cm_places_filters',
        'place_id',
        'filter_id',
        string=_("Custom filters")
    )
    marker_color = fields.Many2one(
        'cm.filter',
        string=_("Overwritte category color with"),
    )
    # Interaction method
    interaction_method = fields.Selection(selection=[
        ('none', _('None')),
        ('form', _('Form')),
        ('external_link', _('External link')),
        ('both', _('Both')),
    ], default='form', required=True, string=_("Interaction method"))
    # TODO: To be deleted
    external_link_url = fields.Char(
        string=_("External link URL"), translate=True)
    external_link_target = fields.Selection(selection=[
        ('_blank', _('Open in a new tab')),
        ('_top', _('Open in the same page'))
    ], default='_blank', required=True, string=_("Target link"))
    external_link_cta_txt = fields.Char(
        string=_("Call-to-action text for external link button (default)"),
        help=_(
            'It will be used when place interaction method is set to "External link"'
        ),
        translate=True,
    )
    # end TODO
    external_link_ids = fields.One2many(
        'cm.place.external.link',
        'place_id',
        string=_("External links")
    )
    social_shareable_url = fields.Char(string=_("Social shareable url"),translate=True)
    # Child places
    child_place_ids = fields.One2many("cm.place.child","parent_place_id",string="Child places")
    selected_child_place_ids = fields.One2many("cm.place.child","origin_place_id",string="Selected Child places")
    child_place_submission_candidate_ids = fields.One2many(
        "crm.lead",
        string="Submission candidates to transfer",
        compute="_compute_child_place_submission_candidate_ids",
        store=False
    )
    can_send_submission_transfer_notification = fields.Boolean(
        compute="_get_can_send_submission_transfer_notification",
        store=False
    )
    pending_form_submission_transfer_request_ids = fields.One2many(
        'cm.form.submission.transfer.request',
        'destination_place_id',
        string=_("Pending submission transfer requests"),
        domain=[("status","=","pending")]
    )
    accepted_form_submission_transfer_request_ids = fields.One2many(
        'cm.form.submission.transfer.request',
        'destination_place_id',
        string=_("Accepted submission transfer requests"),
        domain=[("status","=","accepted")]
    )
    rejected_form_submission_transfer_request_ids = fields.One2many(
        'cm.form.submission.transfer.request',
        'destination_place_id',
        string=_("Rejected submission transfer requests"),
        domain=[("status","=","rejected")]
    )
    place_image_ids = fields.One2many(
        'cm.place.image',
        'place_id',
        string=_("Images")
    )

    @api.depends('child_place_ids')
    def _compute_child_place_submission_candidate_ids(self):
        for record in self:
            submission_candidates = self.env['crm.lead']
            for child_place in record.child_place_ids:
                submission_candidates = submission_candidates | child_place.child_place_id.form_submission_ids
            record.child_place_submission_candidate_ids = submission_candidates

    def _get_context_place_type(self):
        for record in self:
            record.type = self.env.context.type

    # system
    def unlink(self):
        for record in self:
            form_submission_ids = self.env['crm.lead'].search(
                [('place_id', '=', record.id)])
            if form_submission_ids or record.proposal_form_submission_id:
                raise ValidationError(
                    _("You can't delete. Some submissions relate on \
                    this info. Archive instead.")
                )
            super(CmPlace, record).unlink()

    @api.constrains('submissions_target')
    def _recompute_place_progress(self):
        for record in self:
            for submission in record.form_submission_ids:
                submission.constrain_revenue()

    @api.depends('form_submission_ids', 'form_submission_ids.active')
    def _get_total_committed_invoicing(self):
        for record in self:
            total = 0
            if record.form_submission_ids:
                for submission in record.form_submission_ids.filtered(
                    lambda submission: submission.active == True
                ):
                    total += submission.expected_revenue
            record.total_committed_invoicing = total

    @api.depends('form_submission_ids', 'form_submission_ids.active')
    def _get_total_committed_submissions(self):
        for record in self:
            record.total_committed_submissions = len(
                record.form_submission_ids.filtered(
                    lambda submission: submission.submission_type ==
                    'place_submission' and submission.active == True
                )
            )

    @api.depends('form_submission_ids', 'form_submission_ids.active')
    def _get_completed_percentage(self):
        for record in self:
            if (
                record.crowdfunding_type == 'invoicing_amount' and
                record.invoiced_target
            ):
                record.completed_percentage = int(
                    record.total_committed_invoicing/record.invoiced_target*100
                )
            if (
                record.crowdfunding_type == 'submission_amount' and
                record.submissions_target
            ):
                record.completed_percentage = int(
                    record.total_committed_submissions/record.submissions_target*100
                )
            for notification in record.crowdfunding_notification_ids:
                if record.completed_percentage < notification.percentage:
                    notification.unlink()

    @api.depends('form_submission_ids', 'form_submission_ids.active')
    def _get_completed_percentage_live(self):
        for record in self:
            if (
                record.crowdfunding_type == 'invoicing_amount' and
                record.invoiced_target
            ):
                record._get_total_committed_invoicing()
                record.completed_percentage_live = int(
                    record.total_committed_invoicing/record.invoiced_target*100
                )
            if (
                record.crowdfunding_type == 'submission_amount' and
                record.submissions_target
            ):
                record._get_total_committed_submissions()
                record.completed_percentage_live = int(
                    record.total_committed_submissions/record.submissions_target*100
                )

    @api.depends('map_id')
    def _get_crowdfunding_type(self):
        for record in self:
            if record.map_id:
                record.crowdfunding_type = record.map_id.crowdfunding_type

    @api.depends('map_id')
    def _get_allow_filter_by_status(self):
        for record in self:
            if record.map_id:
                record.allow_filter_by_status = \
                    record.map_id.allow_filter_by_status

    @api.depends('child_place_ids')
    def _get_can_send_submission_transfer_notification(self):
        for record in self:
            pending_childs = record.child_place_ids.filtered(lambda child: not child.request_date and child.origin_place_id)
            if pending_childs:
                record.can_send_submission_transfer_notification = True
            else:
                record.can_send_submission_transfer_notification = False

    # place config preselection
    @api.onchange('map_id')
    def _get_config_relations_attrs(self):
        self.ensure_one()
        allowed_form_model_ids = self.map_id.allowed_form_model_mids
        allowed_place_category_ids = self.map_id.allowed_place_category_mids
        allowed_presenter_model_ids = self.map_id.allowed_presenter_model_mids
        allowed_filter_group_mids_map =  \
            self.map_id.allowed_filter_group_mids.mapped(
                lambda r: r.filter_ids.mapped('id'))
        allowed_filter_group_mids = []
        for filter_group in allowed_filter_group_mids_map:
            allowed_filter_group_mids += filter_group
        return_dict = {
            'domain': {
                'form_model_id': [
                    ('id', 'in', allowed_form_model_ids.mapped('id'))
                ],
                'place_category_id': [
                    ('id', 'in', allowed_place_category_ids.mapped('id'))
                ],
                'presenter_model_id': [
                    ('id', 'in', allowed_presenter_model_ids.mapped('id'))
                ],
                'filter_mids': [
                    (
                        'id',
                        'in',
                        allowed_filter_group_mids
                    )
                ]
            }
        }
        if allowed_form_model_ids:
            self.form_model_id = allowed_form_model_ids[0].id
        if allowed_place_category_ids:
            self.place_category_id = allowed_place_category_ids[0].id
        if allowed_presenter_model_ids:
            self.presenter_model_id = allowed_presenter_model_ids[0].id
        return return_dict

    # PRESENTER
    def _get_create_place_meta(
        self,
        key,
        type,
        format,
        sort_order,
        place_id,
        dataschema,
        uischema
    ):
        return self._get_create_place_meta_dmodel(
            'cm.place.presenter.metadata',
            key, type, format, sort_order, place_id, dataschema, uischema)

    def _get_create_place_meta_dmodel(
        self,
        model,
        key,
        type,
        format,
        sort_order,
        place_id,
        dataschema,
        uischema
    ):
        creation_data = {
            'type': type,
            'key': key,
            'format': format,
            'sort_order': sort_order,
            'place_id': place_id
        }
        query = [
            ('place_id', '=', place_id),
            ('key', '=', key),
            ('type', '=', type),
            ('format', '=', format)
        ]
        place_meta = self.env[model]
        for lang in dataschema.keys():
            if key in dataschema[lang].keys():
                creation_data['value'] = dataschema[lang][key]
                place_meta = CmUtils.update_create_existing_model(
                    self.env[model].with_context(lang=lang), query, creation_data
                )
            if ".label" in key and 'elements' in uischema[lang].keys():
                for element in uischema[lang]['elements']:
                    if element['type'] not in [
                        'InteractionButtons', 'InteractionSocial'
                    ]:
                        if element['type'] in ['HorizontalLayout', 'Group']:
                            for sub_element in element['elements']:
                                if sub_element['type'] not in [
                                    'InteractionButtons', 'InteractionSocial'
                                ]:
                                    label = self._parse_uischema_element_label(
                                        sub_element, key)
                                    if label:
                                        creation_data['value'] = label
                        else:
                            label = self._parse_uischema_element_label(
                                element, key)
                            if label:
                                creation_data['value'] = label
                place_meta = CmUtils.update_create_existing_model(
                    self.env[model].with_context(lang=lang), query, creation_data
                )
        if not place_meta:
            place_meta = CmUtils.get_create_existing_model(
                self.env[model], query, creation_data
            )
        return place_meta

    def _parse_uischema_element_label(self, element, key):
        if element['type'] == 'Links':
            for sub_element in element['elements']:
                label = self._get_schema_meta_label_from_key(
                    sub_element, key)
                if label:
                    return label
        else:
            label = self._get_schema_meta_label_from_key(element, key)
            if label:
                return label
        return False

    def _get_schema_meta_label_from_key(self, element, key):
        meta_key = str(key).replace('.label', '')
        if (
            element['scope'] == '#/properties/'+meta_key and
            "label" in element.keys()
        ):
            return element['label']
        return False

    # public method to be called from erppeek after import
    def build_presenter_metadata_ids(self):
        self._build_presenter_metadata_ids()
        return True

    @api.onchange('presenter_model_id')
    def _build_presenter_metadata_ids(
        self,
        presenter_model_relation='presenter_model_id',
        metas_relation='place_presenter_metadata_ids'
    ):
        self.ensure_one()
        try:
            place_id = self._origin.id
        except Exception:
            place_id = self.id
        place_presenter_metadata_ids = []
        presenter_model_id = getattr(self, presenter_model_relation)
        if presenter_model_id:
            presenter_json_schema = json.loads(presenter_model_id.json_schema)
            presenter_json_dataschema = {}
            presenter_json_uischema = {}
            for lang in self.env["res.lang"].get_installed():
                presenter_json_dataschema[lang[0]] = json.loads(
                    presenter_model_id.with_context(lang=lang[0]).json_dataschema
                )
                presenter_json_uischema[lang[0]] = json.loads(
                    presenter_model_id.with_context(lang=lang[0]).json_uischema
                )
            current_meta_ids = []
            sort_order = 0
            for meta_key in presenter_json_schema['properties'].keys():
                meta_format = ''
                if (
                    'format' in
                    presenter_json_schema['properties'][meta_key].keys()
                ):
                    meta_format = \
                        presenter_json_schema['properties'][meta_key]['format']
                if meta_format in self._labeled_meta_formats:
                    place_meta = self._get_create_place_meta(
                        meta_key+'.label',
                        'string',
                        meta_format+'.label',
                        sort_order,
                        place_id,
                        presenter_json_dataschema,
                        presenter_json_uischema
                    )
                    current_meta_ids.append(place_meta.id)
                    place_presenter_metadata_ids.append((4, place_meta.id))
                    sort_order += 1
                if meta_key not in ['progress', 'how_to_arrive']:
                    place_meta = self._get_create_place_meta(
                        meta_key,
                        presenter_json_schema['properties'][meta_key]['type'],
                        meta_format,
                        sort_order,
                        place_id,
                        presenter_json_dataschema,
                        presenter_json_uischema
                    )
                    current_meta_ids.append(place_meta.id)
                    place_presenter_metadata_ids.append((4, place_meta.id))
                    sort_order += 1
            # delete metas not in presenter
            for metadata in self.place_presenter_metadata_ids:
                if metadata.id not in current_meta_ids:
                    place_presenter_metadata_ids.append((2, metadata.id))
        else:
            # delete all metas
            for metadata in self.place_presenter_metadata_ids:
                place_presenter_metadata_ids.append((2, metadata.id))
        # create metas
        setattr(self, metas_relation, place_presenter_metadata_ids)

    # DATAMODEL / API
    def _build_base_datamodel(self,child=False):
        if self.marker_color:
            marker_color = self.marker_color.get_datamodel_dict().get(
                'markerColor', {}
            )
        else:
            marker_color = self._get_category_data_datamodel_dict().get(
                'markerColor', {}
            )
        if child:
            place_lat = child.lat
            place_lng = child.lng
            place_slug_id = child.slug_id
        else:
            place_lat = self.lat
            place_lng = self.lng
            place_slug_id = self.slug_id
        place_dict = {
            'name': self.name,
            'slug': place_slug_id,
            'submit_slug': self.slug_id,
            'map_slug': self.map_id.slug_id,
            'markerColor': marker_color,
            'category_slug': self.place_category_id.slug_id,
            'category_data': self._get_category_data_datamodel_dict(),
            'category': self.place_category_id.name,
            'interaction_method': self.interaction_method,
            'goalProgress': None,
            'goalTarget': None,
            'form_slug': None,
            # TODO: To be removed
            'external_link_url': None,
            'external_link_target': None,
            'external_link_cta_txt': None,
            # end TODO
            'filters': self._get_filters_datamodel_dict(),
            'filters_data': self._get_filters_data_datamodel_dict(),
            'lat': place_lat,
            'lng': place_lng,
            'address': None,
            'submission_number': int(self.total_committed_submissions),
            'social_shareable_url': self.social_shareable_url,
            'images': self.place_image_ids.get_datamodel_dict(),
        }

        if self.address_txt:
            place_dict['address'] = self.address_txt
        if self.allow_filter_by_status:
            place_dict['active'] = self.has_active_service
        if self.crowdfunding_type != 'none':
            if (
                self.completed_percentage > 100
                and not self.allow_contributions_beyond_goal
            ):
                completed_percentage_return = 100
            else:
                completed_percentage_return = self.completed_percentage
            place_dict['goalProgress'] = completed_percentage_return
            if self.crowdfunding_type == 'invoicing_amount':
                place_dict['goalTarget'] = self.invoiced_target
            elif self.crowdfunding_type == 'submission_amount':
                place_dict['goalTarget'] = self.submissions_target
        if self.interaction_method in ['form', 'both'] and self.form_model_id:
            place_dict['form_slug'] = self.form_model_id.slug_id
        if self.interaction_method in ['external_link', 'both']:
            place_dict['external_links'] = []
            if self.external_link_ids:
                for link in self.external_link_ids:
                    place_dict['external_links'].append(
                        link.get_datamodel_dict())
                # TODO: To be removed
                place_dict['external_link_url'] = self.external_link_ids[0].url
                place_dict['external_link_cta_txt'] = self.external_link_ids[0].name
                place_dict['external_link_target'] = self.external_link_ids[0].target
                # end TODO
        return place_dict

    def _get_filters_datamodel_dict(self):
        filters = []
        for filter in self.filter_mids:
            filters.append(filter.slug_id)
        return filters

    def _get_filters_data_datamodel_dict(self):
        filters = []
        for filter in self.filter_mids:
            filters.append(filter.get_datamodel_dict())
        return filters

    def _get_category_data_datamodel_dict(self):
        return self.place_category_id.get_datamodel_dict()

    def _build_social_items_json(self):
        items = []
        if self.map_id.social_item_ids:
            for item in self.map_id.social_item_ids:
                item_datamodel = item.get_datamodel_dict(self)
                #if we have a multiple social item we merge the array of items into result
                if item.type == 'multiple_social':
                    items = items + item_datamodel
                else:
                    items.append(item_datamodel)
        return items

    def _build_presenter_schemadata_json(self, presenter_model_relation='presenter_model_id', metas_relation='place_presenter_metadata_ids'):
        presenter_model_id = getattr(self, presenter_model_relation)
        if not presenter_model_id:
            return False

        presenter_schemadata_dict = {}
        presenter_json_schema = json.loads(presenter_model_id.json_schema)
        for meta_key, meta_val in presenter_json_schema['properties'].items():
            if isinstance(meta_val, dict) and meta_val.get('format') == 'progress':
                presenter_schemadata_dict['progress'] = \
                    min(100, self.completed_percentage)
            else:
                place_meta_ids = getattr(self, metas_relation, None)
                place_meta = place_meta_ids.filtered(
                    lambda r: r.key == meta_key) if place_meta_ids else False

                if not place_meta:
                    continue

                if place_meta[0].value:
                    meta_val_template = Template(place_meta[0].value)
                    presenter_schemadata_dict[meta_key] = \
                        meta_val_template.render(
                            self._build_base_datamodel())
                else:
                    presenter_schemadata_dict[meta_key] = None
        return presenter_schemadata_dict

    def _build_presenter_schema_json(
        self,
        presenter_model_relation='presenter_model_id'
    ):
        presenter_model_id = getattr(self, presenter_model_relation)
        if presenter_model_id:
            return json.loads(presenter_model_id.json_schema)
        return False

    def _build_presenter_uischema_json(
        self,
        presenter_model_relation='presenter_model_id'
    ):
        presenter_model_id = getattr(self, presenter_model_relation)
        if presenter_model_id:
            presenter_json_schema = json.loads(presenter_model_id.json_schema)
            presenter_json_uischema = json.loads(
                presenter_model_id.json_uischema)
            for element in presenter_json_uischema['elements']:
                if element['type'] in ['HorizontalLayout', 'Group']:
                    for sub_element in element['elements']:
                        self._parse_uischema_element(
                            sub_element, presenter_json_schema)
                else:
                    self._parse_uischema_element(
                        element, presenter_json_schema)
            return presenter_json_uischema
        return False

    def _parse_uischema_element(self, element, presenter_json_schema):
        if element['type'] == 'Links':
            for sub_element in element['elements']:
                meta_label = self._get_meta_label_from_scope(
                    presenter_json_schema, sub_element['scope'])
                if meta_label:
                    meta_label_template = Template(meta_label)
                    sub_element['label'] = meta_label_template.render(
                        self._build_base_datamodel())
        elif element['type'] not in [
            'InteractionSocial', 'InteractionButtons'
        ]:
            meta_label = self._get_meta_label_from_scope(
                presenter_json_schema, element['scope'])
            if meta_label:
                meta_label_template = Template(meta_label)
                element['label'] = meta_label_template.render(
                    self._build_base_datamodel())

    def _get_meta_label_from_scope(self, json_schema, scope):
        meta_key = str(scope).replace('#/properties/', '')

        meta_val = json_schema['properties'].get(meta_key)
        if not isinstance(meta_val, dict):
            return False

        meta_format = json_schema['properties'][meta_key].get('format')
        if meta_format in self._labeled_meta_formats:
            place_meta = self.place_presenter_metadata_ids.filtered(
                lambda r: r.key == meta_key+'.label')
            if place_meta:
                return place_meta[0].value
        return False

    # api datamodel
    def get_datamodel_dict(self, single_view=False,child=False):
        place_dict = self._build_base_datamodel(child)
        if single_view:
            place_dict['presenterTextColor'] = self.presenter_model_id.text_color
            place_dict['schemaData'] = self._build_presenter_schemadata_json()
            place_dict['jsonSchema'] = self._build_presenter_schema_json()
            place_dict['uiSchema'] = self._build_presenter_uischema_json()
            place_dict['socialItems'] = self._build_social_items_json()
        return place_dict

    # UI actions
    def accept_place_proposal_workflow_action(self):
        # TODO: Do we mark the lead as won?!?
        for record in self:
            record.write({'type': 'place'})

    def publish_place_workflow_action(self):
        for record in self:
            record.write({'status': 'published'})

    def unpublish_place_workflow_action(self):
        for record in self:
            record.write({'status': 'draft'})

    def send_submission_transfer_notification_workflow_action(self):
        for pending_child in self.child_place_ids.filtered(lambda child: not child.request_date and child.origin_place_id  ):
            pending_child.write({
                'request_date': datetime.now()
            })
            for submission in pending_child.origin_place_id.form_submission_ids:
                request = self.env['cm.form.submission.transfer.request'].create({
                    'submission_id': submission.id,
                    'origin_place_id': pending_child.origin_place_id.id,
                    'destination_place_id': pending_child.parent_place_id.id,
                    'child_place_id': pending_child.id,
                    'request_date': datetime.now(),
                    'company_id': self.company_id.id
                })
                request.request_transfer_reject()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "title": _("Notification successful"),
                "message": _("New users have been notified requesting their submission movement."),
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            }
        }

    # Form Submission
    def submit_place_form(self, data, submission_fields_map=False):
        # Submission creation
        creation_dict = {
            'name': self.name + " (Place Submission)",
            'submission_type': 'place_submission',
            'place_id': self.id,
            'team_id': self.map_id.crm_team_id.id,
            'company_id': self.map_id.company_id.id
        }
        if 'shareable_url_base' in data.keys():
            creation_dict['shareable_url_base'] = data['shareable_url_base']
        if 'child_place' in data.keys():
            place_childs = self.env['cm.place.child'].search([('slug_id','=',data['child_place'])])
            if place_childs:
                creation_dict['child_place_id'] = place_childs[0].id
        submission = self.env['crm.lead'].create(creation_dict)
        # Metadata creation
        if submission_fields_map:
            fields_map = submission_fields_map
        else:
            fields_map = self.form_model_id.json_submission_fields_map
        submission.create_submission_metadata(
            data=data,
            fields_map=fields_map
        )
        # submission overwrite
        submission.write({
            'name': submission.name + " #" + str(submission.id)
        })
        # Constrain probability
        submission.constrain_revenue()
        self.crowdfunding_notify_if_must(submission.id)

        if self.form_model_id.follower_partner_id:
            submission.message_subscribe(
                [self.form_model_id.follower_partner_id.id])

        body = "<p>"+_("New place submission has been made!")+"</p>"
        body += submission._get_metadata_as_msg()

        submission.message_post(
            subject=submission.name+" notification",
            body=body,
            subtype_id=None,
            message_type="notification",
            subtype_xmlid='mail.mt_comment'
        )
        return submission

    def crowdfunding_notify_if_must(self,submission_id=False):
        for request in self.map_id.crowdfunding_notification_request_ids:
            if self.completed_percentage >= request.percentage:
                existing_notification = self.env['cm.crowdfunding.notification'].search(
                    [
                        ('place_id', '=', self.id),
                        ('percentage', '>=', request.percentage),
                    ]
                )
                if existing_notification:
                    return False
                else:
                    self.crowdfunding_notifications(request,submission_id)
                    self.env['cm.crowdfunding.notification'].create({
                        'place_id': self.id,
                        'percentage': request.percentage
                    })
                    return True
        return False

    def crowdfunding_notifications(self, request, submission_id=False, submissions_notified=False):
        # Notify admins
        if request.notify_admins:
            template = request.template_admins
            for admin in request.map_id.admins_to_notify:
                template.with_context({'email_to': admin.email,'lang':admin.lang}).send_mail(
                    res_id=self.id,
                    force_send=True,
                    email_layout_xmlid="mail.mail_notification_layout",
                )
        # Notify submissions
        if request.notify_submissions:
            template = request.template_submissions
            for submission in self.form_submission_ids:
                # This conditional avoids sending crowdfunding notification to a newly created submission.
                # They'll receive the general autoresponder
                if submission.id != submission_id or not submission_id:
                    if not submissions_notified or submission.id not in submissions_notified:
                        template.send_mail(
                            res_id=submission.id,
                            force_send=True,
                            email_layout_xmlid="mail.mail_notification_layout",
                        )

    @api.depends('form_model_id')
    def _get_submission_ok_message(self):
        for record in self:
            try:
                ok_message = record.form_model_id.submission_ok_message
            except Exception:
                ok_message = False
            record.submission_ok_message = ok_message

    @api.depends('form_model_id')
    def _get_submission_ok_email_template_id(self):
        for record in self:
            try:
                email_template = \
                    record.form_model_id.submission_ok_email_template_id
            except Exception:
                email_template = False
            record.submission_ok_email_template_id = email_template.id

    # ACTIONS
    def archive_workflow_action(self):
        for record in self:
            record.write({'active': False})

    def unarchive_workflow_action(self):
        for record in self:
            record.write({'active': True})

    def crowdfunding_notify_if_must_action(self):
        for place_id in self.env.context['active_ids']:
            selected_place = self.env['cm.place'].browse(place_id)
            selected_place.crowdfunding_notify_if_must()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "title": _("Crowdfunding notifications sent"),
                "message": _("An email has been sent to places reaching a notification level if wasn't already sent."),
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
    def get_collect_child_places_wizard_action(self):
        selected_places = []
        for place_id in self.env.context['active_ids']:
            selected_place = self.env['cm.place'].browse(place_id)
            # Validation
            if selected_place.child_place_ids:
                raise UserError(_(
                    "You're trying to append a child ({child_name}) but this place has already childs."
                ).format(
                    child_name=selected_place.name
                ))
            if selected_place.selected_child_place_ids:
                raise UserError(_(
                    "You're trying to append a child place ({child_name}) that belongs already to another parent ({parent_name})"
                ).format(
                    child_name=selected_place.name,
                    parent_name=selected_place.selected_child_place_ids[0].parent_place_id.name
                ))
            selected_places.append((4,place_id))
        wizard = self.env["cm.collectchildplaces.wizard"].create({'collected_child_ids':selected_places})
        return {
            "type": "ir.actions.act_window",
            "name": _("Collect child places"),
            "res_model": "cm.collectchildplaces.wizard",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "res_id": wizard.id,
        }
