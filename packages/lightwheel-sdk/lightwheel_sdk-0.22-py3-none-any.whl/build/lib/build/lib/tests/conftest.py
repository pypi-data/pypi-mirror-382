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
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import requests
from lightwheel_sdk.loader.client import LightwheelClient


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_requests():
    """Mock requests module for testing HTTP calls."""
    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        yield mock_post, mock_get


@pytest.fixture
def mock_client():
    """Create a mock LightwheelClient for testing."""
    client = Mock(spec=LightwheelClient)
    client.host = "https://api.lightwheel.net"
    client.headers = {}
    client.cache_path = Path("/tmp/test_cache.json")
    return client


@pytest.fixture
def sample_api_response():
    """Sample API response for testing."""
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.json.return_value = {"token": "test_token_123", "data": {"id": "test_id", "name": "test_name"}}
    response.text = "Success"
    return response


@pytest.fixture
def sample_error_response():
    """Sample error API response for testing."""
    response = Mock(spec=requests.Response)
    response.status_code = 401
    response.text = "Unauthorized"
    response.json.return_value = {"message": "Authentication failed"}
    return response
