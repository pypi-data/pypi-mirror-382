from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from intuned_browser.intuned_services.cache.cache import Cache
from intuned_browser.intuned_services.cache.cache import validate_key
from intuned_browser.intuned_services.cache.types import CacheGetResponse
from intuned_browser.intuned_services.cache.types import CacheSetRequest


class TestValidateKey:
    def test_valid_key(self):
        assert validate_key("valid_key") == "valid_key"
        assert validate_key("a") == "a"
        assert validate_key("key123") == "key123"

    def test_empty_key_raises_error(self):
        with pytest.raises(ValueError, match="Key must be at least 1 character long"):
            validate_key("")

    def test_forbidden_characters_raise_error(self):
        with pytest.raises(ValueError, match='Key cannot contain the following characters: ":" or "#"'):
            validate_key("key:with:colon")

        with pytest.raises(ValueError, match='Key cannot contain the following characters: ":" or "#"'):
            validate_key("key#with#hash")


class TestCache:
    @pytest.fixture
    def cache(self):
        return Cache()

    @patch("intuned_browser.intuned_services.cache.cache.call_backend_function")
    @pytest.mark.asyncio
    async def test_get_returns_value_when_found(self, mock_call_backend, cache):
        # Setup
        mock_response = MagicMock()
        mock_response.value = {"value": "cached_data"}
        mock_call_backend.return_value = mock_response

        # Execute
        result = await cache.get("test_key")

        # Assert
        assert result == "cached_data"
        mock_call_backend.assert_called_once_with(
            name="cache/test_key", method="GET", validation_model=CacheGetResponse
        )

    @patch("intuned_browser.intuned_services.cache.cache.call_backend_function")
    @pytest.mark.asyncio
    async def test_get_returns_none_when_no_response(self, mock_call_backend, cache):
        mock_call_backend.return_value = None

        result = await cache.get("test_key")

        assert result is None

    @patch("intuned_browser.intuned_services.cache.cache.call_backend_function")
    @pytest.mark.asyncio
    async def test_get_returns_none_when_no_value(self, mock_call_backend, cache):
        mock_response = MagicMock()
        mock_response.value = None
        mock_call_backend.return_value = mock_response

        result = await cache.get("test_key")

        assert result is None

    @patch("intuned_browser.intuned_services.cache.cache.call_backend_function")
    @pytest.mark.asyncio
    async def test_get_validates_key(self, mock_call_backend, cache):
        cache_value = await cache.get("invalid:key")
        assert cache_value is None

    @patch("intuned_browser.intuned_services.cache.cache.call_backend_function")
    @pytest.mark.asyncio
    async def test_set_calls_backend_correctly(self, mock_call_backend, cache):
        test_value = {"data": "test"}

        await cache.set("test_key", test_value)

        mock_call_backend.assert_called_once()
        call_args = mock_call_backend.call_args

        assert call_args[0][0] == "cache/test_key"  # first positional arg
        assert call_args[1]["method"] == "PUT"
        assert call_args[1]["validation_model"].__name__ == "CacheSetResponse"
        assert isinstance(call_args[1]["params"], CacheSetRequest)
        assert call_args[1]["params"].value == test_value

    @patch("intuned_browser.intuned_services.cache.cache.call_backend_function")
    @pytest.mark.asyncio
    async def test_set_validates_key(self, mock_call_backend, cache):
        cache_value = await cache.set("invalid#key", "value")
        assert cache_value is None
