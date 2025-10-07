import httpx

from apisix_client.base_models import BaseResponse
from apisix_client.common import Pagging
from apisix_client.protocols import Logger
from apisix_client.ssl.models import SSLResponse


class SSLClient:
    def __init__(self, httpx_client: httpx.Client, logger: Logger, *args, **kwargs) -> None:
        self._httpx_client: httpx.Client = httpx_client
        self._logger = logger
        self.url_postfix = "/ssls"

    def get(self, id: str) -> BaseResponse[SSLResponse] | None:
        raise NotImplementedError()

    def get_all(self, pagging: Pagging | list | tuple | None = None) -> tuple[BaseResponse[SSLResponse], ...]:
        raise NotImplementedError()

    def delete(self, id: str) -> bool:
        raise NotImplementedError()

    def count(self) -> int:
        raise NotImplementedError()
