import attrs

from apisix_client.common import bool_or_none, str_or_none


@attrs.define()
class KeyAuth:
    key: str = attrs.field(converter=str)


@attrs.define()
class KeyAuthSettings:
    header: str | None = attrs.field(default="apikey", converter=str_or_none)
    query: str | None = attrs.field(default="apikey", converter=str_or_none)
    hide_credentials: bool | None = attrs.field(default=False, converter=bool_or_none)
