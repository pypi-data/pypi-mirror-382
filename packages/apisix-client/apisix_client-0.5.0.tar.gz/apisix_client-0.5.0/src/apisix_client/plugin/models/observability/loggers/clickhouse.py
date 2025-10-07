import attrs

from apisix_client.common.converter import bool_or_none, int_or_none, str_or_none


# https://apisix.apache.org/docs/apisix/plugins/clickhouse-logger/
@attrs.define()
class ClickhouseLogger:
    endpoint_addrs: list[str] = attrs.field(converter=list)
    database: str = attrs.field(converter=str)
    logtable: str = attrs.field(converter=str)
    user: str = attrs.field(converter=str)
    password: str = attrs.field(converter=str)
    timeout: int | None = attrs.field(converter=int_or_none, default=3)
    name: str | None = attrs.field(converter=str_or_none, default="clickhouse logger")
    ssl_verify: bool | None = attrs.field(converter=bool_or_none, default=True)
    log_format: dict | None = attrs.field(default=None)
    include_req_body: bool | None = attrs.field(converter=bool_or_none, default=False)
    include_req_body_expr: list | None = attrs.field(default=None)
    include_resp_body: bool | None = attrs.field(converter=bool_or_none, default=False)
    include_resp_body_expr: list | None = attrs.field(default=None)
    # Next fields are related to batch processor
    batch_max_size: int | None = attrs.field(converter=int_or_none, default=None)
    inactive_timeout: int | None = attrs.field(converter=int_or_none, default=None)
    buffer_duration: int | None = attrs.field(converter=int_or_none, default=None)
    max_retry_count: int | None = attrs.field(converter=int_or_none, default=None)
    retry_delay: int | None = attrs.field(converter=int_or_none, default=None)
