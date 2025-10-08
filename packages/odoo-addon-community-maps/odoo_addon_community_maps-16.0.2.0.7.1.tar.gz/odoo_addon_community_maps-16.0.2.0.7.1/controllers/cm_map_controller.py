
from odoo.addons.base_rest.controllers import main
from odoo.http import route, request


class CmMapController(main.RestController):
    _root_path = "/api/private/maps/"
    _collection_name = "community_maps.form_services"
    _default_auth = "api_key"

