import json
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path

import requests
import yaml


class BaseModelTest:
    """Base class for model e2e tests with common validation methods."""

    CZ_MODEL_CONTRIBUTIONS = "cz-model-contributions"
    GITHUB_REPOS_ENDPOINT = "https://api.github.com/repos/"

    KNOWN_ISSUE_VC_4157 = "Warning: Could not get metric types for PerturbationExpressionPredictionTask: type object 'PerturbationExpressionPredictionTask' has no attribute 'get_metric_types'"

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

    def assert_no_warnings(self, result: subprocess.CompletedProcess):
        """Assert no warnings in command output (when VC-4157 is fixed)."""
        # TODO: Uncomment once this issue is fixed: https://czi.atlassian.net/browse/VC-4157
        # assert "Warning" not in result.stdout
        pass

    def assert_no_traceback(self, result: subprocess.CompletedProcess):
        """Assert no traceback in output."""
        assert (
            "Traceback" not in result.stdout
        ), f"Found traceback in output: {result.stdout}"

    def assert_success_markers(
        self, result: subprocess.CompletedProcess, success_markers: list
    ):
        """Assert all success markers are present in output."""
        for marker in success_markers:
            assert (
                marker in result.stdout
            ), f"Expected '{marker}' in output, got:\n{result.stdout}"

    def assert_model_info(
        self, result: subprocess.CompletedProcess, model_name: str, model_version: str
    ):
        """Assert model name and version appear in output."""
        expected_model_line = f"Model: {model_name} {model_version}"
        assert (
            expected_model_line in result.stdout
        ), f"Expected '{expected_model_line}' in output"

    def assert_work_directory(self, result: subprocess.CompletedProcess, work_dir: str):
        """Assert work directory appears in output."""
        work_dir_regex = rf"Work directory:.*?(?:\n.*?)?{re.escape(work_dir)}"
        assert re.search(
            work_dir_regex, result.stdout, re.MULTILINE | re.DOTALL
        ), f"Expected Work directory: {work_dir} in \n{result.stdout}"

    def validate_model_submit_success(
        self,
        result: subprocess.CompletedProcess,
        model_name: str,
        model_version: str,
        work_dir: str,
    ):
        """Validate successful model submission output."""
        self.assert_successful_command(result, "model submit")
        assert "Starting model submission" in result.stdout

        success_markers = [
            "Model data submitted successfully",
            " Success ",
        ]
        self.assert_success_markers(result, success_markers)
        self.assert_model_info(result, model_name, model_version)
        self.assert_work_directory(result, work_dir)
        self.assert_no_traceback(result)

    def validate_model_status_output(self, result: subprocess.CompletedProcess):
        """Validate model status command output with common assertions."""
        self.assert_no_errors(result)
        self.assert_no_warnings(result)

        self.assert_successful_command(result, "model status")

        # Use regex to match both full names and truncated versions (with ellipsis)
        assert re.search(r"Model\s+Name", result.stdout), "Model Name column not found"
        assert re.search(r"Vers(ion|…)", result.stdout), "Version column not found"
        assert re.search(r"Stat(us|…)", result.stdout), "Status column not found"
        assert "Total submissions:" in result.stdout

    def validate_download_nonexistent_model(
        self,
        result: subprocess.CompletedProcess,
        output_dir: str,
        model: str,
        version: str,
    ):
        """Validate output for download of a non-existent model and absence of output dir content."""
        # Command should exit cleanly (command handles error messaging itself)
        assert (
            result.returncode == 0
        ), f"download command errored: {result.stderr}\n{result.stdout}"

        # Expect API error messaging
        expected_markers = [
            "API Error",
            "Failed to get download URI",
            "No files found in the API response.",
        ]
        assert any(m in result.stdout for m in expected_markers), (
            "Expected an API error message for non-existent model. Got:\n"
            + result.stdout
        )

        # Verify model-specific directory was not created

        model_dir = Path(output_dir) / f"{model}-{version}"
        assert not model_dir.exists(), f"Unexpected directory created: {model_dir}"

    def validate_model_list_standard_output(self, result: subprocess.CompletedProcess):
        """Validate model list command output with common assertions."""
        self.assert_no_warnings(result)
        self.assert_no_errors(result)

        self.assert_successful_command(result, "model list")
        self.assert_table_output(result, ["Model Name", "Version", "Description"])

        # TODO: Assert 'Retrieved x models' with x > 0

    # region GitHub auth helpers for e2e tests
    def get_id_token(self, app_env: dict) -> str:
        """Load ID token from the CLI's token store using the CLI runtime."""
        proc = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                (
                    "from vcp.utils.token import TokenManager;"
                    "t=TokenManager().load_tokens();"
                    "print(t.id_token) if t else exit(1)"
                ),
            ],
            env=app_env,
            capture_output=True,
            text=True,
        )
        self.assert_successful_command(proc, "load id_token")
        return proc.stdout.strip()

    def get_github_contributions_token(self, app_env: dict, id_token: str) -> str:
        """Exchange ID token for GitHub contributions token via Model Hub API."""
        api_base = app_env["VCP_API_BASE_URL"].rstrip("/")
        resp = requests.get(
            f"{api_base}/api/github/contribution/app/token",
            headers={"Authorization": f"Bearer {id_token}"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["token"]

    def make_noninteractive_git_env(self, app_env: dict, github_token: str):
        """Create env vars and helpers so git uses token and never prompts interactively.

        Returns a tuple of (env_with_git, cleanup_fn).
        """
        askpass_tmpdir = tempfile.TemporaryDirectory()
        askpass_path = Path(askpass_tmpdir.name) / "git_askpass.sh"
        askpass_path.write_text(
            "#!/bin/sh\n"
            'case "$1" in\n'
            "  *[Uu]sername*) echo 'x-access-token' ;;\n"
            "  *[Pp]assword*) echo '" + github_token + "' ;;\n"
            "  *) echo '" + github_token + "' ;;\n"
            "esac\n"
        )
        askpass_path.chmod(stat.S_IRWXU)

        empty_gitconfig_tmp = tempfile.NamedTemporaryFile(delete=False)
        empty_gitconfig_tmp.write(b"")
        empty_gitconfig_tmp.flush()
        empty_gitconfig_tmp.close()

        env_with_git = dict(app_env)
        env_with_git.update({
            "GIT_ASKPASS": str(askpass_path),
            "SSH_ASKPASS": str(askpass_path),
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "never",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": empty_gitconfig_tmp.name,
        })

        def cleanup():
            try:
                askpass_tmpdir.cleanup()
            except Exception:
                pass
            try:
                os.unlink(empty_gitconfig_tmp.name)
            except Exception:
                pass

        return env_with_git, cleanup

    # endregion GitHub auth helpers for e2e tests

    # region Copier template helpers
    def override_template_to_local(self, temp_config_path: Path):
        """Create a minimal local copier template and point config to it.

        Returns a tuple of (template_dir_path, cleanup_fn).
        """
        template_tmpdir = tempfile.TemporaryDirectory()
        template_dir = Path(template_tmpdir.name)

        # Minimal template structure required for init and workflow checks
        (template_dir / "copier.yml").write_text("min_version: '0.0.0'\n")
        (template_dir / "model_card_docs").mkdir(parents=True, exist_ok=True)
        (
            template_dir / "model_card_docs" / "model_card_metadata.yaml.jinja"
        ).write_text(
            "model_name: {{ model_name }}\nversion: {{ model_version }}\nlicense: {{ license_type }}\n"
        )

        # Update session config to point to local template
        cfg_data = yaml.safe_load(Path(temp_config_path).read_text())
        cfg_data.setdefault("models", {}).setdefault("github", {})["template_repo"] = (
            str(template_dir)
        )
        Path(temp_config_path).write_text(yaml.safe_dump(cfg_data))

        def cleanup():
            try:
                template_tmpdir.cleanup()
            except Exception:
                pass

        return template_dir, cleanup

    # endregion Copier template helpers

    # region General helpers
    def cleanup_safely(self, *cleanup_functions):
        """Invoke provided cleanup callables, ignoring exceptions for test robustness."""
        for fn in cleanup_functions:
            try:
                if fn:
                    fn()
            except Exception:
                pass

    def prepare_git_and_template_env(self, app_env: dict, temp_config_path: Path):
        """Prepare staging-ready env and local template for e2e git workflows.

        Returns a tuple of (env_with_git, template_dir, cleanup_fn).
        """
        id_token = self.get_id_token(app_env)
        gh_token = self.get_github_contributions_token(app_env, id_token)

        template_dir, cleanup_template = self.override_template_to_local(
            temp_config_path
        )
        env_with_git, cleanup_git = self.make_noninteractive_git_env(app_env, gh_token)

        def cleanup():
            self.cleanup_safely(cleanup_git, cleanup_template)

        return env_with_git, template_dir, cleanup

    def run_model_init(
        self,
        app_env: dict,
        temp_config: Path,
        model_display_name: str,
        model_version: str,
        work_dir: str,
    ):
        env_with_git, _template_dir, cleanup = self.prepare_git_and_template_env(
            app_env, Path(temp_config)
        )
        try:
            init_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "init",
                "--model-name",
                model_display_name,
                "--model-version",
                model_version,
                "--license-type",
                "MIT",
                "--work-dir",
                work_dir,
            ]

            init_result = subprocess.run(
                init_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            assert (
                init_result.returncode == 0
            ), f"init failed: {init_result.stderr}\n{init_result.stdout}"
        finally:
            cleanup()

    # endregion General helpers

    # region Repo cleanup helper
    def cleanup_github_repo(self, app_env: dict, model_name: str, model_version: str):
        """Delete the GitHub repository created for this test model."""
        try:
            if not model_name or not app_env:
                return

            id_token = self.get_id_token(app_env)
            gh_token = self.get_github_contributions_token(app_env, id_token)
            contributions_org = self.CZ_MODEL_CONTRIBUTIONS

            # Compute target repo name
            target_name = f"{model_name}-{model_version}"
            headers = {
                "Authorization": f"Bearer {gh_token}",
                "Accept": "application/vnd.github+json",
            }
            repo_api = f"{self.GITHUB_REPOS_ENDPOINT}{contributions_org}/{target_name}"
            resp = requests.delete(repo_api, headers=headers, timeout=30)

            if resp.status_code in (202, 204):
                print(f"Teardown: Deleted test repo {contributions_org}/{target_name}")
            elif resp.status_code == 404:
                print(
                    f"Teardown: Repo not found (may not have been created): {contributions_org}/{target_name}"
                )
            else:
                print(
                    f"Teardown: Failed to delete repo {contributions_org}/{target_name}: {resp.status_code} {resp.text}"
                )
        except Exception as e:
            print(f"Teardown: Error during repo cleanup for {model_name}: {e}")

    # endregion Repo cleanup helper

    # region Parsing helpers
    def get_model_status_json(
        self, stdout: str, model_name: str, model_version: str
    ) -> dict:
        """
        Parse the model status JSON output.
        """
        stdout = stdout.replace("\n", "")
        stdout = stdout.replace("\r", "")
        stdout = stdout.replace("\t", "")
        payload = json.loads(stdout)

        submissions = payload.get("submissions", [])
        model = [
            model
            for model in submissions
            if model.get("model_name") == model_name
            and model.get("model_version") == model_version
        ]
        return model[0]

    # endregion Parsing helpers
