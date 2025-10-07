from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import create_model
from pydantic import Field

from intuned_browser.helpers.types.custom_type_registry import CustomTypeRegistry


class JsonSchemaToPydantic:
    """Converts JSON Schema to Pydantic models with custom type support."""

    def __init__(self, schema: dict[str, Any], registry: CustomTypeRegistry | None = None):
        self.schema = schema
        if registry:
            self.registry = registry
        else:
            # register intuned types
            self.registry = CustomTypeRegistry()
        self.definitions = self.schema.get("$defs", {})
        self._preprocessed_schema = self._preprocess_schema(self.schema)
        self._model_cache: dict[str, type[BaseModel]] = {}

    def _preprocess_schema(self, node: Any) -> Any:
        """Recursively preprocess schema to resolve custom types and references."""
        if isinstance(node, dict):
            # Handle $ref
            if "$ref" in node:
                ref_path = node["$ref"].split("/")
                if ref_path[0] == "#" and ref_path[1] == "$defs":
                    def_name = ref_path[2]
                    return self._preprocess_schema(self.definitions.get(def_name, {}))

            # Handle custom types
            if "type" in node and isinstance(node["type"], str):
                if self.registry.is_custom_type(node["type"]):
                    # Preserve the entire node, not just the type
                    return node

            # Process other keys recursively
            return {k: self._preprocess_schema(v) for k, v in node.items()}

        elif isinstance(node, list):
            return [self._preprocess_schema(item) for item in node]

        return node

    def convert(self, wrap_arrays: bool = True) -> type[BaseModel]:
        """
        Convert the preprocessed schema to a Pydantic model.

        Args:
            wrap_arrays: If True, wrap root-level arrays in a BaseModel container.
                        This ensures compatibility with functions expecting BaseModel.

        Returns:
            A Pydantic BaseModel class
        """
        result = self._create_model(self._preprocessed_schema, "RootModel")

        # If the result is a list type and wrap_arrays is True, wrap it in a BaseModel
        if wrap_arrays and hasattr(result, "__origin__") and result.__origin__ is list:  # type: ignore
            # Extract description from original schema if available
            description = self._preprocessed_schema.get("description", "Container for array items")

            # Create a wrapper model with a single field containing the list
            fields = {"items": (result, Field(..., description=description))}
            wrapper_model = create_model("ArrayWrapper", __config__=ConfigDict(strict=True), **fields)  # type: ignore

            # Add metadata to indicate this is a wrapped array
            wrapper_model.__wrapped_array__ = True
            wrapper_model.__original_description__ = description

            return wrapper_model

        return result  # type: ignore

    def _create_model(self, schema: dict[str, Any], model_name: str) -> type[BaseModel] | type:
        """Recursively create Pydantic model from preprocessed schema."""
        if "type" in schema and self.registry.is_custom_type(schema["type"]):
            return self.registry.get(schema["type"])  # type: ignore

        if schema.get("type") == "object":
            fields = {}
            required_fields = schema.get("required", [])

            for prop_name, prop_schema in schema.get("properties", {}).items():
                field_type = self._get_field_type(prop_schema, f"{model_name}_{prop_name}")
                is_required = prop_name in required_fields

                # Extract description if present
                description = prop_schema.get("description", None)

                if is_required:
                    fields[prop_name] = (field_type, Field(..., description=description))
                else:
                    optional_type = field_type | None
                    fields[prop_name] = (optional_type, Field(default=None, description=description))

            return create_model(model_name, __config__=ConfigDict(strict=True), **fields)

        # Handle other types (array, primitive)
        return self._get_field_type(schema, model_name)

    def _get_field_type(self, schema: dict[str, Any], name: str) -> Any:
        """Get Python type from JSON Schema type definition."""
        if "type" in schema:
            schema_type = schema["type"]

            if schema_type == "array":
                items_schema = schema.get("items", {})
                item_type = self._create_model(items_schema, f"{name}_Item")
                return list[item_type]

            elif schema_type == "object":
                return self._create_model(schema, name)

            elif self.registry.is_custom_type(schema_type):
                return self.registry.get(schema_type)

            elif schema_type.lower() in {"string", "integer", "number", "boolean", "null"}:
                return {
                    "string": str,
                    "integer": int,
                    "number": float,
                    "boolean": bool,
                    "null": type(None),
                }[schema_type.lower()]

            # 🚨 Raise error for unsupported types
            raise ValueError(f"Unsupported schema type: {schema_type!r} in field {name!r}")

        return Any

    @staticmethod
    def validate_schema(schema: Any) -> tuple[bool, str]:
        """
        Validate the given schema if it can be converted to a Pydantic model.

        Args:
            schema: The schema to validate

        Returns:
            A tuple containing a boolean indicating success and an error message if validation fails
        """
        try:
            JsonSchemaToPydantic(schema).convert()
            return True, ""
        except Exception as e:
            return False, str(e)
