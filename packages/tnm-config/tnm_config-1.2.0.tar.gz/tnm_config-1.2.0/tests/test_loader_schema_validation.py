import json
from pathlib import Path
import pytest

from src.tnm.config import ConfigLoader
from src.tnm.config.errors import ConfigError


def test_pydantic_schema_ok(tmp_path: Path, monkeypatch):
    from pydantic import BaseModel

    class EsCfg(BaseModel):
        hosts: list[str]
        username: str
        password: str | None = None

    monkeypatch.setenv("ES_HOSTS", "http://127.0.0.1:9200")
    monkeypatch.setenv("ES_USERNAME", "puser")

    data = {
        "elasticsearch": {
            "hosts": {"__env__": ["ES_HOSTS", "list:url"]},
            "username": {"__env__": ["ES_USERNAME", "str", "fallback"]},
        }
    }
    f = tmp_path / "cfg.json"
    f.write_text(json.dumps(data))
    loader = ConfigLoader(f)
    inst = loader.load(
        "elasticsearch", project_root_callback=lambda: tmp_path, schema_type=EsCfg
    )
    assert isinstance(inst, EsCfg), "Should be instance of EsCfg"
    assert inst.username == "puser"
    assert isinstance(inst.hosts, list), "Should be list"


def test_pydantic_schema_invalid_raises(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("XVAL", "1")

    from pydantic import BaseModel

    class SmallCfg(BaseModel):
        x: int
        y: int

    data = {"root": {"x": {"__env__": ["XVAL", "int"]}}}
    f = tmp_path / "cfg.json"
    f.write_text(json.dumps(data))

    loader = ConfigLoader(f)
    with pytest.raises(ConfigError) as e:
        loader.load(
            "root", project_root_callback=lambda: tmp_path, schema_type=SmallCfg
        )
    assert (
        "Field required [type=missing, input_value={'x': 1}, input_type=dict]"
        in str(e.value)
    )


def test_dataclass_schema_ok(tmp_path: Path, monkeypatch):
    from dataclasses import dataclass

    @dataclass
    class DCfg:
        name: str
        v: int

    monkeypatch.setenv("NAME", "abc")
    monkeypatch.setenv("V", "10")
    data = {
        "cfg": {"name": {"__env__": ["NAME", "str"]}, "v": {"__env__": ["V", "int"]}}
    }
    f = tmp_path / "cfg.json"
    f.write_text(json.dumps(data))
    loader = ConfigLoader(f)
    inst = loader.load("cfg", project_root_callback=lambda: tmp_path, schema_type=DCfg)
    assert isinstance(inst, DCfg)
    assert inst.v == 10


def test_dataclass_schema_invalid_raises(tmp_path: Path):
    from dataclasses import dataclass

    @dataclass
    class D2:
        a: int
        b: int

    data = {"root": {"a": 1}}
    f = tmp_path / "cfg.json"
    f.write_text(json.dumps(data))
    loader = ConfigLoader(f)
    with pytest.raises(ConfigError) as e:
        loader.load("root", project_root_callback=lambda: tmp_path, schema_type=D2)

    assert "missing 1 required positional argument: 'b'" in str(e.value)
