import json
from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.tools.translate import _
from odoo.http import Response


class CmMapService(Component):
    _inherit = "base.rest.service"
    _name = "cm.map.forms.service"
    _collection = "community_maps.form_services"
    _usage = "forms"
    _description = """
      Map Service
  """

    @restapi.method(
        [(["/"], "POST")],
        auth="api_key"
    )
    def submit(self):
        params = self.request.get_json_data()
        if params:
            if (
                "type" in params.keys()
                and "slug" in params.keys()
                and "data" in params.keys()
            ):
                # PLACE SUBMISSION
                if params["type"] == "place":
                    ok_response = self._forms_submission(
                        params["slug"], params)
                    if ok_response:
                        return ok_response
                # PROPOSAL SUBMISSION
                if params["type"] == "suggestPlace":
                    return_data = self._forms_proposal(params)
                    if return_data:
                        # Create submission at same time of creating proposal
                        if (
                            return_data[
                                "proposal_form"
                            ].generate_submission_in_proposal
                        ):
                            # overwrite slug param with place slug
                            # in order to create correct submission
                            params["slug"] = return_data["place"].slug_id
                            self._forms_submission(
                                return_data["place"].slug_id,
                                params,
                                return_data[
                                    "proposal_form"
                                ].json_submission_fields_map,
                            )
                        return return_data["ok_response"]

        return Response(
            json.dumps({"message": _("Bad request.")}),
            status=400,
            content_type="application/json",
        )

    def _forms_submission(
        self,
        place_slug,
        params,
        submission_fields_map=False
    ):
        place_records = self.env["cm.place"].search(
            [
                ("slug_id", "=", place_slug),
                ("type", "in", ["place", "place_proposal"]),
            ]
        )
        if place_records:
            place_record = place_records[0]
            # shareable
            if "mapUrl" in params.keys():
                params["data"]["shareable_url_base"] = params["mapUrl"]
            if "child_place" in params.keys():
                params["data"]["child_place"] = params["child_place"]
            # submit
            place_submission = place_record.submit_place_form(
                params["data"], submission_fields_map
            )
            # email
            if place_record.submission_ok_email_template_id:
                place_record.submission_ok_email_template_id.send_mail(
                    res_id=place_submission.id,
                    force_send=True,
                    email_layout_xmlid="mail.mail_notification_layout",
                )
            # client mesage
            return {"message": place_record.submission_ok_message}
        return False

    def _forms_proposal(self, params={}):
        if "mapSlug" in params.keys():
            map_record = self.env["cm.map"].search(
                [("slug_id", "=", params["mapSlug"])]
            )
            category_record = self.env["cm.place.category"].search(
                [("slug_id", "=", params["slug"])]
            )
            if map_record and category_record:
                # shareable
                if "mapUrl" in params.keys():
                    params["data"]["shareable_url_base"] = params["mapUrl"]
                # submit
                return_data = map_record.submit_place_proposal(
                    params["data"], category_record
                )
                proposal_submission = return_data["submission"]
                # email
                if category_record.submission_ok_email_template_id:
                    submission_ok_email_template = (
                        category_record.submission_ok_email_template_id
                    )
                else:
                    submission_ok_email_template = (
                        map_record.submission_ok_email_template_id
                    )
                if submission_ok_email_template:
                    submission_ok_email_template.send_mail(
                        res_id=proposal_submission.id,
                        force_send=True,
                        email_layout_xmlid="mail.mail_notification_layout",
                    )
                # client message
                if category_record.submission_ok_message:
                    ok_msg = category_record.submission_ok_message
                else:
                    ok_msg = map_record.submission_ok_message
                return {
                    "ok_response": {"message": ok_msg},
                    "place": return_data["place"],
                    "proposal_form": return_data["proposal_form"],
                }
        return False
