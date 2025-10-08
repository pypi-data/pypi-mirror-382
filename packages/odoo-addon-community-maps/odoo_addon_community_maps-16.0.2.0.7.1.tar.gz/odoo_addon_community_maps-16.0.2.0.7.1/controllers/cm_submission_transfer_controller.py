
from datetime import datetime
from odoo import _, http
from odoo.http import request

class CmSubmissionTransferController(http.Controller):
    #
    # ROUTER
    #
    @http.route(
        ["/reject-submission-transfer"],
        type="http",
        auth="public",
        website=True,
    )
    def reject_submission_transfer(self, **kwargs):
        # validation
        if 'request' not in kwargs.keys():
            values = {'error': _('The url to perform this action is not correct.')}
            return request.render("community_maps.submission_transfer_page",values)
        request_id = request.env['cm.form.submission.transfer.request'].search([('cm_external_id','=',kwargs['request'])])
        if not request_id:
            values = {'error': _('The url to perform this action is not correct.')}
            return request.render("community_maps.submission_transfer_page",values)
        # mark rejection
        request_id.sudo().with_delay().reject_request_transfer_reject()
        # return success
        values = {
            'success': _('The action has been successfully executed. Your submission will stay at {}').format(
                request_id.origin_place_id.name
            )
        }
        return request.render("community_maps.submission_transfer_page",values)

