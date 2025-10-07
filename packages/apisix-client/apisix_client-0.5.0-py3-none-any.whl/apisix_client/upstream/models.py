from typing import Literal

import attrs

from apisix_client.base_models import response_class_factory
from apisix_client.common.converter import int_or_none, str_or_none
from apisix_client.common.models import Timeout

Schemas = Literal["http", "https", "grpc", "grpcs", "tcp", "udp", "tls"]
LoadBalancers = Literal["chash", "roundrobin", "ewma", "leastconn"]


@attrs.define()
class TLS:
    client_cert: str | None = attrs.field(converter=str_or_none, default=None)
    client_key: str | None = attrs.field(converter=str_or_none, default=None)
    client_cert_id: str | None = attrs.field(converter=str_or_none, default=None)


@attrs.define()
class KeepalivePool:
    size: int = attrs.field(converter=int)
    idle_timeout: int = attrs.field(converter=int)
    requests: int = attrs.field(converter=int)


@attrs.define()
class Upstream:
    name: str | None = attrs.field(converter=str_or_none, default=None)
    desc: str | None = attrs.field(converter=str_or_none, default=None)
    type: LoadBalancers | None = attrs.field(default="roundrobin")
    nodes: dict | None = attrs.field(default=None)
    service_name: str | None = attrs.field(converter=str_or_none, default=None)
    discovery_type: str | None = attrs.field(converter=str_or_none, default=None)
    hash_on: str | None = attrs.field(converter=str_or_none, default=None)
    key: str | None = attrs.field(converter=str_or_none, default=None)
    checks: object | None = attrs.field(default=None)
    retries: int | None = attrs.field(converter=int_or_none, default=None)
    retry_timeout: int | None = attrs.field(converter=int_or_none, default=None)
    timeout: Timeout | None = attrs.field(default=None)
    pass_host: str | None = attrs.field(converter=str_or_none, default=None)
    upstream_host: str | None = attrs.field(converter=str_or_none, default=None)
    scheme: Schemas | None = attrs.field(default=None)
    labels: dict = attrs.field(default={})
    tls: TLS | None = attrs.field(default=None)
    keepalive_pool: KeepalivePool | None = attrs.field(default=None)


UpstreamResponse = response_class_factory(Upstream)
