import json
import subprocess


class BaseDataTest:
    """Base class for data e2e tests with common validation methods."""

    def assert_successful_command(
        self, result: subprocess.CompletedProcess, command_name: str = ""
    ):
        """Assert command succeeded with helpful error message."""
        assert (
            result.returncode == 0
        ), f"{command_name} failed: {result.stderr}\n{result.stdout}"

    def assert_table_output(
        self, result: subprocess.CompletedProcess, expected_columns: list
    ):
        """Assert table output contains expected columns."""
        for column in expected_columns:
            assert column in result.stdout, f"Missing column '{column}' in output"

    def assert_no_errors(self, result: subprocess.CompletedProcess):
        """Assert no errors in command output."""
        assert (
            "Error:" not in result.stdout.strip()
        ), f"Found errors in output: {result.stdout}"

    def assert_no_traceback(self, result: subprocess.CompletedProcess):
        """Assert no traceback in output."""
        assert (
            "Traceback" not in result.stdout
        ), f"Found traceback in output: {result.stdout}"

    def assert_json_valid(self, result: subprocess.CompletedProcess) -> dict:
        """Assert output is valid JSON and return parsed data."""
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise AssertionError(
                f"Invalid JSON output: {e}\nOutput:\n{result.stdout}"
            ) from e

    def assert_contains_dataset_fields(self, data: dict):
        """Assert data contains expected dataset fields."""
        required_fields = ["internal_id", "label"]
        for field in required_fields:
            assert field in data, f"Missing required field '{field}' in dataset"
