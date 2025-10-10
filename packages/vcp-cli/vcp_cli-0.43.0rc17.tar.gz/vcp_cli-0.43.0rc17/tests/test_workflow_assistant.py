"""
Unit tests for the ModelWorkflowAssistant class.
"""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.vcp.commands.model.workflow_assistant import ModelWorkflowAssistant


class TestModelWorkflowAssistant:
    """Test cases for ModelWorkflowAssistant."""

    def setup_method(self):
        """Set up test fixtures."""
        self.assistant = ModelWorkflowAssistant()
        self.temp_dir = tempfile.mkdtemp()
        self.work_path = Path(self.temp_dir)

        # Initialize git repository for tests
        subprocess.run(["git", "init"], cwd=self.temp_dir, check=True)

        # Configure git user identity for tests
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=self.temp_dir,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"], cwd=self.temp_dir, check=True
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_submit_step_no_metadata_file(self):
        """Test _validate_submit_step when metadata file doesn't exist."""
        result = self.assistant._validate_submit_step(self.temp_dir)

        assert result[0] is False
        assert "Model configuration file not found" in result[1]
        assert result[2] == {}

    def test_validate_submit_step_incomplete_metadata(self):
        """Test _validate_submit_step with incomplete metadata."""
        # Create metadata file with missing fields
        metadata_file = self.work_path / ".model-metadata"
        with open(metadata_file, "w") as f:
            json.dump({"model_name": "test-model"}, f)

        # Commit the file to avoid uncommitted changes error
        subprocess.run(["git", "add", ".model-metadata"], cwd=self.temp_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Add metadata"], cwd=self.temp_dir, check=True
        )

        result = self.assistant._validate_submit_step(self.temp_dir)

        assert result[0] is False
        assert "Incomplete model configuration" in result[1]
        assert result[2] == {}

    def test_validate_submit_step_with_uncommitted_changes(self):
        """Test _validate_submit_step when there are uncommitted changes."""
        # Create metadata file
        metadata_file = self.work_path / ".model-metadata"
        with open(metadata_file, "w") as f:
            json.dump(
                {
                    "branch_name": "test-branch",
                    "model_name": "test-model",
                    "model_version": "v1",
                },
                f,
            )

        # Mock git status to return uncommitted changes
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stdout="M modified_file.py\nA new_file.py"
            )

            result = self.assistant._validate_submit_step(self.temp_dir)

            assert result[0] is False
            assert "unsubmitted changes" in result[1]
            assert "uncommitted_files" in result[2]

    def test_validate_submit_step_branch_exists_on_remote(self):
        """Test _validate_submit_step when branch exists on remote."""
        # Create metadata file
        metadata_file = self.work_path / ".model-metadata"
        with open(metadata_file, "w") as f:
            json.dump(
                {
                    "branch_name": "test-branch",
                    "model_name": "test-model",
                    "model_version": "v1",
                },
                f,
            )

        # Create model card file
        model_card_dir = self.work_path / "model_card_docs"
        model_card_dir.mkdir()
        model_card_file = model_card_dir / "model_card_metadata.yaml"
        model_card_file.write_text("model_card: test")

        # Commit the files to avoid uncommitted changes error
        subprocess.run(["git", "add", "."], cwd=self.temp_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Add model files"], cwd=self.temp_dir, check=True
        )

        # Mock git ls-remote to return branch exists
        # Mock git log to return recent commits
        with patch("subprocess.run") as mock_run:

            def mock_run_side_effect(cmd, **kwargs):
                if "status" in cmd:
                    return Mock(returncode=0, stdout="")
                elif "ls-remote" in cmd:
                    return Mock(returncode=0, stdout="abc123 refs/heads/test-branch")
                elif "log" in cmd:
                    return Mock(
                        returncode=0, stdout="abc123 model test-model submission"
                    )
                return Mock(returncode=1, stdout="", stderr="")

            mock_run.side_effect = mock_run_side_effect

            result = self.assistant._validate_submit_step(self.temp_dir)

            assert result[0] is True
            assert "Submit step completed successfully" in result[1]
            assert result[2]["validation_results"]["branch_on_remote"] is True
            assert result[2]["validation_results"]["model_card_exists"] is True
            assert result[2]["validation_results"]["recent_commits"] is True

    def test_validate_submit_step_branch_not_on_remote(self):
        """Test _validate_submit_step when branch doesn't exist on remote."""
        # Create metadata file
        metadata_file = self.work_path / ".model-metadata"
        with open(metadata_file, "w") as f:
            json.dump(
                {
                    "branch_name": "test-branch",
                    "model_name": "test-model",
                    "model_version": "v1",
                },
                f,
            )

        # Create model card file
        model_card_dir = self.work_path / "model_card_docs"
        model_card_dir.mkdir()
        model_card_file = model_card_dir / "model_card_metadata.yaml"
        model_card_file.write_text("model_card: test")

        # Commit the files to avoid uncommitted changes error
        subprocess.run(["git", "add", "."], cwd=self.temp_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Add model files"], cwd=self.temp_dir, check=True
        )

        # Mock git ls-remote to return no branch
        # Mock git log to return recent commits
        with patch("subprocess.run") as mock_run:

            def mock_run_side_effect(cmd, **kwargs):
                if "status" in cmd:
                    return Mock(returncode=0, stdout="")
                elif "ls-remote" in cmd:
                    return Mock(returncode=0, stdout="")
                elif "log" in cmd:
                    return Mock(
                        returncode=0, stdout="abc123 model test-model submission"
                    )
                return Mock(returncode=1, stdout="", stderr="")

            mock_run.side_effect = mock_run_side_effect

            result = self.assistant._validate_submit_step(self.temp_dir)

            assert result[0] is True
            assert "Submit step completed successfully" in result[1]
            assert result[2]["validation_results"]["branch_on_remote"] is False
            assert result[2]["validation_results"]["model_card_exists"] is True
            assert result[2]["validation_results"]["recent_commits"] is True

    def test_validate_submit_step_git_ls_remote_timeout(self):
        """Test _validate_submit_step when git ls-remote times out."""
        # Create metadata file
        metadata_file = self.work_path / ".model-metadata"
        with open(metadata_file, "w") as f:
            json.dump(
                {
                    "branch_name": "test-branch",
                    "model_name": "test-model",
                    "model_version": "v1",
                },
                f,
            )

        # Create model card file
        model_card_dir = self.work_path / "model_card_docs"
        model_card_dir.mkdir()
        model_card_file = model_card_dir / "model_card_metadata.yaml"
        model_card_file.write_text("model_card: test")

        # Commit the files to avoid uncommitted changes error
        subprocess.run(["git", "add", "."], cwd=self.temp_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Add model files"], cwd=self.temp_dir, check=True
        )

        # Mock git ls-remote to timeout
        # Mock git log to return recent commits
        with patch("subprocess.run") as mock_run:

            def mock_run_side_effect(cmd, **kwargs):
                if "status" in cmd:
                    return Mock(returncode=0, stdout="")
                elif "ls-remote" in cmd:
                    raise subprocess.TimeoutExpired(cmd, 10)
                elif "log" in cmd:
                    return Mock(
                        returncode=0, stdout="abc123 model test-model submission"
                    )
                return Mock(returncode=1, stdout="", stderr="")

            mock_run.side_effect = mock_run_side_effect

            result = self.assistant._validate_submit_step(self.temp_dir)

            # Should still succeed even if git ls-remote fails
            assert result[0] is True
            assert "Submit step completed successfully" in result[1]
            assert (
                result[2]["validation_results"]["branch_on_remote"] is False
            )  # Default value
            assert result[2]["validation_results"]["model_card_exists"] is True
            assert result[2]["validation_results"]["recent_commits"] is True

    def test_validate_submit_step_git_ls_remote_subprocess_error(self):
        """Test _validate_submit_step when git ls-remote raises SubprocessError."""
        # Create metadata file
        metadata_file = self.work_path / ".model-metadata"
        with open(metadata_file, "w") as f:
            json.dump(
                {
                    "branch_name": "test-branch",
                    "model_name": "test-model",
                    "model_version": "v1",
                },
                f,
            )

        # Create model card file
        model_card_dir = self.work_path / "model_card_docs"
        model_card_dir.mkdir()
        model_card_file = model_card_dir / "model_card_metadata.yaml"
        model_card_file.write_text("model_card: test")

        # Commit the files to avoid uncommitted changes error
        subprocess.run(["git", "add", "."], cwd=self.temp_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Add model files"], cwd=self.temp_dir, check=True
        )

        # Mock git ls-remote to raise SubprocessError
        # Mock git log to return recent commits
        with patch("subprocess.run") as mock_run:

            def mock_run_side_effect(cmd, **kwargs):
                if "status" in cmd:
                    return Mock(returncode=0, stdout="")
                elif "ls-remote" in cmd:
                    raise subprocess.SubprocessError("Git command failed")
                elif "log" in cmd:
                    return Mock(
                        returncode=0, stdout="abc123 model test-model submission"
                    )
                return Mock(returncode=1, stdout="", stderr="")

            mock_run.side_effect = mock_run_side_effect

            result = self.assistant._validate_submit_step(self.temp_dir)

            # Should still succeed even if git ls-remote fails
            assert result[0] is True
            assert "Submit step completed successfully" in result[1]
            assert (
                result[2]["validation_results"]["branch_on_remote"] is False
            )  # Default value
            assert result[2]["validation_results"]["model_card_exists"] is True
            assert result[2]["validation_results"]["recent_commits"] is True

    def test_validate_submit_step_no_model_card(self):
        """Test _validate_submit_step when model card doesn't exist."""
        # Create metadata file
        metadata_file = self.work_path / ".model-metadata"
        with open(metadata_file, "w") as f:
            json.dump(
                {
                    "branch_name": "test-branch",
                    "model_name": "test-model",
                    "model_version": "v1",
                },
                f,
            )

        # Commit the file to avoid uncommitted changes error
        subprocess.run(["git", "add", ".model-metadata"], cwd=self.temp_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Add metadata"], cwd=self.temp_dir, check=True
        )

        # Mock git ls-remote to return branch exists
        # Mock git log to return recent commits
        with patch("subprocess.run") as mock_run:

            def mock_run_side_effect(cmd, **kwargs):
                if "status" in cmd:
                    return Mock(returncode=0, stdout="")
                elif "ls-remote" in cmd:
                    return Mock(returncode=0, stdout="abc123 refs/heads/test-branch")
                elif "log" in cmd:
                    return Mock(
                        returncode=0, stdout="abc123 model test-model submission"
                    )
                return Mock(returncode=1, stdout="", stderr="")

            mock_run.side_effect = mock_run_side_effect

            result = self.assistant._validate_submit_step(self.temp_dir)

            assert result[0] is True
            assert "Submit step completed successfully" in result[1]
            assert result[2]["validation_results"]["branch_on_remote"] is True
            assert result[2]["validation_results"]["model_card_exists"] is False
            assert result[2]["validation_results"]["recent_commits"] is True

    def test_validate_submit_step_exception_handling(self):
        """Test _validate_submit_step exception handling."""
        # Create metadata file
        metadata_file = self.work_path / ".model-metadata"
        with open(metadata_file, "w") as f:
            json.dump(
                {
                    "branch_name": "test-branch",
                    "model_name": "test-model",
                    "model_version": "v1",
                },
                f,
            )

        # Mock subprocess.run to raise an exception
        with patch("subprocess.run", side_effect=Exception("Unexpected error")):
            result = self.assistant._validate_submit_step(self.temp_dir)

            assert result[0] is False
            assert "Error validating submit step" in result[1]
            assert "Unexpected error" in result[1]
            assert result[2] == {}
