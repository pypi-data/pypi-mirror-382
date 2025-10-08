"""
Tests for the Memara Python SDK client.
"""

from unittest.mock import Mock, patch

import httpx
import pytest

from memara import Memara, MemaraAPIError, MemaraAuthError
from memara.models import Memory, Space


class TestMemaraClient:
    """Test cases for the main Memara client."""

    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = Memara(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.memara.io"
        client.close()

    def test_init_with_env_var(self):
        """Test client initialization with environment variable."""
        with patch.dict("os.environ", {"MEMARA_API_KEY": "env_test_key"}):
            client = Memara()
            assert client.api_key == "env_test_key"
            client.close()

    def test_init_without_api_key_raises_error(self):
        """Test that missing API key raises MemaraAuthError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(MemaraAuthError):
                Memara()

    @patch("httpx.Client")
    def test_context_manager(self, mock_client):
        """Test client as context manager."""
        mock_instance = Mock()
        mock_client.return_value = mock_instance

        with Memara(api_key="test_key") as client:
            assert client.api_key == "test_key"

        mock_instance.close.assert_called_once()

    @patch("httpx.Client.request")
    def test_create_memory_success(self, mock_request):
        """Test successful memory creation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {
            "id": "mem_123",
            "content": "Test memory",
            "tags": ["test"],
            "source": "sdk",
            "importance": 5,
            "space_id": None,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "metadata": {},
        }
        mock_request.return_value = mock_response

        with Memara(api_key="test_key") as client:
            memory = client.create_memory(content="Test memory", tags=["test"])

            assert isinstance(memory, Memory)
            assert memory.id == "mem_123"
            assert memory.content == "Test memory"
            assert memory.tags == ["test"]

    @patch("httpx.Client.request")
    def test_search_memories_success(self, mock_request):
        """Test successful memory search."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = [
            {
                "id": "mem_123",
                "content": "Test memory",
                "tags": ["test"],
                "source": "sdk",
                "importance": 5,
                "space_id": None,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "metadata": {},
            }
        ]
        mock_request.return_value = mock_response

        with Memara(api_key="test_key") as client:
            memories = client.search_memories("test query")

            assert len(memories) == 1
            assert isinstance(memories[0], Memory)
            assert memories[0].content == "Test memory"

    @patch("httpx.Client.request")
    def test_api_error_handling(self, mock_request):
        """Test API error handling."""
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.is_success = False
        mock_response.json.return_value = {"detail": "Bad request"}
        mock_request.return_value = mock_response

        with Memara(api_key="test_key") as client:
            with pytest.raises(MemaraAPIError):
                client.create_memory("test")

    @patch("httpx.Client.request")
    def test_auth_error_handling(self, mock_request):
        """Test authentication error handling."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.is_success = False
        mock_request.return_value = mock_response

        with Memara(api_key="invalid_key") as client:
            with pytest.raises(MemaraAuthError):
                client.create_memory("test")


class TestMemoryModel:
    """Test cases for Memory model."""

    def test_memory_model_creation(self):
        """Test creating a Memory model instance."""
        memory_data = {
            "id": "mem_123",
            "content": "Test content",
            "tags": ["tag1", "tag2"],
            "source": "test",
            "importance": 7,
            "space_id": "space_123",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "metadata": {"key": "value"},
        }

        memory = Memory(**memory_data)

        assert memory.id == "mem_123"
        assert memory.content == "Test content"
        assert memory.tags == ["tag1", "tag2"]
        assert memory.importance == 7
        assert memory.metadata == {"key": "value"}


class TestSpaceModel:
    """Test cases for Space model."""

    def test_space_model_creation(self):
        """Test creating a Space model instance."""
        space_data = {
            "id": "space_123",
            "name": "Test Space",
            "icon": "🚀",
            "color": "#6366F1",
            "template_type": "work",
            "privacy_level": "personal",
            "memory_count": 5,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        space = Space(**space_data)

        assert space.id == "space_123"
        assert space.name == "Test Space"
        assert space.icon == "🚀"
        assert space.memory_count == 5
