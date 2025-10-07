def get_model_provider(model_name: str) -> str | None:
    if any(model_name.startswith(pre) for pre in ("gpt-3", "gpt-4", "o1", "o3", "gpt", "o4")):
        return "openai"
    elif model_name.startswith("claude"):
        return "anthropic"
    elif model_name.startswith("gemini"):
        return "google_vertexai"
    else:
        return None
