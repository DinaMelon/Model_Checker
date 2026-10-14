import json
from pathlib import Path


def _to_json_safe(value):
    if value is None:
        return None

    if isinstance(value, (bool, int, float, str)):
        return value

    if isinstance(value, dict):
        return {
            str(key): _to_json_safe(val)
            for key, val in value.items()
        }

    if hasattr(value, "keys"):
        try:
            return {
                str(key): _to_json_safe(value[key])
                for key in value.keys()
            }
        except Exception:
            pass

    if isinstance(value, (list, tuple)):
        return [
            _to_json_safe(item)
            for item in value
        ]

    if hasattr(value, "__iter__"):
        try:
            return [
                _to_json_safe(item)
                for item in value
            ]
        except Exception:
            pass

    return str(value)


def export(result, path):
    safe_result = _to_json_safe(result)

    Path(path).write_text(
        json.dumps(
            safe_result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )