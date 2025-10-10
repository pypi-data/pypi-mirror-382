import os
from typing import Any

from litellm import acompletion

from intuned_browser.intuned_services.api_gateways.models import get_model_provider
from intuned_browser.intuned_services.api_gateways.types import GatewayConfig
from intuned_browser.intuned_services.api_gateways.types import ModelConfig


class APIGateway:
    """
    Unified gateway for LLM API calls that handles both direct and gateway routing.
    Works seamlessly with litellm.
    """

    config: GatewayConfig

    def __init__(self):
        self.config = GatewayConfig()
        self._validate_config()

    def _validate_config(self):
        """Validate gateway configuration if gateway mode is intended"""
        # Config is only required if we're using gateway mode
        pass

    def _detect_provider(self, model: str) -> str:
        """Detect the provider from the model name"""
        model_lower = model.lower()
        return get_model_provider(model_lower) or "unknown"

    def _build_gateway_url(self, provider: str) -> str:
        """Build the gateway URL for a specific provider"""
        if not all([self.config.functions_domain, self.config.workspace_id, self.config.project_id]):
            raise ValueError(
                "Gateway configuration is incomplete. "
                "Please provide functions_domain, workspace_id, and integration_id"
            )

        base_domain = str(self.config.functions_domain).rstrip("/")
        return f"{base_domain}/api/" f"{self.config.workspace_id}/functions/" f"{self.config.project_id}/{provider}"

    def get_model_config(
        self, model: str, api_key: str | None = None, extra_headers: dict[str, Any] | None = None
    ) -> ModelConfig:
        """
        Get the configuration for a model, determining whether to use direct or gateway mode.

        Args:
            model: The model identifier (e.g., "claude-3-sonnet-20240229")
            api_key: Optional API key for direct mode
            extra_headers: Optional extra headers

        Returns:
            ModelConfig with appropriate settings for litellm
        """
        provider = self._detect_provider(model)

        if not api_key:
            if provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
            elif provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif provider == "google_vertexai":
                api_key = os.getenv("GOOGLE_API_KEY")

        if api_key:
            return ModelConfig(model=model, api_key=api_key, extra_headers=extra_headers, base_url=None)

        # Gateway mode - build the gateway URL
        base_url = self._build_gateway_url(provider)

        # Direct mode - use the API key directly
        try:
            from runtime.context.context import IntunedContext
            from runtime.env import get_api_key

            extra_headers = extra_headers or {}
            current_context = IntunedContext.current()
            if current_context.functions_token:
                extra_headers["Authorization"] = f"Bearer {current_context.functions_token}"
            intuned_api_key = get_api_key()
            if intuned_api_key:
                extra_headers["x-api-key"] = intuned_api_key

            return ModelConfig(
                model=model,
                api_key=intuned_api_key or "--THIS_VALUE_WILL_BE_REPLACED_BY_INTUNED_BE--",
                extra_headers=extra_headers,
                base_url=base_url,
            )
        except (ImportError, LookupError) as e:
            raise ValueError(
                "API key is required for direct mode. "
                "For gateway mode, ensure you are running in an Intuned environment and using Intuned Runtime SDK."
            ) from e

    async def acompletion(self, **kwargs) -> Any:
        """
        Wrapper around litellm.acompletion that handles gateway routing.

        This method extracts model and api_key from kwargs, determines the routing,
        and calls litellm with the appropriate configuration.
        """
        # Extract key parameters
        model = kwargs.get("model")
        api_key = kwargs.pop("api_key", None)
        extra_headers = kwargs.get("extra_headers", {})

        if not model:
            raise ValueError("Model parameter is required")

        # Get the model configuration
        config = self.get_model_config(model, api_key, extra_headers)

        # Update kwargs with gateway configuration
        kwargs["model"] = config.model
        kwargs["api_key"] = config.api_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
        if config.extra_headers:
            kwargs["extra_headers"] = {
                **extra_headers,
                **config.extra_headers,
            }

        # Call litellm
        return await acompletion(**kwargs)
