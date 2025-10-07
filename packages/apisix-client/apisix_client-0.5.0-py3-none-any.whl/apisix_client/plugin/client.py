from typing import Tuple

import httpx

from apisix_client.common import Pagging, build_url


class PluginClient:
    def __init__(self, httpx_client: httpx.Client, *args, **kwargs) -> None:
        self._httpx_client: httpx.Client = httpx_client
        self.url_postfix = "/plugins"

    def get_available(self, pagging: Pagging | list | tuple | None = None) -> Tuple[str, ...]:
        pagging_struct = None
        if pagging is not None:
            pagging_struct = Pagging(*pagging) if isinstance(pagging, list | tuple) else pagging

        params = {} if pagging_struct is None else pagging_struct.as_dict
        response = self._httpx_client.get(build_url(self.url_postfix, "list"), params=params)
        return tuple(response.json())

    def reload(self) -> bool:
        response = self._httpx_client.put(build_url(self.url_postfix, "reload"))
        return response.text == "done"
