# Copyright 2025 Lightwheel Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import patch
import pytest
import json

try:
    from click.testing import CliRunner
    from lightwheel_sdk.cli import cli, login, logout, main

    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False


@pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
class TestCLI:
    """Test cases for CLI commands."""

    def test_cli_group(self):
        """Test CLI group creation."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Lightwheel SDK CLI" in result.output

    def test_cli_version_option(self):
        """Test CLI version option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        # Version should be displayed (exact version depends on setup)
        assert result.exit_code == 0

    @patch("lightwheel_sdk.cli.login_manager")
    def test_login_command_without_credentials(self, mock_login_manager):
        """Test login command without provided credentials."""
        mock_login_manager.login.return_value = {"Authorization": "Bearer token"}

        runner = CliRunner()
        result = runner.invoke(login, [])

        assert result.exit_code == 0
        assert "Successfully logged in to Lightwheel!" in result.output
        mock_login_manager.login.assert_called_once_with(force_login=True, username=None, password=None)

    @patch("lightwheel_sdk.cli.login_manager")
    def test_login_command_with_credentials(self, mock_login_manager):
        """Test login command with provided credentials."""
        mock_login_manager.login.return_value = {"Authorization": "Bearer token"}

        runner = CliRunner()
        result = runner.invoke(login, ["--username", "testuser", "--password", "testpass"])

        assert result.exit_code == 0
        assert "Successfully logged in to Lightwheel!" in result.output
        mock_login_manager.login.assert_called_once_with(force_login=True, username="testuser", password="testpass")

    @patch("lightwheel_sdk.cli.login_manager")
    def test_login_command_with_short_options(self, mock_login_manager):
        """Test login command with short option names."""
        mock_login_manager.login.return_value = {"Authorization": "Bearer token"}

        runner = CliRunner()
        result = runner.invoke(login, ["-u", "testuser", "-p", "testpass"])

        assert result.exit_code == 0
        assert "Successfully logged in to Lightwheel!" in result.output
        mock_login_manager.login.assert_called_once_with(force_login=True, username="testuser", password="testpass")

    @patch("lightwheel_sdk.cli.login_manager")
    def test_login_command_failure(self, mock_login_manager):
        """Test login command when login fails."""
        mock_login_manager.login.side_effect = Exception("Login failed")

        runner = CliRunner()
        result = runner.invoke(login, [])

        assert result.exit_code != 0
        assert "Successfully logged in to Lightwheel!" not in result.output

    @patch("lightwheel_sdk.cli.login_manager")
    def test_logout_command_success(self, mock_login_manager):
        """Test logout command success."""
        mock_login_manager.logout.return_value = None

        runner = CliRunner()
        result = runner.invoke(logout, [])

        assert result.exit_code == 0
        assert "Successfully logged out from Lightwheel!" in result.output
        mock_login_manager.logout.assert_called_once()

    @patch("lightwheel_sdk.cli.login_manager")
    def test_logout_command_failure(self, mock_login_manager):
        """Test logout command when logout fails."""
        mock_login_manager.logout.side_effect = Exception("Logout failed")

        runner = CliRunner()
        result = runner.invoke(logout, [])

        assert result.exit_code != 0
        assert "Successfully logged out from Lightwheel!" not in result.output

    def test_cli_help_text(self):
        """Test CLI help text content."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Lightwheel SDK CLI - A Python SDK for interacting with the Lightwheel API." in result.output

    def test_login_help_text(self):
        """Test login command help text."""
        runner = CliRunner()
        result = runner.invoke(login, ["--help"])

        assert result.exit_code == 0
        assert "Log in to Lightwheel." in result.output
        assert "--username" in result.output
        assert "--password" in result.output

    def test_logout_help_text(self):
        """Test logout command help text."""
        runner = CliRunner()
        result = runner.invoke(logout, ["--help"])

        assert result.exit_code == 0
        assert "Log out from Lightwheel." in result.output

    @patch("lightwheel_sdk.cli.login_manager")
    def test_login_command_interactive(self, mock_login_manager):
        """Test login command in interactive mode (no credentials provided)."""
        mock_login_manager.login.return_value = {"Authorization": "Bearer token"}

        runner = CliRunner()
        # Simulate interactive input
        result = runner.invoke(login, [], input="testuser\ntestpass\n")

        assert result.exit_code == 0
        assert "Successfully logged in to Lightwheel!" in result.output
        mock_login_manager.login.assert_called_once_with(force_login=True, username=None, password=None)

    def test_cli_command_structure(self):
        """Test that CLI has the expected command structure."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        # Check that login and logout commands are available
        assert "login" in result.output
        assert "logout" in result.output

    @patch("lightwheel_sdk.cli.login_manager")
    def test_multiple_login_attempts(self, mock_login_manager):
        """Test multiple login attempts."""
        mock_login_manager.login.return_value = {"Authorization": "Bearer token"}

        runner = CliRunner()

        # First login
        result1 = runner.invoke(login, ["-u", "user1", "-p", "pass1"])
        assert result1.exit_code == 0

        # Second login
        result2 = runner.invoke(login, ["-u", "user2", "-p", "pass2"])
        assert result2.exit_code == 0

        # Verify both calls were made
        assert mock_login_manager.login.call_count == 2
        mock_login_manager.login.assert_any_call(force_login=True, username="user1", password="pass1")
        mock_login_manager.login.assert_any_call(force_login=True, username="user2", password="pass2")
