from typing import Any


def get_extraction_tools(schema_to_be_extracted: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Get the extraction tools for extracting structured data in Anthropic's JSON schema format.

    Args:
        schema_to_be_extracted: The JSON schema for the data to be extracted

    Returns:
        A list of Anthropic tool functions in JSON schema format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "extract_data_from_content",
                "description": "Extract structured data from the provided content according to the JSON schema.",
                "parameters": schema_to_be_extracted,
            },
        },
        {
            "type": "function",
            "function": {
                "name": "no_data_found",
                "description": "Called when no data matching the schema can be found in the content.",
                "input_schema": {"type": "object", "properties": {}},
            },
        },
    ]
