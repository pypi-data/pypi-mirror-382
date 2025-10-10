import json
from collections.abc import Mapping
from typing import Any


def remove_none_from_dict(*, dict_obj: dict | list | str | None) -> dict | list | str | None:
    """
    Recursively removes None values and "null" strings from dictionaries and lists.

    Args:
        dict_obj: The object to process, can be a dictionary, list, string, or None

    Returns:
        The processed object with None values and "null" strings removed
    """
    if dict_obj == "null":
        return None

    elif isinstance(dict_obj, dict):
        return {
            key: remove_none_from_dict(dict_obj=value)
            for key, value in dict_obj.items()
            if value is not None and value != "null"
        }
    elif isinstance(dict_obj, list):
        return [remove_none_from_dict(dict_obj=item) for item in dict_obj if item is not None and item != "null"]

    return dict_obj


def safe_json_loads(*, content: str) -> dict[str, Any]:
    """
    Safely parse JSON content, handling common errors.

    Args:
        content: The JSON string to parse

    Returns:
        Parsed JSON as a dictionary
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        # Try to find a valid JSON object in the string
        if "{" in content and "}" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            try:
                return json.loads(content[start:end])
            except:
                pass

        # Try to strip markdown code block syntax
        if "```json" in content:
            try:
                # Extract content between ```json and ```
                start = content.find("```json") + 7
                end = content.find("```", start)
                return json.loads(content[start:end].strip())
            except:
                pass

        # If all attempts fail, raise the original error
        raise e


def format_schema(*, schema_to_be_extracted: Any) -> tuple[Any, bool]:
    """
    Format a schema to be used by the extract_entity_from_content tool.

    Args:
        schema_to_be_extracted: The schema to be formatted

    Returns:
        The formatted schema
    """
    is_array = schema_to_be_extracted.get("type") == "array"
    formatted_schema: Any = (
        {
            "type": "object",
            "properties": {
                "extracted_data": schema_to_be_extracted,
                "number_of_entities": {
                    "type": "number",
                    "description": "The number of entities items in the text - not the overall total. Relay on the text to find this, if the number is not mentioned in the text, this should be null. For example, some lists say 'showing 5 our of 20 items' - 5 is the number of items in the list.",
                },
            },
            "required": ["extracted_data", "number_of_entities"],
            "additionalProperties": False,
        }
        if is_array
        else schema_to_be_extracted
    )

    return formatted_schema, is_array


def recursively_replace_strings(*, data_structure: Any, replacements: Mapping[str, str | None]) -> Any:
    """
    Recursively replace strings in a nested data structure according to a replacement mapping.

    Args:
        data_structure: The data structure to replace strings in
        replacements: A dictionary mapping original strings to their replacements

    Returns:
        The data structure with strings replaced
    """
    if isinstance(data_structure, str):
        return replacements.get(data_structure, data_structure)
    elif isinstance(data_structure, list):
        return [recursively_replace_strings(data_structure=item, replacements=replacements) for item in data_structure]
    elif isinstance(data_structure, dict):
        return {
            key: recursively_replace_strings(data_structure=value, replacements=replacements)
            for key, value in data_structure.items()
        }
    else:
        return data_structure
