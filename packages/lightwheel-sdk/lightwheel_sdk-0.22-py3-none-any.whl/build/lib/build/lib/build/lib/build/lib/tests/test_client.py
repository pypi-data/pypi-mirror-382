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
import os
import json
from unittest.mock import Mock, patch
from lightwheel_sdk.loader.client import LightwheelClient
from lightwheel_sdk.loader.exception import ApiException


class TestLightwheelClient:
    """Test cases for LightwheelClient class."""

    @patch("os.environ.get")
    def test_init_with_default_host(self, mock_environ_get):
        """Test client initialization with default host."""
        mock_environ_get.return_value = None
        client = LightwheelClient()
        assert client.host == "https://api.lightwheel.net"
        assert client.base_timeout == 10
        assert isinstance(client.headers, dict)

    def test_init_with_custom_host(self):
        """Test client initialization with custom host."""
        client = LightwheelClient(host="https://custom.api.com")
        assert client.host == "https://custom.api.com"
        assert client.base_timeout == 10

    def test_init_with_custom_timeout(self):
        """Test client initialization with custom timeout."""
        client = LightwheelClient(base_timeout=30)
        assert client.base_timeout == 30

    def test_init_with_env_host(self):
        """Test client initialization with environment variable host."""
        with patch.dict(os.environ, {"LW_API_ENDPOINT": "https://env.api.com"}):
            client = LightwheelClient()
            assert client.host == "https://env.api.com"

    def test_init_strips_trailing_slash(self):
        """Test that host trailing slash is stripped."""
        client = LightwheelClient(host="https://api.lightwheel.net/")
        assert client.host == "https://api.lightwheel.net"

    def test_get_headers(self):
        """Test getting headers."""
        client = LightwheelClient()
        client.headers = {"Authorization": "Bearer token"}
        assert client._get_headers() == {"Authorization": "Bearer token"}

    def test_update_header(self):
        """Test updating headers."""
        client = LightwheelClient()
        client._update_header("Authorization", "Bearer token")
        assert client.headers["Authorization"] == "Bearer token"

    def test_post_success(self, mock_requests):
        """Test successful POST request."""
        mock_post, _ = mock_requests
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        client = LightwheelClient()
        response = client.post("/test/path", data={"key": "value"})

        assert response == mock_response
        mock_post.assert_called_once_with(f"{client.host}/test/path", headers=client.headers, json={"key": "value"}, timeout=10)

    def test_post_with_custom_timeout(self, mock_requests):
        """Test POST request with custom timeout."""
        mock_post, _ = mock_requests
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        client = LightwheelClient()
        client.post("/test/path", data={"key": "value"}, timeout=30)

        mock_post.assert_called_once_with("https://api.lightwheel.net/test/path", headers=client.headers, json={"key": "value"}, timeout=30)

    def test_post_401_error(self, mock_requests):
        """Test POST request with 401 error."""

        def post_side_effect(*args, **kwargs):
            mock_response = Mock()
            if args[0] == "https://api.lightwheel.net/test/path":
                mock_response.status_code = 401
                mock_response.url = args[0]
            else:
                mock_response.status_code = 200
                mock_response.url = args[0]
                mock_response.json.return_value = {"token": "test_token"}
            return mock_response

        mock_post, _ = mock_requests
        mock_post.side_effect = post_side_effect

        client = LightwheelClient()

        with pytest.raises(Exception) as exc_info:
            client.post("/test/path", data={"key": "value"})
        mock_post.asset_called_times(2)
        assert "/test/path" in str(exc_info.value)

    def test_post_non_200_error(self, mock_requests):
        """Test POST request with non-200 status code."""
        mock_post, _ = mock_requests
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        client = LightwheelClient()

        with pytest.raises(ApiException) as exc_info:
            client.post("/test/path", data={"key": "value"})

        assert "/test/path" in str(exc_info.value)

    @patch("builtins.input")
    @patch("getpass.getpass")
    def test_login_success(self, mock_getpass, mock_input, mock_requests, temp_cache_dir):
        """Test successful login."""
        mock_post, _ = mock_requests
        mock_input.return_value = "testuser"
        mock_getpass.return_value = "testpass"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "test_token", "refreshToken": "test_refresh_token"}
        mock_post.return_value = mock_response

        client = LightwheelClient()
        client.cache_path = temp_cache_dir / "account.json"

        headers = client.login(force_login=True)
        account_cache = client.cache_path.read_text(encoding="utf-8")
        assert account_cache == json.dumps({"username": "testuser", "token": "test_token", "refreshToken": "test_refresh_token"}, indent=4)

        assert headers["Authorization"] == "Bearer test_token"
        assert headers["UserName"] == "testuser"
        assert client.headers["Authorization"] == "Bearer test_token"
        assert client.headers["UserName"] == "testuser"

    def test_login_with_credentials(self, mock_requests, temp_cache_dir):
        """Test login with provided credentials."""
        mock_post, _ = mock_requests
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "test_token", "refreshToken": "test_refresh_token"}
        mock_post.return_value = mock_response

        client = LightwheelClient()
        client.cache_path = temp_cache_dir / "account.json"

        headers = client.login(force_login=True, username="testuser", password="testpass")

        assert headers["Authorization"] == "Bearer test_token"
        assert headers["UserName"] == "testuser"
        account_cache = client.cache_path.read_text(encoding="utf-8")
        assert account_cache == json.dumps({"username": "testuser", "token": "test_token", "refreshToken": "test_refresh_token"}, indent=4)

    def test_login_from_cache(self, temp_cache_dir):
        """Test login using cached credentials."""
        cache_data = {"username": "cached_user", "token": "cached_token", "refreshToken": "cached_refresh_token"}

        with open(temp_cache_dir / "account.json", "w", encoding="utf-8") as f:
            json.dump(cache_data, f)

        client = LightwheelClient()
        client.cache_path = temp_cache_dir / "account.json"

        headers = client.login()

        assert headers["Authorization"] == "Bearer cached_token"
        assert headers["UserName"] == "cached_user"

    def test_logout(self, temp_cache_dir):
        """Test logout functionality."""
        # Create a cache file
        cache_file = temp_cache_dir / "account.json"
        cache_file.write_text('{"test": "data"}')

        client = LightwheelClient()
        client.cache_path = cache_file
        client.headers = {"Authorization": "Bearer token", "UserName": "user"}

        client.logout()

        # Check that cache file is deleted and headers are cleared
        assert not cache_file.exists()
        assert client.headers["Authorization"] == ""
        assert client.headers["UserName"] == ""

    def test_init_headers_from_env(self):
        """Test initialization of headers from environment variables."""
        env_vars = {"LW_SDK_HEADERS_CUSTOM_HEADER": "custom_value", "LW_SDK_HEADERS_ANOTHER_HEADER": "another_value", "LoaderUserName": "env_user", "LoaderToken": "env_token"}

        with patch.dict(os.environ, env_vars):
            client = LightwheelClient()

            assert client.headers["custom-header"] == "custom_value"
            assert client.headers["another-header"] == "another_value"
            assert client.headers["Authorization"] == "Bearer env_token"
            assert client.headers["UserName"] == "env_user"
