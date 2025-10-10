import subprocess
import tempfile

import pytest

from tests.e2e.model.base_model_test import BaseModelTest


class TestModelDownload(BaseModelTest):
    NON_EXISTENT_MODEL = "nonexistent-model-12345"
    NON_EXISTENT_MODEL_VERSION = "1"

    @pytest.mark.e2e
    def test_model_download_of_non_existent_model(self, session_auth):
        app_env, _ = session_auth

        model = self.NON_EXISTENT_MODEL
        version = self.NON_EXISTENT_MODEL_VERSION

        with tempfile.TemporaryDirectory() as output_dir:
            # region Run the download command
            cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "download",
                "--model",
                model,
                "--version",
                version,
                "--output",
                output_dir,
            ]

            result = subprocess.run(
                cmd,
                env=app_env,
                capture_output=True,
                text=True,
            )

            print(result.stdout)
            print(result.stderr)
            # endregion Run the download command

            # region Validate output of download of non-existent model
            self.validate_download_nonexistent_model(result, output_dir, model, version)
            # endregion Validate output of download of non-existent model

    @pytest.mark.e2e
    def test_model_download_of_non_existent_model_with_config_option(
        self, session_auth
    ):
        app_env, temp_config = session_auth

        model = self.NON_EXISTENT_MODEL
        version = self.NON_EXISTENT_MODEL_VERSION

        with tempfile.TemporaryDirectory() as output_dir:
            # region Run the download command
            cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "download",
                "--model",
                model,
                "--version",
                version,
                "--output",
                output_dir,
                "--config",
                str(temp_config),
            ]

            result = subprocess.run(
                cmd,
                env=app_env,
                capture_output=True,
                text=True,
            )

            print(result.stdout)
            print(result.stderr)
            # endregion Run the download command

            # region Validate output of download of non-existent model
            self.validate_download_nonexistent_model(result, output_dir, model, version)
            # endregion Validate output of download of non-existent model

    @pytest.mark.e2e
    def test_model_download_of_non_existent_model_with_verbose_option(
        self, session_auth
    ):
        app_env, _ = session_auth

        model = self.NON_EXISTENT_MODEL
        version = self.NON_EXISTENT_MODEL_VERSION

        with tempfile.TemporaryDirectory() as output_dir:
            # region Run the download command
            cmd = [
                "uv",
                "run",
                "vcp",
                "model",
                "download",
                "--model",
                model,
                "--version",
                version,
                "--output",
                output_dir,
                "--verbose",
            ]

            result = subprocess.run(
                cmd,
                env=app_env,
                capture_output=True,
                text=True,
            )

            print(result.stdout)
            print(result.stderr)
            # endregion Run the download command

            # region Validate output of download of non-existent model
            self.validate_download_nonexistent_model(result, output_dir, model, version)
            # endregion Validate output of download of non-existent model
