import subprocess

import pytest

from tests.e2e.model.base_model_test import BaseModelTest


class TestModelStatus(BaseModelTest):
    @pytest.mark.e2e
    def test_model_status(self, session_auth):
        app_env, _ = session_auth

        table_result = subprocess.run(
            ["uv", "run", "vcp", "model", "status"],
            env=app_env,
            capture_output=True,
            text=True,
        )

        print(table_result.stdout)
        print(table_result.stderr)

        # Validate model status output using base class method
        self.validate_model_status_output(table_result)

    @pytest.mark.e2e
    def test_model_status_with_config_option(self, session_auth):
        app_env, temp_config = session_auth

        table_result = subprocess.run(
            [
                "uv",
                "run",
                "vcp",
                "model",
                "status",
                "--config",
                str(temp_config),
            ],
            env=app_env,
            capture_output=True,
            text=True,
        )

        print(table_result.stdout)
        print(table_result.stderr)

        # Validate model status output using base class method
        self.validate_model_status_output(table_result)

    @pytest.mark.e2e
    def test_model_status_with_verbose_option(self, session_auth):
        app_env, _ = session_auth

        table_result = subprocess.run(
            [
                "uv",
                "run",
                "vcp",
                "model",
                "status",
                "--verbose",
            ],
            env=app_env,
            capture_output=True,
            text=True,
        )

        print(table_result.stdout)
        print(table_result.stderr)

        # Validate model status output using base class method
        self.validate_model_status_output(table_result)
