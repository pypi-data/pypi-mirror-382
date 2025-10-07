def str_or_none(value: object | None) -> str | None:
    return None if value is None else str(value)


def bool_or_none(value: object | None) -> bool | None:
    return None if value is None else bool(value)
