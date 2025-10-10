import pytest
import yaml

from vcp.config import Config


@pytest.fixture
def default_config_yaml():
    return {
        "api": {
            "base_url": "https://api.default.com/v1",
            "endpoints": {
                "login": "/auth/login",
                "submit": "/api/models/submit",
                "download": "/api/models/download",
                "list": "/api/models/list",
            },
        },
        "aws": {
            "region": "us-west-2",
            "cognito": {
                "user_pool_id": "default_pool",
                "client_id": "default_client",
                "client_secret": "default_secret",
                "domain": "default_domain",
            },
        },
        "databricks": {
            "host": "https://default.databricks.com",
            "token": "default-token",
        },
    }


@pytest.fixture
def user_config_yaml():
    return {
        "models": {"base_url": "https://api.user.com/v2"},
        "aws": {"cognito": {"client_id": "user_client"}},
    }


@pytest.fixture
def malformed_yaml():
    return """
api
  base_url: "https://malformed.api.com"
  endpoints:
    login: "/auth/login"
"""


@pytest.fixture
def write_yaml(tmp_path):
    def _write_yaml(content, filename):
        path = tmp_path / filename
        with open(path, "w") as f:
            yaml.dump(content, f)
        return path

    return _write_yaml


@pytest.fixture
def mock_default_config(tmp_path, monkeypatch, default_config_yaml, write_yaml):
    path = tmp_path / "default_config.yaml"
    write_yaml(default_config_yaml, "default_config.yaml")

    def mock_open_text(*args, **kwargs):
        return open(path)

    monkeypatch.setattr("importlib.resources.open_text", mock_open_text)


@pytest.fixture
def mock_missing_default_config(monkeypatch):
    def mock_open_text(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr("importlib.resources.open_text", mock_open_text)


def test_load_default_config_success(mock_default_config, default_config_yaml):
    default_config = Config.load_default_config()
    assert default_config == default_config_yaml


def test_load_user_config_missing():
    user_config = Config.load_user_config("non_existent.yaml")
    assert user_config == {}


def test_load_user_config_malformed(tmp_path, malformed_yaml, write_yaml):
    malformed_path = tmp_path / "malformed.yaml"
    malformed_path.write_text(malformed_yaml)

    with pytest.raises(RuntimeError, match="User configuration is malformed"):
        Config.load_user_config(str(malformed_path))


def test_merge_configs(mock_default_config, tmp_path, user_config_yaml, write_yaml):
    user_config_path = write_yaml(user_config_yaml, "user_config.yaml")

    final_config = Config.load(str(user_config_path))

    assert (
        final_config.models.base_url == "https://api.user.com/v2"
    )  # overridden by user
    assert final_config.aws.cognito.client_id == "user_client"  # overridden by user
    assert final_config.aws.cognito.domain == "default_domain"
    assert final_config.databricks.host == "https://default.databricks.com"


def test_empty_merged_config(mock_missing_default_config):
    with pytest.raises(RuntimeError, match="No valid configuration provided"):
        Config.load("non_existent.yaml")
