"""Unit tests for SerpShot SDK."""

import os
import pytest

from serpshot import (
    AsyncSerpShot,
    AuthHandler,
    AuthenticationError,
    LocationType,
    SearchType,
    SerpShot,
)
from serpshot.models import SearchRequest, SearchResponse


class TestAuthHandler:
    """Test authentication handler."""

    def test_valid_api_key(self):
        """Test valid API key initialization."""
        auth = AuthHandler("valid-api-key-12345")
        assert auth.api_key == "valid-api-key-12345"

    def test_empty_api_key_raises_error(self):
        """Test that empty API key raises error."""
        with pytest.raises(AuthenticationError):
            AuthHandler("")

    def test_none_api_key_raises_error(self):
        """Test that None API key raises error."""
        with pytest.raises(AuthenticationError):
            AuthHandler(None)

    def test_whitespace_api_key_raises_error(self):
        """Test that whitespace-only API key raises error."""
        with pytest.raises(AuthenticationError):
            AuthHandler("   ")

    def test_get_headers(self):
        """Test that headers are properly generated."""
        auth = AuthHandler("test-key")
        headers = auth.get_headers()
        
        assert headers["X-API-Key"] == "test-key"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"


class TestSearchRequest:
    """Test search request model."""

    def test_default_values(self):
        """Test default values are set correctly."""
        request = SearchRequest(queries=["test"])
        
        assert request.queries == ["test"]
        assert request.type == SearchType.SEARCH
        assert request.num == 10
        assert request.page == 1
        assert request.gl == "us"
        assert request.hl == "en"
        assert request.lr == "en"

    def test_custom_values(self):
        """Test custom values are accepted."""
        request = SearchRequest(
            queries=["test query", "another query"],
            type=SearchType.IMAGE,
            num=20,
            page=2,
            gl="cn",
            hl="zh-CN",
            lr="zh-CN",
            location=LocationType.US,
        )
        
        assert request.queries == ["test query", "another query"]
        assert request.type == SearchType.IMAGE
        assert request.num == 20
        assert request.page == 2
        assert request.gl == "cn"
        assert request.hl == "zh-CN"
        assert request.lr == "zh-CN"
        assert request.location == LocationType.US

    def test_queries_validation(self):
        """Test queries validation."""
        # Empty queries list should fail
        with pytest.raises(ValueError):
            SearchRequest(queries=[])
        
        # Very long query should fail
        with pytest.raises(ValueError):
            SearchRequest(queries=["x" * 3000])

    def test_num_validation(self):
        """Test num parameter validation."""
        # Too small
        with pytest.raises(ValueError):
            SearchRequest(queries=["test"], num=0)
        
        # Too large
        with pytest.raises(ValueError):
            SearchRequest(queries=["test"], num=101)

    def test_page_validation(self):
        """Test page parameter validation."""
        # Page must be >= 1
        with pytest.raises(ValueError):
            SearchRequest(queries=["test"], page=0)


class TestBaseClient:
    """Test base client functionality."""

    def test_build_search_params(self):
        """Test search parameter building."""
        client = SerpShot(api_key="test-key-12345")
        
        params = client._build_search_params(
            query="test",
            search_type=SearchType.SEARCH,
            num=20,
            gl="us",
        )
        
        assert params["queries"] == ["test"]
        assert params["type"] == "search"
        assert params["num"] == 20
        assert params["gl"] == "us"
        assert params["page"] == 1

    def test_calculate_credits(self):
        """Test credit calculation logic."""
        client = SerpShot(api_key="test-key-12345")
        
        # Base search
        credits = client._calculate_credits(SearchType.SEARCH, 10)
        assert credits == 1
        
        # Image search
        credits = client._calculate_credits(SearchType.IMAGE, 10)
        assert credits == 2
        
        # High result count
        credits = client._calculate_credits(SearchType.SEARCH, 30)
        assert credits == 3


class TestSyncClient:
    """Test synchronous client."""

    def test_initialization(self):
        """Test client initialization."""
        client = SerpShot(
            api_key="test-key",
            timeout=60.0,
            max_retries=5,
        )
        
        assert client.timeout == 60.0
        assert client.max_retries == 5

    def test_context_manager(self):
        """Test context manager usage."""
        with SerpShot(api_key="test-key-12345") as client:
            assert client is not None

    def test_initialization_without_api_key_raises_error(self):
        """Test that initialization without API key raises error when env var is not set."""
        # Ensure env var is not set
        original_value = os.environ.pop("SERPSHOT_API_KEY", None)
        try:
            with pytest.raises(ValueError, match="API key is required"):
                SerpShot()
        finally:
            # Restore original value if it existed
            if original_value:
                os.environ["SERPSHOT_API_KEY"] = original_value

    def test_initialization_from_env_var(self):
        """Test that initialization reads from environment variable."""
        original_value = os.environ.get("SERPSHOT_API_KEY")
        try:
            os.environ["SERPSHOT_API_KEY"] = "env-test-key-12345"
            client = SerpShot()
            assert client.auth.api_key == "env-test-key-12345"
        finally:
            # Restore original value
            if original_value:
                os.environ["SERPSHOT_API_KEY"] = original_value
            else:
                os.environ.pop("SERPSHOT_API_KEY", None)

    def test_explicit_api_key_overrides_env_var(self):
        """Test that explicit API key takes precedence over environment variable."""
        original_value = os.environ.get("SERPSHOT_API_KEY")
        try:
            os.environ["SERPSHOT_API_KEY"] = "env-test-key"
            client = SerpShot(api_key="explicit-test-key")
            assert client.auth.api_key == "explicit-test-key"
        finally:
            # Restore original value
            if original_value:
                os.environ["SERPSHOT_API_KEY"] = original_value
            else:
                os.environ.pop("SERPSHOT_API_KEY", None)


