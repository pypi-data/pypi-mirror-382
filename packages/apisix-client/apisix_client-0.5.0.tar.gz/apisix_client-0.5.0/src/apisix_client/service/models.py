import attrs

from apisix_client.base_models import BaseSchema, response_class_factory
from apisix_client.common.converter import str_or_none
from apisix_client.plugin.models import Plugins
from apisix_client.upstream.models import Upstream


@attrs.define()
class Service(BaseSchema):
    plugins: Plugins | None = attrs.field(default=None)
    upstream: Upstream | None = attrs.field(default=None)
    upstream_id: str | None = attrs.field(default=None, converter=str_or_none)
    labels: dict | None = attrs.field(default=None)
    enable_websocket: bool | None = attrs.field(default=False)
    hosts: list[str] | None = attrs.field(default=None)


ServiceResponse = response_class_factory(Service)
