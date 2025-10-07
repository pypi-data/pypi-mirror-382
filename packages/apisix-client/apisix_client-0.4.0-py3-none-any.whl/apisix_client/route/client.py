import httpx

from apisix_client.base_models import BaseResponse, converter
from apisix_client.common import Pagging, pythonize_json_response
from apisix_client.protocols import Logger
from apisix_client.route.models import Route, RouteResponse


class RouteClient:
    def __init__(self, httpx_client: httpx.Client, logger: Logger, *args, **kwargs) -> None:
        self._httpx_client: httpx.Client = httpx_client
        self._logger = logger
        self.url_postfix = "/routes"

    def _handle_response_after_create(self, response: httpx.Response) -> str | None:
        if response.status_code == 400:  # Bad request
            self._logger.info(f"Bad request! {response.text}")
            return None

        json_response = response.json()
        return str(json_response["value"]["id"]) if response.status_code in (200, 201) else None

    def create_with_id_generation(self, new_route: Route) -> str | None:
        req_body = converter.unstructure(new_route)
        response = self._httpx_client.post(self.url_postfix, json=req_body)
        return self._handle_response_after_create(response)

    def create_or_update(self, new_route: Route, route_id: str) -> str | None:
        req_body = converter.unstructure(new_route)
        response = self._httpx_client.put(self.url_postfix + f"/{route_id}", json=req_body)
        return self._handle_response_after_create(response)

    def get(self, route_id: str) -> BaseResponse[RouteResponse] | None:
        r = self._httpx_client.get(self.url_postfix + "/" + route_id)
        json_response = r.json()

        if "message" in json_response:
            self._logger.info(json_response["message"])
            return None

        return converter.structure(pythonize_json_response(json_response), BaseResponse[RouteResponse])

    def get_all(
        self, pagging: Pagging | list | tuple | None = None
    ) -> tuple[BaseResponse[RouteResponse], ...]:
        pagging_struct = None
        if pagging is not None:
            pagging_struct = Pagging(*pagging) if isinstance(pagging, list | tuple) else pagging

        params = {} if pagging_struct is None else pagging_struct.as_dict
        r = self._httpx_client.get(self.url_postfix, params=params)
        json_response = r.json()

        return tuple(
            converter.structure(pythonize_json_response(i), BaseResponse[RouteResponse])
            for i in json_response["list"]
        )

    def delete(self, route_id: str) -> bool:
        r = self._httpx_client.delete(self.url_postfix + "/" + route_id)
        json_response = r.json()
        if "message" in json_response:
            self._logger.info(json_response["message"])

        return bool(json_response["deleted"]) if "deleted" in json_response else False

    def count(self) -> int:
        r = self._httpx_client.get(self.url_postfix)
        json_response = r.json()

        return int(json_response["total"])
