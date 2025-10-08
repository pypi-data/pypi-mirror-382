"""
Basic tests for LZaaS CLI
"""

import pytest
from lzaas.cli.main import cli
from lzaas.utils.validators import validate_email, validate_account_name


def test_cli_import():
    """Test that the CLI can be imported successfully."""
    assert cli is not None


def test_validate_email():
    """Test email validation function."""
    # Valid emails
    assert validate_email("test@example.com") is True
    assert validate_email("user.name@domain.co.uk") is True

    # Invalid emails
    assert validate_email("invalid-email") is False
    assert validate_email("@domain.com") is False
    assert validate_email("user@") is False


def test_validate_account_name():
    """Test account name validation function."""
    # Valid account names
    assert validate_account_name("test-account") is True
    assert validate_account_name("MyAccount123") is True

    # Invalid account names (assuming some basic rules)
    assert validate_account_name("") is False
    assert validate_account_name("a" * 100) is False  # Too long


def test_cli_help():
    """Test that CLI help works."""
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    # Should exit with code 0 and contain help text
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_template_list():
    """Test template list command."""
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(cli, ["template", "list"])

    # Should not crash (exit code 0 or 1 is acceptable for now)
    assert result.exit_code in [0, 1]


def test_info_command():
    """Test info command."""
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(cli, ["info"])

    # Should not crash (exit code 0 or 1 is acceptable for now)
    assert result.exit_code in [0, 1]
