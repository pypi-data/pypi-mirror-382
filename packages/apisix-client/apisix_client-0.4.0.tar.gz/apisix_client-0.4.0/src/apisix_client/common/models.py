import attrs

ATTRS_META_APISIX_KEYWORD = "apisix_keyword"

APISIX_MIN_PAGE_SIZE = 10
APISIX_MAX_PAGE_SIZE = 500


def page_size_validation(instance, attributes, value) -> None:
    if value < APISIX_MIN_PAGE_SIZE or value > APISIX_MAX_PAGE_SIZE:
        raise ValueError(f"page_size must be between {APISIX_MIN_PAGE_SIZE} and {APISIX_MAX_PAGE_SIZE}")


@attrs.define()
class Pagging:
    page: int = attrs.field(converter=int)
    page_size: int = attrs.field(
        converter=int, default=APISIX_MIN_PAGE_SIZE, validator=[page_size_validation]
    )

    @property
    def as_dict(self) -> dict[str, int]:
        return attrs.asdict(self)


@attrs.define()
class Timeout:
    connect: float
    send: float
    read: float
