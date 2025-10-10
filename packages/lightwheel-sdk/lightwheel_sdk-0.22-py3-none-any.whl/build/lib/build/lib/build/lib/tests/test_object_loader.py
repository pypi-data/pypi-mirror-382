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
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from lightwheel_sdk.loader.object import ObjectLoader, RegistryQuery
from lightwheel_sdk.loader.exception import ApiException


class TestRegistryQuery:
    """Test cases for RegistryQuery class."""

    def test_init_valid_registry_types(self):
        """Test RegistryQuery initialization with valid registry types."""
        valid_types = ["objects", "fixtures", "textures"]

        for registry_type in valid_types:
            query = RegistryQuery(registry_type)
            assert query.registry_type == registry_type
            assert query.registry_name == []
            assert query.exclude_registry_name == []
            assert query.eqs == []
            assert query.contains_list == []

    def test_init_invalid_registry_type(self):
        """Test RegistryQuery initialization with invalid registry type."""
        with pytest.raises(ValueError) as exc_info:
            RegistryQuery("invalid_type")

        assert "Invalid registry type" in str(exc_info.value)

    def test_init_with_parameters(self):
        """Test RegistryQuery initialization with all parameters."""
        query = RegistryQuery(registry_type="objects", registry_name=["bowl", "cup"], exclude_registry_name=["old_bowl"], equals={"quality": "high"}, contains={"material": "ceramic"})

        assert query.registry_type == "objects"
        assert query.registry_name == ["bowl", "cup"]
        assert query.exclude_registry_name == ["old_bowl"]
        assert query.eqs == [{"key": "quality", "value": "high"}]
        assert query.contains_list == [{"key": "material", "value": "ceramic"}]

    def test_query_file_usd(self):
        """Test query_file with USD file type."""
        query = RegistryQuery("objects", ["bowl"])
        result = query.query_file("USD", file_name="bowl_001", source=["lightwheel"])

        expected = {"file_type": 1, "registry_type": "objects", "eq": [], "contain": [], "source": ["lightwheel"], "registry_name": ["bowl"], "file_name": "bowl_001"}  # USD enum

        assert result == expected

    def test_query_file_mjcf(self):
        """Test query_file with MJCF file type."""
        query = RegistryQuery("fixtures", ["table"])
        result = query.query_file("MJCF", source=["custom"])

        expected = {"file_type": 2, "registry_type": "fixtures", "eq": [], "contain": [], "source": ["custom"], "registry_name": ["table"]}  # MJCF enum

        assert result == expected

    def test_query_file_other_type(self):
        """Test query_file with 'other' file type."""
        query = RegistryQuery("textures", ["wood"])
        result = query.query_file("other")

        expected = {"file_type": 3, "registry_type": "textures", "eq": [], "contain": [], "registry_name": ["wood"]}  # other enum

        assert result == expected

    def test_query_file_invalid_file_type(self):
        """Test query_file with invalid file type."""
        query = RegistryQuery("objects")

        with pytest.raises(ValueError) as exc_info:
            query.query_file("INVALID")

        assert "Invalid file type: INVALID" in str(exc_info.value)

    def test_query_file_without_registry_name_but_with_file_name(self):
        """Test query_file with file_name but without registry_name."""
        query = RegistryQuery("objects")

        with pytest.raises(ValueError) as exc_info:
            query.query_file("USD", file_name="test_file")

        assert "registry_name is required when file_name is provided" in str(exc_info.value)

    def test_query_file_with_projects_and_quality_levels(self):
        """Test query_file with projects and quality levels."""
        query = RegistryQuery("objects", ["bowl"])
        result = query.query_file("USD", projects=["LiAuto", "TestProject"], quality_levels=[1, 2])

        expected = {"file_type": 1, "registry_type": "objects", "eq": [], "contain": [], "registry_name": ["bowl"], "project_names": ["LiAuto", "TestProject"], "quality_levels": [1, 2]}

        assert result == expected

    def test_query_file_with_equals_and_contains(self):
        """Test query_file with equals and contains filters."""
        query = RegistryQuery("objects", equals={"color": "blue"}, contains={"material": "plastic"})
        result = query.query_file("USD")

        expected = {"file_type": 1, "registry_type": "objects", "eq": [{"key": "color", "value": "blue"}], "contain": [{"key": "material", "value": "plastic"}]}

        assert result == expected


