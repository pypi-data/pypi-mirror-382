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

import pytest
from lightwheel_sdk.loader.login import Login


class TestLogin:
    """Test cases for Login class."""

    def test_login_with_force_login(self, mock_client):
        """Test login with force_login=True."""
        expected_headers = {"Authorization": "Bearer token", "UserName": "testuser"}
        mock_client.login.return_value = expected_headers

        login = Login(mock_client)
        result = login.login(force_login=True, username="testuser", password="testpass")

        assert result == expected_headers
        mock_client.login.assert_called_once_with(force_login=True, username="testuser", password="testpass")

    def test_login_without_credentials(self, mock_client):
        """Test login without provided credentials."""
        expected_headers = {"Authorization": "Bearer token", "UserName": "testuser"}
        mock_client.login.return_value = expected_headers

        login = Login(mock_client)
        result = login.login(force_login=True)

        assert result == expected_headers
        mock_client.login.assert_called_once_with(force_login=True, username=None, password=None)

    def test_login_with_default_params(self, mock_client):
        """Test login with default parameters."""
        expected_headers = {"Authorization": "Bearer token", "UserName": "testuser"}
        mock_client.login.return_value = expected_headers

        login = Login(mock_client)
        result = login.login()

        assert result == expected_headers
        mock_client.login.assert_called_once_with(force_login=False, username=None, password=None)

    def test_logout(self, mock_client):
        """Test logout functionality."""
        mock_client.logout.return_value = None

        login = Login(mock_client)
        result = login.logout()

        assert result is None
        mock_client.logout.assert_called_once()

    def test_multiple_login_calls(self, mock_client):
        """Test multiple login calls."""
        expected_headers = {"Authorization": "Bearer token", "UserName": "testuser"}
        mock_client.login.return_value = expected_headers

        login = Login(mock_client)

        # First login
        result1 = login.login(force_login=True)
        assert result1 == expected_headers

        # Second login with different parameters
        result2 = login.login(force_login=False, username="user2", password="pass2")
        assert result2 == expected_headers

        # Verify both calls were made
        assert mock_client.login.call_count == 2
        mock_client.login.assert_any_call(force_login=True, username=None, password=None)
        mock_client.login.assert_any_call(force_login=False, username="user2", password="pass2")

    def test_login_with_client_exception(self, mock_client):
        """Test login when client raises an exception."""
        mock_client.login.side_effect = Exception("Login failed")

        login = Login(mock_client)

        with pytest.raises(Exception) as exc_info:
            login.login(force_login=True)

        assert str(exc_info.value) == "Login failed"
        mock_client.login.assert_called_once()

    def test_logout_with_client_exception(self, mock_client):
        """Test logout when client raises an exception."""
        mock_client.logout.side_effect = Exception("Logout failed")

        login = Login(mock_client)

        with pytest.raises(Exception) as exc_info:
            login.logout()

        assert str(exc_info.value) == "Logout failed"
        mock_client.logout.assert_called_once()
