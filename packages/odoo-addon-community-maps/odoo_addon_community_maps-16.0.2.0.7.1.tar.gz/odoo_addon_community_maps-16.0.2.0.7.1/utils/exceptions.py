from odoo.http import request
from odoo.tools.translate import _

from .commons import CM_ERROR_MSGS


def error_response(exception, status=500):
    """
    Helper function to return a JSON response from an exception
    """
    return request.make_json_response({
        "code": getattr(exception, "code", "UNKNOWN_ERROR"), 
        "message": getattr(exception, "message", str(exception))
    }, status=status)


class RecordNotFound(Exception):
    """
    Exception raised when a record is not found for a model with a given slug
    """

    def __init__(self, model, slug):
        error_info = CM_ERROR_MSGS.get(model, {}).get("not_found")

        if error_info:
            self.code = error_info["code"]
            self.message = error_info["message"] % slug
        else:
            self.code = "UNKNOWN_MODEL_NOT_FOUND"
            self.message = _("No record found for model %s with id %s") % (model, slug)

        super().__init__(self.message)


class MultipleRecordsFound(Exception):
    """
    Exception raised when more than one record is found for a model with a given slug
    """

    def __init__(self, model, slug):
        error_info = CM_ERROR_MSGS.get(model, {}).get("multiple_found")

        if error_info:
            self.code = error_info["code"]
            self.message = error_info["message"] % slug
        else:
            self.code = "UNKNOWN_MODEL_MULTIPLE_FOUND"
            self.message = _("More than one record found for model %s with id %s") % (
                model,
                slug,
            )

        super().__init__(self.message)