class TestAsyncClient:
    """Test asynchronous client."""

    def test_initialization(self):
        """Test async client initialization."""
        client = AsyncSerpShot(
            api_key="test-key",
            timeout=60.0,
            max_retries=5,
        )
        
        assert client.timeout == 60.0
        assert client.max_retries == 5

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager usage."""
        async with AsyncSerpShot(api_key="test-key-12345") as client:
            assert client is not None

    def test_initialization_without_api_key_raises_error(self):
        """Test that async initialization without API key raises error when env var is not set."""
        original_value = os.environ.pop("SERPSHOT_API_KEY", None)
        try:
            with pytest.raises(ValueError, match="API key is required"):
                AsyncSerpShot()
        finally:
            # Restore original value if it existed
            if original_value:
                os.environ["SERPSHOT_API_KEY"] = original_value

    def test_initialization_from_env_var(self):
        """Test that async initialization reads from environment variable."""
        original_value = os.environ.get("SERPSHOT_API_KEY")
        try:
            os.environ["SERPSHOT_API_KEY"] = "env-test-key-12345"
            client = AsyncSerpShot()
            assert client.auth.api_key == "env-test-key-12345"
        finally:
            # Restore original value
            if original_value:
                os.environ["SERPSHOT_API_KEY"] = original_value
            else:
                os.environ.pop("SERPSHOT_API_KEY", None)

    def test_explicit_api_key_overrides_env_var(self):
        """Test that explicit API key takes precedence over environment variable."""
        original_value = os.environ.get("SERPSHOT_API_KEY")
        try:
            os.environ["SERPSHOT_API_KEY"] = "env-test-key"
            client = AsyncSerpShot(api_key="explicit-test-key")
            assert client.auth.api_key == "explicit-test-key"
        finally:
            # Restore original value
            if original_value:
                os.environ["SERPSHOT_API_KEY"] = original_value
            else:
                os.environ.pop("SERPSHOT_API_KEY", None)


class TestSearchResponse:
    """Test search response model."""

    def test_parse_response(self):
        """Test parsing API response."""
        data = {
            "success": True,
            "query": "test query",
            "total_results": "1000",
            "search_time": "0.5",
            "results": [
                {
                    "title": "Test Result",
                    "link": "https://example.com",
                    "snippet": "This is a test",
                    "position": 1,
                }
            ],
            "credits_used": 1,
        }
        
        response = SearchResponse.model_validate(data)
        
        assert response.success is True
        assert response.query == "test query"
        assert response.total_results == "1000"
        assert response.search_time == "0.5"
        assert len(response.results) == 1
        assert response.results[0].title == "Test Result"


# Integration test markers
@pytest.mark.integration
class TestIntegration:
    """Integration tests (require real API key)."""

    @pytest.mark.skip(reason="Requires API key and credits")
    def test_real_search(self):
        """Test real API search (requires API key)."""
        api_key = os.getenv("SERPSHOT_API_KEY")
        
        if not api_key:
            pytest.skip("SERPSHOT_API_KEY not set")
        
        # Test with explicit API key
        with SerpShot(api_key=api_key) as client:
            response = client.search("Python", num=5)
            assert response.success
            assert len(response.results) > 0

    @pytest.mark.skip(reason="Requires API key and credits")
    def test_real_search_from_env_var(self):
        """Test real API search using environment variable."""
        api_key = os.getenv("SERPSHOT_API_KEY")
        
        if not api_key:
            pytest.skip("SERPSHOT_API_KEY not set")
        
        # Test with environment variable (should work if env var is set)
        with SerpShot() as client:
            response = client.search("Python", num=5)
            assert response.success
            assert len(response.results) > 0

    @pytest.mark.skip(reason="Requires API key and credits")
    @pytest.mark.asyncio
    async def test_real_async_search(self):
        """Test real async API search (requires API key)."""
        api_key = os.getenv("SERPSHOT_API_KEY")
        
        if not api_key:
            pytest.skip("SERPSHOT_API_KEY not set")
        
        # Test with explicit API key
        async with AsyncSerpShot(api_key=api_key) as client:
            response = await client.search("Python", num=5)
            assert response.success
            assert len(response.results) > 0

    @pytest.mark.skip(reason="Requires API key and credits")
    @pytest.mark.asyncio
    async def test_real_async_search_from_env_var(self):
        """Test real async API search using environment variable."""
        api_key = os.getenv("SERPSHOT_API_KEY")
        
        if not api_key:
            pytest.skip("SERPSHOT_API_KEY not set")
        
        # Test with environment variable (should work if env var is set)
        async with AsyncSerpShot() as client:
            response = await client.search("Python", num=5)
            assert response.success
            assert len(response.results) > 0
