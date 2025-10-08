from odoo.addons.base_rest.controllers import main


class CmMapPrivateController(main.RestController):
    _root_path = "/api/private/"
    _collection_name = "community_maps.private_services"
    _default_auth = "api_key"