import json
import subprocess

import pytest

from tests.e2e.model.base_model_test import BaseModelTest


class TestModelList(BaseModelTest):
    @pytest.mark.e2e
    def test_model_list(self, session_auth):
        app_env, _ = session_auth

        # region Run the model list command
        result = subprocess.run(
            ["uv", "run", "vcp", "model", "list"],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)
        # endregion Run the model list command

        # region Validate table header in result.stdout
        self.validate_model_list_standard_output(result)
        # endregion Validate table header in result.stdout

    @pytest.mark.e2e
    def test_model_list_with_config_option(self, session_auth):
        app_env, temp_config = session_auth

        # region Run the model list command
        result = subprocess.run(
            ["uv", "run", "vcp", "model", "list", "--config", str(temp_config)],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)
        # endregion Run the model list command

        # region Validate table header in result.stdout
        self.validate_model_list_standard_output(result)
        # endregion Validate table header in result.stdout

    @pytest.mark.e2e
    def test_model_list_with_json_option(self, session_auth):
        app_env, _ = session_auth

        # region Run the model list command
        result = subprocess.run(
            ["uv", "run", "vcp", "model", "list", "--format", "json"],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)
        # endregion Run the model list command

        # region Validate JSON output format
        self.assert_successful_command(result, "model list --format json")
        self.assert_no_errors(result)

        # Parse and validate JSON structure
        try:
            result.stdout = result.stdout.replace(
                self.KNOWN_ISSUE_VC_4157, ""
            )  # TODO: Remove once VC-4157 is fixed
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON output: {e}\nOutput:\n{result.stdout}")

        # Validate expected JSON structure
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
        assert (
            "models" in data
        ), f"Missing 'models' key in JSON output. Keys: {list(data.keys())}"
        assert isinstance(
            data["models"], list
        ), f"Expected 'models' to be a list, got {type(data['models'])}"
        # endregion Validate JSON output format
