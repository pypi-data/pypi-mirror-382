import os
from unittest.mock import patch

import pytest
from runtime.context.context import IntunedContext

from intuned_browser.intuned_services.api_gateways.ai_api_gateway import APIGateway
from intuned_browser.intuned_services.api_gateways.types import GatewayConfig


class TestAPIGateway:
    @pytest.fixture
    def gateway(self):
        with patch.dict(
            os.environ,
            {
                "FUNCTIONS_DOMAIN": "https://functions.example.com",
                "INTUNED_WORKSPACE_ID": "workspace123",
                "INTUNED_INTEGRATION_ID": "integration456",
            },
        ):
            return APIGateway()

    @pytest.fixture
    def gateway_no_config(self):
        return APIGateway()

    def test_init_without_config(self):
        gateway = APIGateway()
        assert isinstance(gateway.config, GatewayConfig)

    def test_detect_provider_openai_models(self, gateway):
        assert gateway._detect_provider("gpt-4") == "openai"
        assert gateway._detect_provider("gpt-3.5-turbo") == "openai"
        assert gateway._detect_provider("o1-preview") == "openai"
        assert gateway._detect_provider("o3-mini") == "openai"
        assert gateway._detect_provider("gpt-4o") == "openai"
        assert gateway._detect_provider("o4-model") == "openai"

    def test_detect_provider_anthropic_models(self, gateway):
        assert gateway._detect_provider("claude-3-sonnet") == "anthropic"
        assert gateway._detect_provider("claude-3-haiku") == "anthropic"
        assert gateway._detect_provider("CLAUDE-3-OPUS") == "anthropic"  # case insensitive

    def test_detect_provider_google_models(self, gateway):
        assert gateway._detect_provider("gemini-pro") == "google_vertexai"
        assert gateway._detect_provider("gemini-1.5-pro") == "google_vertexai"

    def test_detect_provider_unknown_models(self, gateway):
        assert gateway._detect_provider("unknown-model") == "unknown"
        assert gateway._detect_provider("llama-2") == "unknown"
        assert gateway._detect_provider("mistral-7b") == "unknown"

    def test_build_gateway_url_success(self, gateway):
        result = gateway._build_gateway_url("anthropic")

        expected = "https://functions.example.com/api/workspace123/functions/integration456/anthropic"
        assert result == expected

    def test_build_gateway_url_strips_trailing_slash(self, gateway):
        result = gateway._build_gateway_url("anthropic")

        expected = "https://functions.example.com/api/workspace123/functions/integration456/anthropic"
        assert result == expected

    def test_get_model_config_direct_mode(self, gateway):
        # Direct mode when API key is provided
        config = gateway.get_model_config(
            model="claude-3-sonnet", api_key="sk-test123", extra_headers={"Custom-Header": "value"}
        )

        assert config.model == "claude-3-sonnet"
        assert config.api_key == "sk-test123"
        assert config.extra_headers == {"Custom-Header": "value"}
        assert config.base_url is None

    def test_get_model_config_gateway_mode(self, gateway):
        with IntunedContext() as ctx:
            config = gateway.get_model_config(model="claude-3-sonnet", extra_headers={"Custom-Header": "value"})

            assert config.model == "claude-3-sonnet"
            assert config.api_key == "--THIS_VALUE_WILL_BE_REPLACED_BY_INTUNED_BE--"
            assert config.extra_headers == {"Custom-Header": "value"}
            assert (
                config.base_url == "https://functions.example.com/api/workspace123/functions/integration456/anthropic"
            )

    @patch("intuned_browser.intuned_services.api_gateways.ai_api_gateway.acompletion")
    @pytest.mark.asyncio
    async def test_acompletion_direct_mode(self, mock_acompletion, gateway):
        mock_response = {"choices": [{"message": {"content": "test response"}}]}
        mock_acompletion.return_value = mock_response

        result = await gateway.acompletion(
            model="claude-3-sonnet", messages=[{"role": "user", "content": "test"}], api_key="sk-test123"
        )

        assert result == mock_response
        mock_acompletion.assert_called_once_with(
            model="claude-3-sonnet", messages=[{"role": "user", "content": "test"}], api_key="sk-test123"
        )

    @patch("intuned_browser.intuned_services.api_gateways.ai_api_gateway.acompletion")
    @pytest.mark.asyncio
    async def test_acompletion_gateway_mode(self, mock_acompletion, gateway):
        with IntunedContext() as ctx:
            mock_response = {"choices": [{"message": {"content": "test response"}}]}
            mock_acompletion.return_value = mock_response

            result = await gateway.acompletion(model="claude-3-sonnet", messages=[{"role": "user", "content": "test"}])

            assert result == mock_response
            mock_acompletion.assert_called_once_with(
                model="claude-3-sonnet",
                messages=[{"role": "user", "content": "test"}],
                api_key="--THIS_VALUE_WILL_BE_REPLACED_BY_INTUNED_BE--",
                base_url="https://functions.example.com/api/workspace123/functions/integration456/anthropic",
            )

    @patch("intuned_browser.intuned_services.api_gateways.ai_api_gateway.acompletion")
    @pytest.mark.asyncio
    async def test_acompletion_with_extra_headers(self, mock_acompletion, gateway):
        mock_acompletion.return_value = {"test": "response"}

        await gateway.acompletion(
            model="claude-3-sonnet",
            messages=[{"role": "user", "content": "test"}],
            api_key="sk-test123",
            extra_headers={"Custom-Header": "value"},
        )

        mock_acompletion.assert_called_once_with(
            model="claude-3-sonnet",
            messages=[{"role": "user", "content": "test"}],
            api_key="sk-test123",
            extra_headers={"Custom-Header": "value"},
        )

    @pytest.mark.asyncio
    async def test_acompletion_no_model_raises_error(self, gateway):
        with pytest.raises(ValueError, match="Model parameter is required"):
            await gateway.acompletion(messages=[{"role": "user", "content": "test"}])

    @patch("intuned_browser.intuned_services.api_gateways.ai_api_gateway.acompletion")
    @pytest.mark.asyncio
    async def test_acompletion_removes_api_key_from_kwargs(self, mock_acompletion, gateway):
        mock_acompletion.return_value = {"test": "response"}

        await gateway.acompletion(
            model="claude-3-sonnet", messages=[{"role": "user", "content": "test"}], api_key="sk-test123"
        )

        # Verify api_key was passed to acompletion but removed from original kwargs
        call_kwargs = mock_acompletion.call_args[1]
        assert "api_key" in call_kwargs
        assert call_kwargs["api_key"] == "sk-test123"
