from psycopg2 import OperationalError

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

from ..utils.exceptions import RecordNotFound, MultipleRecordsFound, error_response


class CmMapService(Component):
    _inherit = "base.rest.service"
    _name = "cm.map.service"
    _collection = "community_maps.private_services"
    _usage = "maps"
    _description = """
      Map Service
  """

    def _get_unique_record(self, model, slug, domain=[], raise_not_found=True):
        """
        Retrieve a unique record for a given model using a slug identifier and
        additional search criteria.
        Ensure that only one record is found, otherwise raise an error.

        :param model: The model name to search for.
        :param slug: The unique slug identifier of the record.
        :param domain: Additional search criteria.
        :param raise_not_found: Whether to raise an error if no record is found.
        :return: The record found.
        :raises RecordNotFound: If no record is found and raise_not_found is True.
        :raises MultipleRecordsFound: If multiple records are found.
        """
        if not slug:
            raise RecordNotFound(model, None)

        search_domain = [("slug_id", "=", slug)] + domain
        record = self.env[model].search(search_domain)
        if not record:
            if raise_not_found:
                raise RecordNotFound(model, slug)
            return None

        try:
            record.ensure_one()
        except Exception:
            raise MultipleRecordsFound(model, slug)

        return record

    def _handle_request(self, func, *args, **kwargs):
        """
        Handle a request to a service function and handle exceptions.

        :param func: The service function to call.
        :param args: The arguments to pass to the function.
        :param kwargs: The keyword arguments to pass to the function.
        :return: The response from the function or an error response.
        """
        try:
            return func(*args, **kwargs)
        except OperationalError as e:
            e.code = "OPERATIONAL_ERROR"
            e.message = "Database connection error. Please try again later."
            return error_response(e)
        except (RecordNotFound, MultipleRecordsFound) as e:
            status_code = 404 if isinstance(e, RecordNotFound) else 400
            return error_response(e, status_code)
        except (ValueError, KeyError) as e:
            e.code = "BAD_REQUEST"
            e.message = ": ".join([type(e).__name__, str(e)])
            return error_response(e, 400)
        except Exception as e:
            e.code = "DATAMODEL_ERROR"
            return error_response(e)

    def _config_service(self, map_slug):
        """
        Provide configuration data for the specified map.
        
        :param map_slug: The slug of the map.
        :return: The configuration data model dictionary.
        """
        map_record = self._get_unique_record("cm.map", map_slug)
        return map_record.get_config_datamodel_dict()

    def _places_service(self, map_slug):
        """
        Provide places data for the specified map.
        
        :param map_slug: The slug of the map.
        :return: The places data model dictionary.
        """
        map_record = self._get_unique_record("cm.map", map_slug)
        return map_record.get_places_datamodel_dict()

    def _places_single_service(self, map_slug, place_slug=None):
        """
        Provide data for a single place on the specified map. If the place is a
        child place, return the parent place data model dictionary with the child
        place data model dictionary as a child attribute.

        :param map_slug: The slug of the map.
        :param place_slug: The slug of the place.
        :return: The place data model dictionary.
        """
        self._get_unique_record("cm.map", map_slug)  # Ensure map exists and is unique
        place_record = self._get_unique_record(
            "cm.place",
            place_slug,
            [("type", "=", "place"), ("status", "=", "published")],
            raise_not_found=False,
        )
        if place_record:
            return place_record.get_datamodel_dict(single_view=True)

        # if no place record found or exception raised, check for child place
        place_child_record = self._get_unique_record("cm.place.child", place_slug)
        return place_child_record.parent_place_id.get_datamodel_dict(
            single_view=True, child=place_child_record
        )

    @restapi.method(
        [(["/<string:slug>/config"], "GET")],
        auth="api_key",
    )
    def config(self, map_slug):
        """API endpoint to fetch map configuration."""
        return self._handle_request(self._config_service, map_slug)

    @restapi.method([(["/<string:map_slug>/places"], "GET")], auth="api_key")
    def places(self, map_slug):
        """API endpoint to fetch map places."""
        return self._handle_request(self._places_service, map_slug)

    @restapi.method(
        [(["/<string:map_slug>/places/<string:place_slug>"], "GET")], auth="api_key"
    )
    def places_single(self, map_slug, place_slug=None):
        """API endpoint to fetch a single place."""
        return self._handle_request(self._places_single_service, map_slug, place_slug)
