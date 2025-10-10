import pytest
from click.testing import CliRunner

from vcp.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help(config_for_tests, runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
