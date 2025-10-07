import attrs

from apisix_client.common import ATTRS_META_APISIX_KEYWORD, bool_or_none, str_or_none


@attrs.define()
class KeyAuth:
    key: str | None = attrs.field(default=None)


@attrs.define()
class LimitCount:
    count: int = attrs.field(converter=int)
    time_window: int = attrs.field(converter=int)
    key: str = attrs.field(converter=str)
    key_type: str = attrs.field(converter=str)
    rejected_code: int = attrs.field(converter=int, default=503)
    policy: str | None = attrs.field(converter=str_or_none, default=None)
    allow_degradation: bool | None = attrs.field(converter=bool_or_none, default=None)
    show_limit_quota_header: bool | None = attrs.field(converter=bool_or_none, default=None)


@attrs.define()
class Plugins:
    key_auth: KeyAuth | None = attrs.field(default=None, metadata={ATTRS_META_APISIX_KEYWORD: "key-auth"})
    limit_count: LimitCount | None = attrs.field(
        default=None, metadata={ATTRS_META_APISIX_KEYWORD: "limit-count"}
    )