class TestObjectLoader:
    """Test cases for ObjectLoader class."""

    def test_init(self, mock_client):
        """Test ObjectLoader initialization."""
        loader = ObjectLoader(mock_client)

        assert loader.client == mock_client
        assert loader.version_cache == []

    def test_acquire_by_registry_success(self, mock_client, mock_requests):
        """Test successful acquire_by_registry call."""
        _, mock_get = mock_requests

        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {"fileUrl": "https://s3.amazonaws.com/test/file.zip", "objectName": "test_object", "fileVersionId": "version_123"}
        mock_client.post.return_value = mock_response

        # Mock the download response
        mock_download_response = Mock()
        mock_download_response.status_code = 200
        mock_download_response.content = b"fake zip content"
        mock_get.return_value = mock_download_response

        loader = ObjectLoader(mock_client)

        with patch("zipfile.ZipFile"), patch("builtins.open", mock_open()), patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.mkdir"):

            _, object_name, result = loader.acquire_by_registry("objects", registry_name=["bowl"], file_type="USD")

        assert object_name == "file"
        assert result["fileVersionId"] == "version_123"
        assert "fileUrl" not in result  # Should be removed

    def test_acquire_by_file_version_success(self, mock_client, mock_requests):
        """Test successful acquire_by_file_version call."""
        _, mock_get = mock_requests

        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {"fileUrl": "https://s3.amazonaws.com/test/file.zip", "objectName": "test_object", "fileVersionId": "version_123"}
        mock_client.post.return_value = mock_response

        # Mock the download response
        mock_download_response = Mock()
        mock_download_response.status_code = 200
        mock_download_response.content = b"fake zip content"
        mock_get.return_value = mock_download_response

        loader = ObjectLoader(mock_client)

        with patch("zipfile.ZipFile"), patch("builtins.open", mock_open()), patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.mkdir"):

            _, object_name, result = loader.acquire_by_file_version("version_123")

        assert object_name == "file"
        assert result["fileVersionId"] == "version_123"
        assert "fileUrl" not in result  # Should be removed

    def test_list_registry(self, mock_client):
        """Test list_registry call."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": [{"name": "objects", "count": 100}, {"name": "fixtures", "count": 50}]}
        mock_client.post.return_value = mock_response

        loader = ObjectLoader(mock_client)
        result = loader.list_registry()

        assert result == [{"name": "objects", "count": 100}, {"name": "fixtures", "count": 50}]

    def test_download_to_cache_usd(self, mock_client, mock_requests):
        """Test download_to_cache for USD file."""
        mock_post, mock_get = mock_requests

        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {"fileUrl": "https://s3.amazonaws.com/test/object.usd.zip"}
        mock_post.return_value = mock_response

        # Mock the download response
        mock_download_response = Mock()
        mock_download_response.status_code = 200
        mock_download_response.content = b"fake zip content"
        mock_get.return_value = mock_download_response

        loader = ObjectLoader(mock_client)

        with patch("zipfile.ZipFile"), patch("builtins.open", mock_open()), patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.mkdir"):

            usd_path, object_name = loader.download_to_cache(mock_response)

        assert object_name == "object"
        assert usd_path.endswith("object.usd")

    def test_download_to_cache_mjcf(self, mock_client, mock_requests):
        """Test download_to_cache for MJCF file."""
        mock_post, mock_get = mock_requests

        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {"fileUrl": "https://s3.amazonaws.com/test/model.mjcf.zip"}
        mock_post.return_value = mock_response

        # Mock the download response
        mock_download_response = Mock()
        mock_download_response.status_code = 200
        mock_download_response.content = b"fake zip content"
        mock_get.return_value = mock_download_response

        loader = ObjectLoader(mock_client)

        with patch("zipfile.ZipFile"), patch("builtins.open", mock_open()), patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.mkdir"):

            # Override get_object_type_and_path to return MJCF
            with patch.object(loader, "get_object_type_and_path", return_value=("MJCF", "model", "https://s3.amazonaws.com/test/model.mjcf.zip", Path("/tmp/model.mjcf.zip"))):
                usd_path, object_name = loader.download_to_cache(mock_response)

        assert object_name == "model"
        assert usd_path.endswith("model.xml")

    def test_download_to_cache_download_error(self, mock_client, mock_requests):
        """Test download_to_cache with download error."""
        mock_post, mock_get = mock_requests

        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {"fileUrl": "https://s3.amazonaws.com/test/object.usd.zip"}
        mock_post.return_value = mock_response

        # Mock the download response with error
        mock_download_response = Mock()
        mock_download_response.status_code = 404
        mock_get.return_value = mock_download_response

        loader = ObjectLoader(mock_client)

        with pytest.raises(ApiException):
            loader.download_to_cache(mock_response)

    def test_get_object_type_and_path(self, mock_client):
        """Test get_object_type_and_path method."""
        mock_response = Mock()
        mock_response.json.return_value = {"fileUrl": "https://s3.amazonaws.com/bucket/path/to/object.usd.zip"}

        loader = ObjectLoader(mock_client)
        object_type, object_name, s3_url, cache_file_path = loader.get_object_type_and_path(mock_response)

        assert object_type == "USD"
        assert object_name == "object"
        assert s3_url == "https://s3.amazonaws.com/bucket/path/to/object.usd.zip"
        assert cache_file_path.name == "object.usd.zip"
