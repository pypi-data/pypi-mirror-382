"""End-to-end (E2E) test setup.

Environment selection via APP_ENV: staging (default)

"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml
from dotenv import load_dotenv

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 1) Load repo-level base env (if present)

# Determine environment from APP_ENV (required for E2E tests)
APP_ENV_RAW = os.environ.get("APP_ENV")
if not APP_ENV_RAW or not APP_ENV_RAW.strip():
    raise RuntimeError(
        "APP_ENV is required for E2E tests. Set it to one of: local, dev, staging, prod.\n"
        "Example: APP_ENV=staging uv run pytest tests/e2e"
    )
APP_ENV = APP_ENV_RAW.strip().lower()

# 2) Load environment-specific E2E env (if present)
env_specific = os.path.join(os.path.dirname(__file__), f".env.{APP_ENV}")
loaded_files: list[str] = []
if load_dotenv(os.path.join(REPO_ROOT, ".env")):
    loaded_files.append("/.env")
if load_dotenv(env_specific, override=True):
    loaded_files.append(f"tests/e2e/.env.{APP_ENV}")


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "prod_only: mark test as requiring prod environment with real dataset IDs",
    )


def pytest_collection_modifyitems(config, items):
    """Skip prod_only tests if not running in prod environment."""
    app_env = os.environ.get("APP_ENV", "").strip().lower()

    if app_env != "prod":
        skip_prod = pytest.mark.skip(
            reason="Test requires APP_ENV=prod (uses real dataset IDs)"
        )
        for item in items:
            if "prod_only" in item.keywords:
                item.add_marker(skip_prod)


def pytest_sessionstart(session: pytest.Session) -> None:
    """Validate environment for E2E tests."""

    app_env = os.environ.get("APP_ENV", "staging").strip().lower()

    # Enforce required vars for staging
    if app_env == "staging":
        required_vars = [
            "VCP_API_BASE_URL",
            "DATA_API_BASE_URL",
            "USER_POOL_ID",
            "CLIENT_ID",
            "AUTH_BASE_URL",
            "VCP_ADMIN_USERNAME",
            "VCP_ADMIN_PASSWORD",
        ]
        for var in required_vars:
            if not os.environ.get(var):
                raise RuntimeError(
                    f"{var} is required for staging E2E tests. "
                    "Set it via tests/e2e/.env.staging or shell env."
                )


@pytest.fixture(scope="session")
def session_auth():
    with tempfile.TemporaryDirectory() as temp_home:
        app_env = dict(os.environ)
        app_env.update({
            "HOME": temp_home,
            "VCP_API_BASE_URL": os.getenv("VCP_API_BASE_URL"),
            "DATA_API_BASE_URL": os.getenv("DATA_API_BASE_URL"),
            "COGNITO_USER_POOL_ID": os.getenv("USER_POOL_ID"),
            "COGNITO_CLIENT_ID": os.getenv("CLIENT_ID"),
            "COGNITO_DOMAIN": os.getenv("AUTH_BASE_URL"),
            "VCP_PASSWORD": os.getenv("VCP_ADMIN_PASSWORD"),
            # Provide anonymous AWS credentials for boto3 (not used for auth)
            "AWS_ACCESS_KEY_ID": "dummy",
            "AWS_SECRET_ACCESS_KEY": "dummy",
        })
        # Remove AWS_PROFILE if it exists to prevent profile lookup
        app_env.pop("AWS_PROFILE", None)

        # Create custom config file at ~/.vcp/config.yaml so CLI finds it without --config
        temp_config_dir = Path(temp_home) / ".vcp"
        temp_config_dir.mkdir(parents=True, exist_ok=True)
        temp_config = temp_config_dir / "config.yaml"
        config_dict = {
            "models": {
                "base_url": os.getenv("VCP_API_BASE_URL"),
                "github": {
                    "template_repo": "https://github.com/chanzuckerberg/model-template.git",
                },
                "endpoints": {
                    "login": "/auth/login",
                    "submit": "/api/models/submit",
                    "download": "/api/models/download",
                    "list": "/api/models/list",
                },
            },
            "data_api": {"base_url": os.getenv("DATA_API_BASE_URL")},
            "aws": {
                "region": "us-west-2",
                "cognito": {
                    "user_pool_id": os.getenv("USER_POOL_ID"),
                    "client_id": os.getenv("CLIENT_ID"),
                    "domain": os.getenv("AUTH_BASE_URL"),
                    "flow": "password",
                },
            },
        }
        config_content = yaml.safe_dump(config_dict)
        temp_config.write_text(config_content)

        # Perform login
        login_result = subprocess.run(
            [
                "uv",
                "run",
                "vcp",
                "login",
                "--username",
                os.getenv("VCP_ADMIN_USERNAME"),
                "--config",
                str(temp_config),
            ],
            env=app_env,
            capture_output=True,
            text=True,
        )
        assert login_result.returncode == 0, f"Login failed: {login_result.stderr}"
        assert "Login successful!" in login_result.stdout

        yield app_env, temp_config
