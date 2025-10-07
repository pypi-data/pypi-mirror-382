import json
from pathlib import Path
from typing import Any, Callable

from ._base import BaseLoader
from .._utils import _cast_env_value, _resolve_project_path
from ..errors import ConfigError


class JSONLoader(BaseLoader):
    def _normalize_node(
        self, node: Any, project_root_callback: Callable[[], Path | str] | None
    ):
        if not isinstance(node, dict):
            return node

        if "__env__" in node:
            val = node["__env__"]
            if not isinstance(val, list) or len(val) < 2:
                raise ConfigError("__env__ must be a list like [VAR, TYPE, default?]")
            default = val[2] if len(val) >= 3 else None
            return _cast_env_value(val[0], val[1], default)

        if "__path__" in node:
            data = node["__path__"]
            if not isinstance(data, dict) or "value" not in data:
                raise ConfigError(
                    "__path__ must be an object like {'value': 'p', 'project_relative': true}"
                )
            return _resolve_project_path(
                data["value"],
                project_root_callback=project_root_callback,
                project_relative=data.get("project_relative", True),
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
        try:
            with path.open("r", encoding="utf-8") as fh:
                content = json.load(fh)
        except Exception as exc:
            raise ConfigError(
                f"Failed to parse JSON config '{path}': {str(exc)}"
            ) from exc

        return self._normalize_node(
            content, project_root_callback=project_root_callback
        )
