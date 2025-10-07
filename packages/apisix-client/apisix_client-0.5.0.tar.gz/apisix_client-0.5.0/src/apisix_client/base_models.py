from datetime import datetime
from typing import Callable, Generic, TypeVar

import attrs
import cattrs

from apisix_client.common import ATTRS_META_APISIX_KEYWORD, str_or_none

converter = cattrs.GenConverter()


def get_apisix_unstructure_hook(cls) -> Callable[[object], dict]:
    def apisix_json_format(obj: object) -> dict:
        results = {}
        for field in attrs.fields(cls):
            field_data = getattr(obj, field.name)
            if not field_data and not isinstance(field_data, (int, float, bool)):
                continue

            key = field.metadata.get(ATTRS_META_APISIX_KEYWORD, field.name)
            results[key] = converter.unstructure(field_data)

        return results

    return apisix_json_format


converter.register_unstructure_hook_factory(
    lambda obj: hasattr(obj, "__attrs_attrs__"), get_apisix_unstructure_hook
)


@attrs.define()
class BaseSchema:
    name: str | None = attrs.field(default=None, converter=str_or_none)
    desc: str | None = attrs.field(default=None, converter=str_or_none)


V = TypeVar("V")


# https://apisix.apache.org/docs/apisix/admin-api/#v3-new-feature
@attrs.define()
class BaseResponse(Generic[V]):
    key: str = attrs.field(converter=str)
    created_index: int = attrs.field(converter=int)
    modified_index: int = attrs.field(converter=int)
    value: V = attrs.field()


# A response from Apisix always contains id, create_time, update_time and others schema specific fields.
# If we want to keep attrs classes with slot=True, we canno't use MixinClass.
def response_class_factory(cls: type) -> type:
    """
    Dynamically creates a new response class based on the given schema specific class `cls`.

    The generated class inherits from `cls` and adds the following fields:
        - id (str): Identifier, converted to string, defaults to an empty string.
        - create_time (datetime): Creation time, converted from a timestamp, defaults to epoch.
        - update_time (datetime): Update time, converted from a timestamp, defaults to epoch.

    The returned class uses attrs, is frozen (immutable), and uses slots for memory efficiency.

    Args:
        cls (type): The base class to inherit from.

    Returns:
        type: A new attrs-based response class with additional fields.
    """
    return attrs.make_class(
        f"Response{cls.__name__}",
        {
            "id": attrs.field(converter=str, default=""),
            "create_time": attrs.field(converter=datetime.fromtimestamp, default=datetime.fromtimestamp(0)),
            "update_time": attrs.field(converter=datetime.fromtimestamp, default=datetime.fromtimestamp(0)),
        },
        bases=(cls,),
        slots=True,
        frozen=True,
    )
