from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from . import get_config
from ._typeguard import typechecked
from .errors import EnvVarNotSetError, InvalidURLError, ConfigError


def _cast_env_value(var_name: str, type_hint: str, default: Any) -> Any:
    """
    Cast environment variable using type_hint.
    Supported hints: url, str, int, float, bool, list:str, list:url
    :raises EnvVarNotSetError: if missing and default is None.
    :raises InvalidURLError: on invalid input.
    :raises ValueError: on invalid input.
    """
    val: str | None = get_config(key=var_name, default=None)
    if val is None:
        if default is not None:
            return _match_type_hint(type_hint, default)
        raise EnvVarNotSetError(f"Environment variable '{var_name}' not set")

    return _match_type_hint(type_hint=type_hint, val=val)


def _match_type_hint(type_hint: str, val: Any):
    match type_hint:
        case "url":
            parsed = urlparse(val)
            if not parsed.scheme or not parsed.netloc:
                raise InvalidURLError(f"Provided URL '{val}' is invalid.")
            return val
        case "str":
            return val
        case "int":
            return int(val)
        case "float":
            return float(val)
        case "bool":
            v = val.lower()
            if v in ("1", "true", "yes", "y", "on"):
                return True
            if v in ("0", "false", "no", "n", "off"):
                return False
            raise ValueError(f"Cannot cast '{val}' to bool")
        case hint if hint.startswith("list:str"):
            return [item.strip() for item in val.split(",") if item.strip()]
        case hint if hint.startswith("list:url"):
            valid = []
            for item in val.split(","):
                parsed = urlparse(item.strip())
                if not parsed.scheme or not parsed.netloc:
                    raise InvalidURLError(
                        f"The provided URL {item!r} in list {val!r} is invalid."
                    )
                valid.append(item.strip())
            return valid
        case _:
            raise ValueError(f"Unsupported env type hint: {type_hint!r}")


@typechecked
def _get_project_root_from_callable(
    project_root_callback: Callable[[], Path | str] | None,
) -> Path:
    """Return a resolved Path from the provided callable."""
    if not project_root_callback:
        raise ConfigError(
            "'project_root_callback' is required for !path with project_relative=True"
        )

    try:
        p = project_root_callback()
    except Exception as exc:
        raise ConfigError(
            f"'project_root_callback' raised an exception: {str(exc)}"
        ) from exc
    if not isinstance(p, Path):
        p = Path(p)

    p = p.resolve()

    if not p.is_dir():
        raise ConfigError(f"'project_root_callback' is not a directory: {p}")

    return p


def _resolve_project_path(
    value: Any,
    project_root_callback: Callable[[], Path | str] | None = None,
    project_relative: bool = True,
) -> Any:
    """Resolve project-relative paths. Accept lists and scalars."""
    if isinstance(value, list):
        return [
            _resolve_project_path(
                item,
                project_root_callback=project_root_callback,
                project_relative=project_relative,
            )
            for item in value
        ]
    if isinstance(value, str) and project_relative:
        root = _get_project_root_from_callable(project_root_callback)
        return str((root / value).resolve())
    return value


def _resolve_node(
    node: Any, project_root_callback: Callable[[], Path | str] | None = None
) -> Any:
    """
    Recursively resolve special markers:
      - YAML: handled by constructors (if PyYAML used)
      - For JSON: special marker objects:
          {"__env__": ["VAR", "type", default?]}
          {"__path__": {"value": "...", "project_relative": true/false}}
      - For XML (xmltodict): tags:
          <env var="VAR" type="list:url" default="..."/>
          <path value="..." project_relative="true"/>
    """
    if isinstance(node, list):
        return [
            _resolve_node(item, project_root_callback=project_root_callback)
            for item in node
        ]

    if not isinstance(node, dict):
        return node

    return {
        k: _resolve_node(v, project_root_callback=project_root_callback)
        for k, v in node.items()
    }
