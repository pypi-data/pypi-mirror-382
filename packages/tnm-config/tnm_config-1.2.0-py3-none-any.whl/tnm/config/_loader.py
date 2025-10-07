from dataclasses import is_dataclass
from pathlib import Path
from typing import Any, Callable, Type, TypeVar, overload

from ._typeguard import typechecked
from .errors import ConfigError
from .loaders import get_loader_for_suffix, registered_suffixes

T = TypeVar("T")
_RawConfigResult = dict[str, Any] | list[Any] | str | int | float | bool | None


@typechecked
class ConfigLoader:
    def __init__(self, config_path: Path | str) -> None:
        self._path = Path(config_path)

    @overload
    def load(
        self,
        section: str | None = None,
        project_root_callback: Callable[[], Path | str] | None = None,
        schema_type: None = None,
    ) -> _RawConfigResult: ...

    @overload
    def load(
        self,
        section: str | None = None,
        project_root_callback: Callable[[], Path | str] | None = None,
        schema_type: Type[T] = ...,
    ) -> T: ...

    def load(
        self,
        section: str | None = None,
        project_root_callback: Callable[[], Path | str] | None = None,
        schema_type: Type[T] | None = None,
    ) -> T | _RawConfigResult:
        if not self._path.is_file():
            raise ConfigError(f"Config file '{self._path}' not found")

        suffix = self._path.suffix.lower()
        loader = self._select_loader(suffix)

        parsed = loader.load(self._path, project_root_callback=project_root_callback)

        if section:
            if not isinstance(parsed, dict):
                raise ConfigError("Section requested but config root is not a mapping")

            if section not in parsed:
                raise ConfigError(f"Missing section {section!r} in config")
            resolved = parsed[section]
        else:
            resolved = parsed

        if schema_type is None:
            return resolved

        if is_dataclass(schema_type):
            if not isinstance(resolved, dict):
                raise ConfigError(
                    "Dataclass schema requires a mapping (dict) as config root."
                )
            try:
                return schema_type(**resolved)  # type: ignore[call-arg]
            except Exception as exc:
                raise ConfigError(f"Dataclass construction error: {exc}") from exc

        try:
            from pydantic import BaseModel, ValidationError as PydanticValidationError

            if isinstance(schema_type, type) and issubclass(schema_type, BaseModel):
                if not isinstance(resolved, dict):
                    resolved = {"value": resolved}
                try:
                    if hasattr(schema_type, "model_validate"):
                        return schema_type.model_validate(resolved)  # type: ignore[return-value]
                    return schema_type.parse_obj(resolved)  # # noqa
                except PydanticValidationError as exc:
                    raise ConfigError(f"Pydantic validation error: {exc}") from exc
        except (ModuleNotFoundError, ImportError):
            ...

        try:
            if isinstance(resolved, dict):
                return schema_type(**resolved)  # type: ignore[call-arg]
            return schema_type(resolved)  # type: ignore[call-arg]
        except Exception as exc:
            raise ConfigError(
                f"Failed to construct schema_type {schema_type!r}: {exc}"
            ) from exc

    @staticmethod
    def _select_loader(suffix: str):
        """
        Factory selecting the appropriate loader implementation for a file suffix.
        """
        loader = get_loader_for_suffix(suffix)
        if loader is None:
            raise ConfigError(
                f"Unsupported file format: {suffix}. Supported are: {registered_suffixes()}"
            )

        return loader
