from pathlib import Path
from typing import Any, Callable

from ._base import BaseLoader
from .._utils import _cast_env_value, _resolve_project_path
from ..errors import ConfigError

_is_xmltodict_installed = False

try:
    import xmltodict

    _is_xmltodict_installed = True
except (ImportError, ModuleNotFoundError):
    ...


class XMLLoader(BaseLoader):
    def _normalize_node(
        self,
        node: Any,
        project_root_callback: Callable[[], Path | str] | None,
    ) -> Any:
        if isinstance(node, list):
            return [self._normalize_node(item, project_root_callback) for item in node]

        if not isinstance(node, dict):
            return node

        if len(node) == 1:
            key = next(iter(node.keys()))
            val = node[key]
            if key == "env" and isinstance(val, dict):
                var = val.get("@var") or val.get("var")
                t = val.get("@type") or val.get("type")
                default = val.get("@default") or val.get("default")
                if var is None or t is None:
                    raise ConfigError("<env> elements require var and type attributes")
                return _cast_env_value(var, t, default)
            if key == "path" and isinstance(val, dict):
                v = val.get("@value") or val.get("value")
                proj_rel = val.get("@project_relative") or val.get("project_relative")
                proj_rel_bool = (
                    True if proj_rel in (None, True, "true", "True", "1") else False
                )
                if v is None:
                    raise ConfigError("<path> elements require value attribute")
                return _resolve_project_path(
                    v,
                    project_root_callback=project_root_callback,
                    project_relative=proj_rel_bool,
                )

        return {
            k: self._normalize_node(v, project_root_callback) for k, v in node.items()
        }

    def load(
        self,
        path: Path,
        *,
        project_root_callback: Callable[[], Path | str] | None = None,
    ) -> Any:
        if not _is_xmltodict_installed:
            raise ConfigError(
                "xmltodict is required to load XML files. Install tnm-config[xml]."
            )

        try:
            raw = path.read_text(encoding="utf-8")
            parsed = xmltodict.parse(raw, force_list=None)
        except Exception as exc:
            raise ConfigError(
                f"Failed to parse XML config '{path}': {str(exc)}"
            ) from exc

        return self._normalize_node(parsed, project_root_callback=project_root_callback)
