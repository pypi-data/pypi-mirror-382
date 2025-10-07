import logging

import httpx

from apisix_client.consumer.client import ConsumerClient
from apisix_client.credential.client import CredentialClient
from apisix_client.global_rule.client import GlobalRuleClient
from apisix_client.plugin.client import PluginClient
from apisix_client.protocols import Logger
from apisix_client.route.client import RouteClient
from apisix_client.secret.client import SecretClient
from apisix_client.service.client import ServiceClient
from apisix_client.ssl.client import SSLClient
from apisix_client.upstream.client import UpstreamClient

APISIX_URL_DEFAULT = "http://localhost:9100"

LOGGER = logging.getLogger(__name__)


class ApisixClient:
    def __init__(
        self, base_url: str | None, api_key: str, logger: Logger | None = None, *args, **kwargs
    ) -> None:
        self._base_url = (base_url or APISIX_URL_DEFAULT) + "apisix/admin"
        self._httpx_client = httpx.Client(base_url=self._base_url, headers={"X-API-KEY": api_key})
        self._logger: Logger = LOGGER if logger is None else logger

        self.consumer = ConsumerClient(self._httpx_client, logger=self._logger)
        self.credential = CredentialClient(self._httpx_client, logger=self._logger)
        self.global_rule = GlobalRuleClient(self._httpx_client, logger=self._logger)
        self.plugin = PluginClient(self._httpx_client, logger=self._logger)
        self.route = RouteClient(self._httpx_client, logger=self._logger)
        self.secret = SecretClient(self._httpx_client, logger=self._logger)
        self.service = ServiceClient(self._httpx_client, logger=self._logger)
        self.ssl = SSLClient(self._httpx_client, logger=self._logger)
        self.upstream = UpstreamClient(self._httpx_client, logger=self._logger)
