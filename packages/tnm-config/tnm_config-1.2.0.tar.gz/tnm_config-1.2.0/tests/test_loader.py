import json
from pathlib import Path

import pytest

from src.tnm.config import ConfigLoader
from src.tnm.config.errors import InvalidURLError, EnvVarNotSetError, ConfigError


def _make_project_structure(tmp_path: Path):
    extras = tmp_path / "extras" / "templates"
    extras.mkdir(parents=True)

    (extras / "dummy.txt").write_text("ok")
    return extras


def test_json_env_and_path_resolution(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ES_HOSTS", "http://127.0.0.1:9200,http://example.com")
    monkeypatch.setenv("ES_USERNAME", "json_user")

    project_root = tmp_path
    _make_project_structure(tmp_path)

    cfg_data = {
        "elasticsearch": {
            "hosts": {"__env__": ["ES_HOSTS", "list:url", "http://127.0.0.1:9200"]},
            "username": {"__env__": ["ES_USERNAME", "str", "fallback"]},
            "templates_dir": {
                "__path__": {"value": "extras/templates", "project_relative": True}
            },
        }
    }

    cfg_file = tmp_path / "cfg.json"

    cfg_file.write_text(json.dumps(cfg_data))

    loader = ConfigLoader(cfg_file)
    cfg = loader.load("elasticsearch", project_root_callback=lambda: project_root)

    assert isinstance(cfg, dict)
    assert cfg["username"] == "json_user"
    assert isinstance(cfg["hosts"], list)
    assert cfg["hosts"][0].startswith("http://127.0.0.1")
    assert Path(cfg["templates_dir"]).resolve().is_dir()
    assert str(project_root) in str(Path(cfg["templates_dir"]).resolve())


def test_project_root_callback_invalid_signature_raises_config_error(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setenv("ES_HOSTS", "http://127.0.0.1:9200,http://example.com")
    monkeypatch.setenv("ES_USERNAME", "json_user")

    _make_project_structure(tmp_path)

    cfg_data = {
        "elasticsearch": {
            "hosts": {"__env__": ["ES_HOSTS", "list:url", "http://127.0.0.1:9200"]},
            "username": {"__env__": ["ES_USERNAME", "str", "fallback"]},
            "templates_dir": {
                "__path__": {"value": "extras/templates", "project_relative": True}
            },
        }
    }

    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps(cfg_data))

    loader = ConfigLoader(cfg_file)

    def bad_callback(arg1: str):
        return arg1

    with pytest.raises(ConfigError) as exc_info:
        loader.load("elasticsearch", project_root_callback=bad_callback)

    assert isinstance(exc_info.value, ConfigError)

    msg = str(exc_info.value).lower()

    assert ("project_root" in msg) or ("type" in msg) or ("validation" in msg)


def test_yaml_env_and_path_resolution(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ES_HOSTS", "http://127.0.0.1:9200")
    monkeypatch.delenv("ES_USERNAME", raising=False)

    project_root = tmp_path
    _make_project_structure(tmp_path)

    yaml_text = """
                elasticsearch:
                  hosts: !env [ ES_HOSTS, list:url, http://127.0.0.1:9200 ]
                  username: !env [ ES_USERNAME, str, default_user ]
                  templates_dir: !path [ extras/templates, true ]
                """

    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text(yaml_text)

    loader = ConfigLoader(cfg_file)
    cfg = loader.load("elasticsearch", project_root_callback=lambda: project_root)

    assert cfg["username"] == "default_user"
    assert isinstance(cfg["hosts"], list)
    assert cfg["hosts"][0].startswith("http://127.0.0.1")
    assert Path(cfg["templates_dir"]).is_dir()


def test_xml_env_and_path_resolution(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ES_HOSTS", "http://127.0.0.1:9200,http://example.com")
    monkeypatch.setenv("ES_USERNAME", "xml_user")

    project_root = tmp_path
    _make_project_structure(tmp_path)

    xml_text = """<?xml version="1.0"?>
                    <elasticsearch>
                      <hosts>
                        <env var="ES_HOSTS" type="list:url" default="http://127.0.0.1:9200" />
                      </hosts>
                      <username>
                        <env var="ES_USERNAME" type="str" default="fallback" />
                      </username>
                      <templates_dir>
                        <path value="extras/templates" project_relative="true" />
                      </templates_dir>
                    </elasticsearch>
                """
    cfg_file = tmp_path / "cfg.xml"
    cfg_file.write_text(xml_text)

    loader = ConfigLoader(cfg_file)

    cfg = loader.load("elasticsearch", project_root_callback=lambda: project_root)

    assert cfg["username"] == "xml_user"
    assert isinstance(cfg["hosts"], list)
    assert "http://127.0.0.1" in cfg["hosts"][0]
    assert Path(cfg["templates_dir"]).is_dir()


def test_missing_env_raises(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)

    cfg_data = {"app": {"value": {"__env__": ["MISSING_VAR", "str"]}}}
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps(cfg_data))

    loader = ConfigLoader(cfg_file)
    with pytest.raises(EnvVarNotSetError):
        loader.load("app")


def test_invalid_url_raises(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("BAD_URL", "not-a-url")

    cfg_data = {"app": {"endpoint": {"__env__": ["BAD_URL", "url"]}}}
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps(cfg_data))

    loader = ConfigLoader(cfg_file)
    with pytest.raises(InvalidURLError):
        loader.load("app")


@pytest.mark.parametrize(
    "env_key,env_val,ctype,expected",
    [
        ("I1", "1", "int", 1),
        ("F1", "3.14", "float", 3.14),
        ("B1", "true", "bool", True),
        ("B2", "0", "bool", False),
    ],
)
def test_basic_casts(tmp_path: Path, monkeypatch, env_key, env_val, ctype, expected):
    monkeypatch.setenv(env_key, env_val)
    cfg_data = {"app": {"v": {"__env__": [env_key, ctype]}}}
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps(cfg_data))
    loader = ConfigLoader(cfg_file)
    cfg = loader.load("app")
    assert cfg["v"] == expected


def test_list_str_and_list_url(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("LIST_STR", "a, b ,c")
    monkeypatch.setenv("LIST_URLS", "http://a.test,http://b.test")

    cfg_data = {
        "app": {
            "names": {"__env__": ["LIST_STR", "list:str"]},
            "urls": {"__env__": ["LIST_URLS", "list:url"]},
        }
    }
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps(cfg_data))

    loader = ConfigLoader(cfg_file)
    cfg = loader.load("app")
    assert cfg["names"] == ["a", "b", "c"]
    assert isinstance(cfg["urls"], list)
    assert cfg["urls"][0].startswith("http://")


def test_project_root_callback_failure(tmp_path: Path):
    cfg_data = {
        "app": {
            "p": {"__path__": {"value": "extras/templates", "project_relative": True}}
        }
    }
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps(cfg_data))

    def bad_callback():
        raise RuntimeError("boom")

    loader = ConfigLoader(cfg_file)
    with pytest.raises(ConfigError) as exc_info:
        loader.load("app", project_root_callback=bad_callback)

    assert str(exc_info.value) == "'project_root_callback' raised an exception: boom"


def test_json_without_section_returns_root(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ROOTVAL", "rooted")
    cfg_data = {"root": {"val": {"__env__": ["ROOTVAL", "str"]}}}
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps(cfg_data))
    loader = ConfigLoader(cfg_file)
    data = loader.load(None)  # load whole doc
    assert data["root"]["val"] == "rooted"
