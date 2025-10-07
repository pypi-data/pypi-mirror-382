import humps


def pythonize_json_response(data: dict) -> dict:
    return humps.decamelize(humps.dekebabize(data))


def build_url(*url_parts):
    return "/".join(
        list(url_parts[0]) if len(url_parts) and isinstance(url_parts[0], (list, tuple)) else list(url_parts)
    )
