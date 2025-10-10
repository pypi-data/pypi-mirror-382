import subprocess
import tempfile
import uuid
from pathlib import Path

import pytest

from tests.e2e.model.base_model_test import BaseModelTest


class TestModelAssistE2E(BaseModelTest):
    def setup_method(self):
        """Initialize instance variables for teardown."""
        self.model_name = None
        self.app_env = None
        self.model_version = None

    def teardown_method(self):
        """Clean up GitHub repository created during test."""
        if not self.model_name or not self.app_env:
            return
        self.cleanup_github_repo(self.app_env, self.model_name, self.model_version)

    @pytest.mark.e2e
    def test_model_assist_end_to_end(self, session_auth):
        """
        Test the model assist from initialization to submission and acceptance.
        This test covers the model submission lifecycle, including:
        - Model initialization
        - Model status checks
          - Initialized
          - Submitted
          - Accepted
        - Model assist steps
          - Metadata step
          - Copy weights step
          - Package model step
          - Submit model step

        VCP CLI commands used:
        - vcp model init
        - vcp model status
        - vcp model assist
        - vcp model submit

        This test is designed to ensure that the model assist is working as expected.

        """
        app_env, temp_config = session_auth
        self.app_env = app_env

        with tempfile.TemporaryDirectory() as work_dir:
            work_path = Path(work_dir)

            unique = uuid.uuid4().hex[:8]
            model_name = f"test-e2e-assist-model-{unique}"
            self.model_name = model_name
            model_version = "v1.0.0"
            self.model_version = model_version

            # region Prepare git and template environment
            env_with_git, _template_dir, cleanup = self.prepare_git_and_template_env(
                app_env, Path(temp_config)
            )
            # endregion Prepare git and template environment

            # region Run model init
            try:
                init_cmd = [
                    "uv",
                    "run",
                    "vcp",
                    "model",
                    "init",
                    "--model-name",
                    model_name,
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

                print(init_result.stdout)
                print(init_result.stderr)

                assert (
                    init_result.returncode == 0
                ), f"init failed: {init_result.stderr}\n{init_result.stdout}"
                assert (
                    "Model initialization completed successfully!" in init_result.stdout
                )
                assert f"Work directory: {work_dir}" in init_result.stdout
            finally:
                cleanup()
            # endregion Run model init

            # region Run model status and assert initialized
            status_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "status",
                "--format",
                "json",
            ]

            status_proc = subprocess.run(
                status_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            self.assert_successful_command(status_proc, "model status")
            model = self.get_model_status_json(
                status_proc.stdout, model_name, model_version
            )
            assert (
                model
            ), f"Could not parse JSON from model status output: {status_proc.stdout}"

            assert model, f"Model not found in payload: {model}"
            assert (
                model.get("status") == "initialized"
            ), f"Model status is not initialized: {model}"

            print(f"model: {model}")
            # endregion Run model status and assert initialized

            # region Prepare assist environment
            (work_path / "copier.yml").write_text("min_version: '0.0.0'\n")
            (work_path / ".copier-answers.yml").write_text("{}\n")
            # endregion Prepare assist environment

            # region Run assist status and assert metadata step is next
            assist_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "assist",
                "--work-dir",
                work_dir,
            ]

            assist_result = subprocess.run(
                assist_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(assist_result.stdout)
            print(assist_result.stderr)

            assert (
                assist_result.returncode == 0
            ), f"assist failed: {assist_result.stderr}\n{assist_result.stdout}"
            assert "VCP Model Workflow Status" in assist_result.stdout
            assert "Next Step: Review Files" in assist_result.stdout
            # endregion Run assist status and assert metadata step is next

            # region Run assist metadata and assert copy weights step is next
            # Edit metadata with required fields and mark files as recently modified
            metadata_path = work_path / "model_card_docs" / "model_card_metadata.yaml"
            metadata_content = (
                f"model_display_name: {model_name}\n"
                f"model_version: {model_version}\n"
                "model_description: E2E assist test model description\n"
            )
            metadata_path.write_text(metadata_content)

            # Touch README to count as an edited key file
            (work_path / "README.md").write_text(
                f"# {model_name}\n\nUpdated by assist e2e test\n"
            )

            # Check assist again; next step should be Copy Weights
            assist_result = subprocess.run(
                assist_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(assist_result.stdout)
            print(assist_result.stderr)

            self.assert_successful_command(
                assist_result, "model assist (after metadata)"
            )
            assert "VCP Model Workflow Status" in assist_result.stdout
            assert "Next Step: Copy Weights" in assist_result.stdout
            # endregion Run assist metadata and assert copy weights step is next

            # region Run assist weights and assert package step is next
            # Create *_mlflow_pkg/model_data and add a non-gitkeep file
            mlflow_pkg = work_path / "example_mlflow_pkg"
            model_data_dir = mlflow_pkg / "model_data"
            model_data_dir.mkdir(parents=True, exist_ok=True)
            (model_data_dir / "weights.bin").write_bytes(b"dummy-weights\n")

            # Re-run assist; next step should be Package Model
            assist_result = subprocess.run(
                assist_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(assist_result.stdout)
            print(assist_result.stderr)

            self.assert_successful_command(
                assist_result, "model assist (after weights)"
            )
            assert "VCP Model Workflow Status" in assist_result.stdout
            assert "Next Step: Package Model" in assist_result.stdout
            # endregion Run assist weights and assert package step is next

            # region Run assist package and assert submit step is next
            # Create mlflow package artifact directory with at least one file
            artifact_dir = work_path / "example_mlflow_pkg" / "mlflow_model_artifact"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "README.txt").write_text("artifact contents for e2e test\n")

            # Re-run assist; next step should be Stage Files
            assist_result = subprocess.run(
                assist_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(assist_result.stdout)
            print(assist_result.stderr)

            self.assert_successful_command(
                assist_result, "model assist (after package)"
            )
            assert "VCP Model Workflow Status" in assist_result.stdout
            assert "Next Step: Submit Model" in assist_result.stdout
            # endregion Run assist package and assert submit step is next

            # region Run assist submit and assert success
            # Convert weights to staged pointers to satisfy submit validations
            # Replace non-.ptr file with a .ptr pointer file
            (model_data_dir / "weights.bin").unlink(missing_ok=True)
            (model_data_dir / "weights.bin.ptr").write_text("{}\n")

            # Ensure a git repo and commit exist to satisfy submit checks
            subprocess.run(["git", "init"], cwd=work_dir, env=env_with_git, check=False)

            # Set author identity
            subprocess.run(
                ["git", "config", "user.name", "E2E Test"],
                cwd=work_dir,
                env=env_with_git,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=work_dir,
                env=env_with_git,
                check=True,
            )

            subprocess.run(
                ["git", "add", "."], cwd=work_dir, env=env_with_git, check=False
            )
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.email=devnull@example.com",
                    "-c",
                    "user.name=E2E Assist Test",
                    "commit",
                    "-m",
                    f"feat: model {model_name} initial files",
                ],
                cwd=work_dir,
                env=env_with_git,
                check=False,
            )

            submit_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "submit",
                "--work-dir",
                work_dir,
            ]

            submit_result = subprocess.run(
                submit_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(submit_result.stdout)
            print(submit_result.stderr)

            assert (
                submit_result.returncode == 0
            ), f"submit failed: {submit_result.stderr}\n{submit_result.stdout}"
            assert "Starting model submission" in submit_result.stdout
            assert "✅ Init command validation passed" in submit_result.stdout
            assert "Validating stage command was run" in submit_result.stdout
            assert "Model data submitted successfully" in submit_result.stdout
            # endregion Run assist submit and assert success

            # region Run assist and assert "🎉 Workflow Successfully Completed!"
            assist_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "assist",
                "--work-dir",
                work_dir,
            ]

            assist_result = subprocess.run(
                assist_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            print(assist_result.stdout)
            print(assist_result.stderr)

            assert "🎉 Workflow Successfully Completed!" in assist_result.stdout
            # endregion Run assist and assert "🎉 Workflow Successfully Completed!"

            # region Run model status and assert submitted
            status_cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "status",
                "--format",
                "json",
            ]

            status_proc = subprocess.run(
                status_cmd,
                env=env_with_git,
                capture_output=True,
                text=True,
            )

            self.assert_successful_command(status_proc, "model status")
            model = self.get_model_status_json(
                status_proc.stdout, model_name, model_version
            )
            assert (
                model
            ), f"Could not parse JSON from model status output: {status_proc.stdout}"

            assert model, f"Model not found in payload: {model}"
            assert (
                model.get("status") == "submitted"
            ), f"Model status is not submitted: {model}"

            assert (
                f"github.com/{self.CZ_MODEL_CONTRIBUTIONS}/{model_name}"
                in model.get("pr_url")
            ), f"Model PR URL does not include github.com/{self.CZ_MODEL_CONTRIBUTIONS}/{model_name}: {model}"

            print(f"model: {model}")
            # endregion Run model status and assert submitted
