import os
from typing import Any, Callable, TypeVar, overload

from dotenv import load_dotenv

T = TypeVar("T")


load_dotenv(override=True)


@overload
def get_config(key: str, default: Any = None, cast: Callable[[str], T] = ...) -> T: ...
@overload
def get_config(key: str, default: Any = None, cast: None = ...) -> Any: ...


def get_config(
    key: str, default: Any = None, cast: Callable[[str], T] | None = None
) -> Any:
    """
    Read environment variable and optionally cast. If cast fails, returns default.
    """
    value = os.environ.get(key, default)
    if cast:
        if cast is str and (value is None or value == ""):
            return default
        try:
            return cast(value)  # type: ignore[arg-type]
        except Exception:
            return default
    return value
