from typing import Any

from jsonschema import Draft7Validator
from pydantic import ValidationError

from intuned_browser.ai.types.json_schema import ArraySchema
from intuned_browser.ai.types.json_schema import BasicSchema
from intuned_browser.ai.types.json_schema import BooleanSchema
from intuned_browser.ai.types.json_schema import JsonSchema
from intuned_browser.ai.types.json_schema import NumberSchema
from intuned_browser.ai.types.json_schema import ObjectSchema
from intuned_browser.ai.types.json_schema import StringSchema


def validate_schema(data_schema) -> JsonSchema:
    """Parse and validate a dictionary as JsonSchema"""
    if isinstance(
        data_schema,
        (StringSchema | NumberSchema | BooleanSchema | ArraySchema | ObjectSchema | BasicSchema),
    ):
        return data_schema  # Already a pydantic model

    if not isinstance(data_schema, dict):
        raise ValueError("Data schema must be a dictionary or JsonSchema instance.")

    schema_type = data_schema.get("type")

    # validate the typedict using pydantic's model_validate
    try:
        if schema_type == "string":
            return StringSchema.model_validate(data_schema)
        elif schema_type == "number" or schema_type == "integer":
            return NumberSchema.model_validate(data_schema)
        elif schema_type == "boolean":
            return BooleanSchema.model_validate(data_schema)
        elif schema_type == "array":
            return ArraySchema.model_validate(data_schema)
        elif schema_type == "object":
            return ObjectSchema.model_validate(data_schema)
        else:
            raise ValueError(f"Unknown schema type: {schema_type}")

    except ValidationError as e:
        raise ValueError("Invalid schema format") from e


def validate_tool_call_schema(*, instance: Any, schema: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Validate an instance against a JSON schema and collect all validation errors.

    Unlike the standard jsonschema.validate function, this function collects all
    validation errors instead of raising an exception on the first error.

    Args:
        instance: The instance to validate
        schema: The JSON schema to validate against

    Returns:
        A list of validation errors, each containing:
        - path: The JSON path to the invalid property
        - message: The validation error message
        - value: The invalid value
        - schema_path: The path in the schema that was violated
    """
    validator = Draft7Validator(schema)
    errors = []

    for error in validator.iter_errors(instance):
        # Format the path as a string (e.g., "root.items[0].name")
        path_string = ".".join(str(path_part) for path_part in error.path) if error.path else "root"

        # Format the schema path
        schema_path_string = (
            ".".join(str(path_part) for path_part in error.schema_path) if error.schema_path else "schema"
        )

        # Add the error to the list
        errors.append(
            {"path": path_string, "message": error.message, "value": error.instance, "schema_path": schema_path_string}
        )

    return errors


def check_all_types_are_strings(schema: JsonSchema) -> bool:
    """
    Check if all types in the schema are strings.

    Args:
        schema: The schema to check

    Returns:
        True if all types are strings, False otherwise
    """
    if isinstance(schema, StringSchema):
        return True
    elif isinstance(schema, ArraySchema):
        if schema.items is None:
            return True  # No items constraint means it could be strings

        # Handle both single schema and list of schemas
        if isinstance(schema.items, list):
            return all(check_all_types_are_strings(item) for item in schema.items)
        else:
            return check_all_types_are_strings(schema.items)

    elif isinstance(schema, ObjectSchema):
        if schema.properties is None:
            return True  # No properties constraint means it could be strings

        return all(check_all_types_are_strings(prop) for prop in schema.properties.values())

    # For NumberSchema, BooleanSchema, or BasicSchema
    return False
