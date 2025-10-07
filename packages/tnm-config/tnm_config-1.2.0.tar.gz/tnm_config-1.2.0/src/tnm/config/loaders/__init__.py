from __future__ import annotations

from importlib import import_module
from importlib.metadata import entry_points
from typing import Any, Callable, Dict, Optional

from ._base import BaseLoader

LoaderFactory = Callable[[], Any]

_registry: Dict[str, LoaderFactory] = {}


def register_loader(suffix: str, factory: LoaderFactory) -> None:
    if not suffix.startswith("."):
        suffix = f".{suffix}"
    _registry[suffix.lower()] = factory


def unregister_loader(suffix: str) -> None:
    if not suffix.startswith("."):
        suffix = f".{suffix}"
    _registry.pop(suffix.lower(), None)


def get_loader_for_suffix(suffix: str) -> Optional[Any]:
    if not suffix:
        return None
    if not suffix.startswith("."):
        suffix = f".{suffix}"
    factory = _registry.get(suffix.lower())
    return factory() if factory is not None else None


def registered_suffixes() -> list[str]:
    return sorted(_registry.keys())


def _safe_register(suffixes: list[str], loader_cls: type[BaseLoader]) -> None:
    """Register loader_cls for each suffix; avoid late-binding closures."""

    def _loader_factory(cls: type[BaseLoader] = loader_cls) -> BaseLoader:
        return cls()

    for s in suffixes:
        register_loader(s, _loader_factory)


def _import_module_relative_or_absolute(
    short_module: str, absolute_candidates: list[str]
):
    try:
        mod = import_module(f".{short_module}", package=__name__)
        return mod
    except Exception:
        pass

    for name in absolute_candidates:
        try:
            mod = import_module(name)
            return mod
        except Exception:
            continue

    return None


def _try_register_builtin(
    short_module: str,
    suffixes: list[str],
    class_name_candidates: list[str],
    absolute_module_candidates: list[str] | None = None,
) -> None:
    if absolute_module_candidates is None:
        absolute_module_candidates = [
            f"tnm.config.loaders.{short_module}",
            f"src.tnm.config.loaders.{short_module}",
        ]

    mod = _import_module_relative_or_absolute(short_module, absolute_module_candidates)
    if mod is None:
        return

    for cls_name in class_name_candidates:
        loader_cls = getattr(mod, cls_name, None)
        if loader_cls is None:
            continue
        _safe_register(suffixes, loader_cls)
        return


_try_register_builtin(
    short_module="json_loader",
    suffixes=[".json"],
    class_name_candidates=["JsonLoader", "JSONLoader", "JSONLoaderImpl"],
    absolute_module_candidates=[
        "tnm.config.loaders.json_loader",
        "src.tnm.config.loaders.json_loader",
    ],
)

_try_register_builtin(
    short_module="yaml_loader",
    suffixes=[".yaml", ".yml"],
    class_name_candidates=["YamlLoader", "YAMLLoader", "YamlLoaderImpl"],
    absolute_module_candidates=[
        "tnm.config.loaders.yaml_loader",
        "src.tnm.config.loaders.yaml_loader",
    ],
)

_try_register_builtin(
    short_module="xml_loader",
    suffixes=[".xml"],
    class_name_candidates=["XmlLoader", "XMLLoader", "XmlLoaderImpl"],
    absolute_module_candidates=[
        "tnm.config.loaders.xml_loader",
        "src.tnm.config.loaders.xml_loader",
    ],
)


def _discover_entrypoint_loaders() -> None:
    try:
        eps = entry_points()
        try:
            points = list(eps.select(group="tnm_config.loaders"))
        except Exception:
            points = getattr(eps, "tnm_config.loaders", []) or []
        for ep in points:
            suffix = ep.name if ep.name else None
            if suffix is None:
                continue
            if not suffix.startswith("."):
                suffix = f".{suffix}"
            try:
                obj = ep.load()
                if callable(obj):

                    def _obj_lambda(_obj: type[BaseLoader] = obj):
                        return _obj() if isinstance(obj, type) else obj

                    register_loader(suffix, _obj_lambda)
            except Exception:
                continue
    except Exception:
        return


_discover_entrypoint_loaders()


__all__ = [
    "register_loader",
    "unregister_loader",
    "get_loader_for_suffix",
    "registered_suffixes",
]
