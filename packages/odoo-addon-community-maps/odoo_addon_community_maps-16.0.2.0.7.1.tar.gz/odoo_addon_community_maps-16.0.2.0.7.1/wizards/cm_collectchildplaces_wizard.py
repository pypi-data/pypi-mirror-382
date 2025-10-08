from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

class CmCollectChildPlacesWizard(models.TransientModel):
    _name = "cm.collectchildplaces.wizard"
    _description = "Collect places to be childs of a new place"

    collect_behaviour = fields.Selection([
        ("replicate","Replicate same place on multiple locations"),
        ("absorb_delete","Absorb places on another and delete the initial ones.")
    ], string=_("Collect behaviour"))
    destination_place_id = fields.Many2one("cm.place",string=_("Destination place"))
    collected_child_ids = fields.Many2many(
        comodel_name="cm.place", string="Collected child places", domain=[]
    )
    request_users_for_submission_transfer = fields.Boolean(string=_("Send email to users asking to move their submission to destination place"))

    def _collect_child_place(self,collected_child):
        creation_dict = {
            'name': collected_child.name,
            'parent_place_id': self.destination_place_id.id,
            'origin_place_id': collected_child.id
        }
        if self.collect_behaviour == 'replicate':
            creation_dict.update({
                'lat': collected_child.lat,
                'lng': collected_child.lng
            })
        c_child_place = self.env['cm.place.child'].create(
            creation_dict
        )
        c_child_place.setup_slug_id()
        collected_child.write({
            'status': 'movement_request'
        })
        collected_child.message_post(
            body=_("REQUEST: place transfer. Destination: #{destination_id} {destination_name}").format(
                destination_id=self.destination_place_id.id,
                destination_name=self.destination_place_id.name
            )
        )
        self.destination_place_id.message_post(
            body=_("REQUEST: place collection. Collected place: #{origin_id} {origin_name}").format(
                origin_id=collected_child.id,
                origin_name=collected_child.name
            )
        )
        return c_child_place

    def collect_child_places_action(self):
        # validation
        if not self.collected_child_ids:
            raise UserError(_("You must select at least one child in order to perform this action"))
        collected_places_map = self.collected_child_ids.mapped('map_id')
        if len(collected_places_map) > 1:
            raise UserError(_("You are not allowed to collect places from different maps"))
        if collected_places_map.id != self.destination_place_id.map_id.id:
            raise UserError(_("Destination place cannot differ from collected places"))
        # create child places
        for collected_child in self.collected_child_ids:
            self._collect_child_place(collected_child)
        # send notifications
        if self.request_users_for_submission_transfer:
            self.destination_place_id.send_submission_transfer_notification_workflow_action()
        return {
            "type": "ir.actions.act_window",
            "name": self.destination_place_id.name,
            "res_model": "cm.place",
            "view_type": "form",
            "view_mode": "form",
            "target": "current",
            "res_id": self.destination_place_id.id,
        }
