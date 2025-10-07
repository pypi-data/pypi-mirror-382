import pytest

from src.tnm.config.errors import ConfigError
from src.tnm.config._typeguard import typechecked


@typechecked
def fn_no_args() -> None:
    return None


@typechecked
def greet(name: str) -> str:
    return f"hello {name}"


def test_typeguard_adapter_converts_error():
    with pytest.raises(ConfigError, match="is not an instance of str"):
        greet(123)
