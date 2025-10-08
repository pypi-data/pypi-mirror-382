from odoo.tools.translate import _


CM_ERROR_MSGS = {
    "cm.map": {
        "not_found": {
            "code": "MAP_NOT_FOUND",
            "message": _("No map record found for id %s"),
        },
        "multiple_found": {
            "code": "MAP_MULTIPLE_FOUND",
            "message": _("More than one map found for %s"),
        },
    },
    "cm.place": {
        "not_found": {"code": "PLACE_NOT_FOUND", "message": _("No place record for id %s")},
        "multiple_found": {
            "code": "PLACE_MULTIPLE_FOUND",
            "message": _("More than one place found for %s"),
        },
    },
    "cm.place.child": {
        "not_found": {
            "code": "PLACE_NOT_FOUND",
            "message": _("No place record for id %s"),
        },
        "multiple_found": {
            "code": "PLACE_MULTIPLE_FOUND",
            "message": _("More than one child place found for %s"),
        },
    },
}
