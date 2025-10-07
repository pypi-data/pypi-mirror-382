import httpx

from apisix_client.base_models import BaseResponse, converter
from apisix_client.common import Pagging, build_url, pythonize_json_response
from apisix_client.consumer.models import Consumer, ConsumerResponse
from apisix_client.protocols import Logger


class ConsumerClient:
    def __init__(self, httpx_client: httpx.Client, logger: Logger, *args, **kwargs) -> None:
        self._httpx_client: httpx.Client = httpx_client
        self._logger: Logger = logger
        self.url_postfix = "/consumers"

    def create_or_update(self, new_customer: Consumer) -> bool:
        req_body = converter.unstructure(new_customer)
        response = self._httpx_client.put(self.url_postfix, json=req_body)

        if response.status_code == 400:  # Bad request
            self._logger.info(f"Bad request. {response.json()}")
            return False

        return response.status_code in (200, 201)  # Successfully updated or created

    def get(self, name: str) -> BaseResponse[ConsumerResponse] | None:
        r = self._httpx_client.get(build_url(self.url_postfix, name))
        json_response = r.json()

        if "message" in json_response:
            self._logger.info(json_response["message"])
            return None

        return converter.structure(pythonize_json_response(json_response), BaseResponse[ConsumerResponse])

    def get_all(
        self, pagging: Pagging | list | tuple | None = None
    ) -> tuple[BaseResponse[ConsumerResponse], ...]:
        pagging_struct = None
        if pagging is not None:
            pagging_struct = Pagging(*pagging) if isinstance(pagging, list | tuple) else pagging

        params = {} if pagging_struct is None else pagging_struct.as_dict
        r = self._httpx_client.get(self.url_postfix, params=params)
        json_response = r.json()

        return tuple(
            converter.structure(pythonize_json_response(i), BaseResponse[ConsumerResponse])
            for i in json_response["list"]
        )

    def delete(self, username: str) -> int:
        r = self._httpx_client.delete(build_url(self.url_postfix, username))
        json_response = r.json()
        if "message" in json_response:
            self._logger.info(json_response["message"])
            return 0

        return int(json_response["deleted"])

    def count(self) -> int:
        r = self._httpx_client.get(self.url_postfix)
        json_response = r.json()

        return int(json_response["total"])
