import attrs

from apisix_client.common import ATTRS_META_APISIX_KEYWORD
from apisix_client.plugin.models.key_auth import KeyAuth, KeyAuthSettings
from apisix_client.plugin.models.limit_count import LimitCount
from apisix_client.plugin.models.observability.loggers.clickhouse import ClickhouseLogger


@attrs.define()
class Plugins:
    key_auth: KeyAuth | KeyAuthSettings | None = attrs.field(
        default=None, metadata={ATTRS_META_APISIX_KEYWORD: "key-auth"}
    )
    limit_count: LimitCount | None = attrs.field(
        default=None, metadata={ATTRS_META_APISIX_KEYWORD: "limit-count"}
    )
    clickhouse_logger: ClickhouseLogger | None = attrs.field(
        default=None, metadata={ATTRS_META_APISIX_KEYWORD: "clickhouse-logger"}
    )
