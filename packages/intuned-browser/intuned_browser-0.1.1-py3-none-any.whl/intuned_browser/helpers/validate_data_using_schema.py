from typing import Any

from pydantic import ValidationError as PydanticValidationError

from intuned_browser.helpers.types import ValidationError
from intuned_browser.helpers.types.converter import JsonSchemaToPydantic


def validate_data_using_schema(input_data: dict[str, Any] | list[dict[str, Any]], schema: dict[str, Any]):
    schema_model = JsonSchemaToPydantic(schema).convert()

    # Handle single object vs list of objects
    if isinstance(input_data, dict):
        # Single object case
        try:
            if schema["type"] == "array":
                # This shouldn't happen for single dict, but handle gracefully
                raise ValidationError("Data validation failed: Expected array but got single object", input_data)
            else:
                schema_model(**input_data)
        except PydanticValidationError as e:
            raise ValidationError(f"Data validation failed: {str(e)}", input_data) from e
    elif isinstance(input_data, list):
        # List of objects case
        try:
            if schema["type"] == "array":
                # Validate the entire array
                schema_model(items=input_data)
            else:
                # Validate each object individually
                for idx, item in enumerate(input_data):
                    if not isinstance(item, dict):
                        raise ValidationError(
                            f"Data validation failed: Each item should be a dictionary, found {type(item).__name__} at index {idx}",
                            input_data,
                        )
                    schema_model(**item)
        except PydanticValidationError as e:
            raise ValidationError(f"Data validation failed: {str(e)}", input_data) from e
    else:
        raise ValidationError(
            f"Data validation failed: Expected dict or list, got {type(input_data).__name__}",
            input_data,
        )
