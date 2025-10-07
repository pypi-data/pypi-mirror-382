import re
from enum import IntEnum

import attrs

from apisix_client.base_models import response_class_factory
from apisix_client.common import Timeout, str_or_none
from apisix_client.plugin import Plugins


def route_id_validator(value) -> None:
    """
    https://apisix.apache.org/docs/apisix/admin-api/#quick-note-on-id-syntax
    ID's as a text string must be of a length between 1 and 64 characters and they should only contain
    uppercase, lowercase, numbers and no special characters apart from dashes ( - ), periods ( . ) and
    underscores ( _ ). For integer values they simply must have a minimum character count of 1.
    """
    str_id = str(value)
    char_count = len(str_id)
    if char_count < 1 or char_count > 64:
        raise ValueError(f"Id must be of a length between 1 and 64 characters. Got id with len {char_count}")

    finds = re.findall(r"([\d | \w | . | \- | _ ]+)", value)
    if len(finds) != 1 or len(finds[0]) != len(str_id):
        raise ValueError(
            f"Provided id {value} incomplete requirements. Id should only contain uppercase, lowercase,",
            "numbers and no special characters apart from dashes ( - ), periods ( . ) and underscores ( _ ).",
        )


def exclusive_use_of_props(prop_a: str, prop_b: str, one_of_required: bool):
    def exclusived_use_of_uri(instance, attributes, value) -> None:
        f"{prop_a} can't be used with {prop_b} and vice versa, but one of them must be fulfilled."
        if one_of_required and not getattr(instance, prop_a) and not getattr(instance, prop_b):
            raise ValueError(f"One of the fields {prop_a} or {prop_b} must be fulfilled.")

        if getattr(instance, prop_a) is not None and getattr(instance, prop_b) is not None:
            raise ValueError(f"Only one of the fields {prop_a}, {prop_b} should be fulfilled.")

    return exclusived_use_of_uri


class RouteStatus(IntEnum):
    ENABLED = 1
    DISABLED = 0


@attrs.define()
class Route:
    name: str | None = attrs.field(default=None)
    desc: str | None = attrs.field(default=None)
    uri: str | None = attrs.field(default=None)
    uris: list[str] | None = attrs.field(
        default=None, validator=[exclusive_use_of_props("uri", "uris", True)]
    )
    host: str | None = attrs.field(default=None)
    hosts: list[str] | None = attrs.field(
        default=None, validator=[exclusive_use_of_props("host", "hosts", False)]
    )
    remote_addr: str | None = attrs.field(default=None)
    remote_addrs: list[str] | None = attrs.field(
        default=None, validator=[exclusive_use_of_props("remote_addr", "remote_addrs", False)]
    )
    methods: list[str] | None = attrs.field(default=None)
    vars: list[list[str]] | None = attrs.field(default=None)
    filter_func: str | None = attrs.field(default=None)
    plugins: Plugins | None = attrs.field(default=None)
    script: str | None = attrs.field(default=None)
    upstream: object | None = attrs.field(
        default=None
    )  # TODO replace with upstream object like Plugins above
    upstream_id: str | None = attrs.field(converter=str_or_none, default=None)
    service_id: str | None = attrs.field(converter=str_or_none, default=None)
    plugin_config_id: int = attrs.field(
        default=None, validator=[exclusive_use_of_props("script", "plugin_config_id", False)]
    )
    labels: dict | None = attrs.field(default=None)
    timeout: Timeout | None = attrs.field(default=None)
    priority: int | None = attrs.field(default=0)
    enable_websocket: bool | None = attrs.field(default=False)
    status: RouteStatus | None = attrs.field(default=RouteStatus.ENABLED)


RouteResponse = response_class_factory(Route)
