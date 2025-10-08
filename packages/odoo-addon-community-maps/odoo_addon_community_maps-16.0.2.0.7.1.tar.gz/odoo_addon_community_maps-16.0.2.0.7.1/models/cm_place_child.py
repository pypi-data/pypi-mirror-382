
from datetime import datetime
from odoo import models, api, fields
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

class CmPlaceChild(models.Model):
    _name = 'cm.place.child'

    _inherit = ["cm.slug.id.mixin"]

    name = fields.Char(string=_("Name"), required=True)
    lat = fields.Char(string=_("Latitude"))
    lng = fields.Char(string=_("Longitude"))
    parent_place_id = fields.Many2one("cm.place",string=_("Parent place"),required=True)
    origin_place_id = fields.Many2one(
        "cm.place",
        string=_("Child place"),
        domain=lambda self: [
            ('selected_child_place_ids','=',False),
            ('child_place_ids','=',False)
        ]
    )
    request_date = fields.Datetime(string=_("Request date"))
    transfer_date = fields.Datetime(string=_("Transfer date"))
    form_submission_transfer_request_ids = fields.One2many(
        'cm.form.submission.transfer.request',
        'child_place_id',
        string=_("Related submission transfer requests"),
    )

    @api.onchange('origin_place_id')
    def _onchange_origin_place(self):
        for record in self:
            record.name = record.origin_place_id.name
            record.lat = record.origin_place_id.lat
            record.lng = record.origin_place_id.lng

    @api.constrains('parent_place_id')
    def _constrain_child_place(self):
        for record in self:
            if record.origin_place_id.id == record.parent_place_id.id:
                raise ValidationError(_(
                    "You cannot append a child ({origin_name}) with same reference as current place ({parent_name})."
                ).format(
                    origin_name=record.origin_place_id.name,parent_name=record.parent_place_id.name
                ))
            if record.origin_place_id.child_place_ids:
                raise ValidationError(_(
                    "You're trying to append a child ({origin_name}) to ({destination_name}) but this place has already childs."
                ).format(
                    origin_name=record.origin_place_id.name,
                    destination_name=record.parent_place_id.name,
                ))
            if record.origin_place_id.selected_child_place_ids and record.origin_place_id.selected_child_place_ids[0].parent_place_id.id != record.parent_place_id.id:
                raise ValidationError(_(
                    "You're trying to append a child place ({origin_name}) to ({destination_name}) that belongs already to another parent ({parent_name})"
                ).format(
                    origin_name=record.origin_place_id.name,
                    destination_name=record.parent_place_id.name,
                    parent_name=record.child_place_id.selected_child_place_ids[0].parent_place_id.name
                ))

    def complete_transfer(self):
        # move submission
        for transfer_request in self.form_submission_transfer_request_ids.filtered(lambda request: request.status == 'pending'):
                transfer_request.accept_request_transfer()
        # origin final status (draft and archived)
        self.origin_place_id.write({
            'status': 'draft',
            'active': False
        })
        # notify both places (origin and destination)
        self.origin_place_id.message_post(
            body=_("EXECUTED: place transfer. Destination: #{destination_id} {destination_name}").format(
                destination_id=self.parent_place_id.id,
                destination_name=self.parent_place_id.name
            )
        )
        self.parent_place_id.message_post(
            body=_("EXECUTED: place collection. Collected place: #{origin_id} {origin_name}").format(
                origin_id=self.origin_place_id.id,
                origin_name=self.origin_place_id.name
            )
        )
        # setup transfer_date
        self.write({'transfer_date':datetime.now()})

    def _extend_complete_transfer(self):
        """
        _extend_complete_transfer used to be
        extended on core modules and add more functionallity to this method
        :return: None
        """
        pass
