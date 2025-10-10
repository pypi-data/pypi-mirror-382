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

from unittest.mock import Mock
import requests
from lightwheel_sdk.loader.exception import ApiException


class TestApiException:
    """Test cases for ApiException class."""

    def test_init_with_response(self):
        """Test ApiException initialization with response."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        exception = ApiException(mock_response)

        assert exception.response == mock_response
        assert str(exception) == "404 Not Found"

    def test_init_with_different_status_codes(self):
        """Test ApiException with different HTTP status codes."""
        test_cases = [(200, "OK"), (400, "Bad Request"), (401, "Unauthorized"), (403, "Forbidden"), (404, "Not Found"), (500, "Internal Server Error")]

        for status_code, text in test_cases:
            mock_response = Mock(spec=requests.Response)
            mock_response.status_code = status_code
            mock_response.text = text

            exception = ApiException(mock_response)

            assert exception.response == mock_response
            assert str(exception) == f"{status_code} {text}"

    def test_authenticated_failed_true(self):
        """Test authenticated_failed returns True for 401 status."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 401

        exception = ApiException(mock_response)

        assert exception.authenticated_failed() is True

    def test_authenticated_failed_false(self):
        """Test authenticated_failed returns False for non-401 status."""
        test_cases = [200, 400, 403, 404, 500]

        for status_code in test_cases:
            mock_response = Mock(spec=requests.Response)
            mock_response.status_code = status_code

            exception = ApiException(mock_response)

            assert exception.authenticated_failed() is False

    def test_inheritance(self):
        """Test that ApiException inherits from Exception."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Server Error"

        exception = ApiException(mock_response)

        assert isinstance(exception, Exception)
        assert isinstance(exception, ApiException)

    def test_response_attribute_access(self):
        """Test that response attribute can be accessed."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.json.return_value = {"error": "Invalid input"}

        exception = ApiException(mock_response)

        # Test accessing response attributes
        assert exception.response.status_code == 400
        assert exception.response.text == "Bad Request"
        assert exception.response.json() == {"error": "Invalid input"}
