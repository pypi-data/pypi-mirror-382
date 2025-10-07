import pytest

from intuned_browser.ai.types.json_schema import ArraySchema
from intuned_browser.ai.types.json_schema import BooleanSchema
from intuned_browser.ai.types.json_schema import NumberSchema
from intuned_browser.ai.types.json_schema import ObjectSchema

# Assuming these imports work in your environment
from intuned_browser.ai.types.json_schema import StringSchema
from intuned_browser.ai.utils.validate_schema import check_all_types_are_strings
from intuned_browser.ai.utils.validate_schema import validate_schema
from intuned_browser.ai.utils.validate_schema import validate_tool_call_schema


class TestValidateAndParseSchema:
    def test_returns_existing__models_unchanged(self):
        """Test that existing  schema models are returned as-is"""
        string_schema = StringSchema(type="string")
        result = validate_schema(string_schema)
        assert result is string_schema

        number_schema = NumberSchema(type="number")
        result = validate_schema(number_schema)
        assert result is number_schema

    def test_parses_string_schema_from_dict(self):
        """Test parsing string schema from dictionary"""
        schema_dict = {"type": "string", "description": "A string field"}
        result = validate_schema(schema_dict)
        assert isinstance(result, StringSchema)
        assert result.type == "string"

    def test_parses_number_schema_from_dict(self):
        """Test parsing number schema from dictionary"""
        schema_dict = {"type": "number", "minimum": 0, "maximum": 100}
        result = validate_schema(schema_dict)
        assert isinstance(result, NumberSchema)
        assert result.type == "number"

    def test_parses_integer_schema_from_dict(self):
        """Test parsing integer schema from dictionary"""
        schema_dict = {"type": "integer", "minimum": 1}
        result = validate_schema(schema_dict)
        assert isinstance(result, NumberSchema)
        assert result.type == "integer"

    def test_parses_boolean_schema_from_dict(self):
        """Test parsing boolean schema from dictionary"""
        schema_dict = {"type": "boolean", "description": "A boolean flag"}
        result = validate_schema(schema_dict)
        assert isinstance(result, BooleanSchema)
        assert result.type == "boolean"

    def test_parses_array_schema_from_dict(self):
        """Test parsing array schema from dictionary"""
        schema_dict = {"type": "array", "items": {"type": "string"}}
        result = validate_schema(schema_dict)
        assert isinstance(result, ArraySchema)
        assert result.type == "array"

    def test_parses_object_schema_from_dict(self):
        """Test parsing object schema from dictionary"""
        schema_dict = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "number"}}}
        result = validate_schema(schema_dict)
        assert isinstance(result, ObjectSchema)
        assert result.type == "object"

    def test_falls_back_to_basic_schema_for_unknown_type(self):
        """Test fallback to BasicSchema for unknown types"""
        schema_dict = {"type": "unknown_type", "description": "Unknown"}
        with pytest.raises(ValueError, match="Unknown schema type: unknown_type"):
            validate_schema(schema_dict)

    def test_raises_error_for_non_dict_non_schema_input(self):
        """Test that non-dict, non-schema input raises ValueError"""
        with pytest.raises(ValueError, match="Data schema must be a dictionary or JsonSchema"):
            validate_schema("invalid")

        with pytest.raises(ValueError, match="Data schema must be a dictionary"):
            validate_schema(123)

        with pytest.raises(ValueError, match="Data schema must be a dictionary"):
            validate_schema([])

    def test_raises_error_for_invalid_schema_format(self):
        """Test that invalid schema format that has no type raises ValueError with ValidationError message"""
        invalid_schema = {"description": "describe me"}

        with pytest.raises(ValueError, match="Unknown schema type:"):
            validate_schema(invalid_schema)


class TestValidateToolCallSchema:
    def test_returns_empty_list_for_valid_instance(self):
        """Test that valid instance returns no errors"""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
            "required": ["name"],
        }
        instance = {"name": "John", "age": 30}

        errors = validate_tool_call_schema(instance=instance, schema=schema)
        assert errors == []

    def test_collects_missing_required_field_error(self):
        """Test that missing required field generates error"""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
            "required": ["name", "age"],
        }
        instance = {"name": "John"}

        errors = validate_tool_call_schema(instance=instance, schema=schema)
        assert len(errors) == 1
        assert "age" in errors[0]["message"]
        assert errors[0]["path"] == "root"

    def test_collects_type_mismatch_errors(self):
        """Test that type mismatches generate errors"""
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "number"}}}
        instance = {"name": 123, "age": "not_a_number"}

        errors = validate_tool_call_schema(instance=instance, schema=schema)
        assert len(errors) == 2

        # Check that both errors are present
        error_messages = [error["message"] for error in errors]
        assert any("string" in msg.lower() for msg in error_messages)
        assert any("number" in msg.lower() for msg in error_messages)

    def test_formats_nested_object_paths_correctly(self):
        """Test that nested object paths are formatted correctly"""
        schema = {
            "type": "object",
            "properties": {
                "user": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
            },
        }
        instance = {"user": {}}

        errors = validate_tool_call_schema(instance=instance, schema=schema)
        assert len(errors) == 1
        assert errors[0]["path"] == "user"

    def test_formats_array_paths_correctly(self):
        """Test that array item paths are formatted correctly"""
        schema = {
            "type": "array",
            "items": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
        }
        instance = [{"name": "John"}, {}]

        errors = validate_tool_call_schema(instance=instance, schema=schema)
        assert len(errors) == 1
        assert "1" in errors[0]["path"]  # Should reference the second array item

    def test_includes_error_details(self):
        """Test that error details include all required fields"""
        schema = {"type": "string"}
        instance = 123

        errors = validate_tool_call_schema(instance=instance, schema=schema)
        assert len(errors) == 1

        error = errors[0]
        assert "path" in error
        assert "message" in error
        assert "value" in error
        assert "schema_path" in error
        assert error["value"] == 123

    def test_handles_complex_nested_validation_errors(self):
        """Test handling of multiple nested validation errors"""
        schema = {
            "type": "object",
            "properties": {
                "users": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}, "age": {"type": "number", "minimum": 0}},
                        "required": ["name"],
                    },
                }
            },
        }
        instance = {
            "users": [
                {"name": "John", "age": -5},  # Invalid age
                {"age": 25},  # Missing name
                {"name": 123},  # Invalid name type
            ]
        }

        errors = validate_tool_call_schema(instance=instance, schema=schema)
        assert len(errors) >= 3  # Should have multiple errors

        # Verify we get errors for different types of validation failures
        error_paths = [error["path"] for error in errors]
        assert any("users" in path for path in error_paths)

    def test_root_level_validation_error(self):
        """Test validation error at root level"""
        schema = {"type": "string"}
        instance = {"not": "a_string"}

        errors = validate_tool_call_schema(instance=instance, schema=schema)
        assert len(errors) == 1
        assert errors[0]["path"] == "root"
        assert errors[0]["value"] == {"not": "a_string"}


class TestCheckAllTypesAreStrings:
    def test_returns_true_for_string_schema(self):
        """Test that StringSchema returns True"""
        schema = StringSchema(type="string")
        assert check_all_types_are_strings(schema) is True

    def test_returns_false_for_number_schema(self):
        """Test that NumberSchema returns False"""
        schema = NumberSchema(type="number")
        assert check_all_types_are_strings(schema) is False

    def test_returns_false_for_boolean_schema(self):
        """Test that BooleanSchema returns False"""
        schema = BooleanSchema(type="boolean")
        assert check_all_types_are_strings(schema) is False

    def test_returns_true_for_array_of_strings(self):
        """Test that ArraySchema with string items returns True"""
        string = StringSchema(type="string")
        schema = ArraySchema(type="array", items=StringSchema(type="string"))
        assert check_all_types_are_strings(schema) is True

    def test_returns_false_for_array_with_non_string_items(self):
        """Test that ArraySchema with non-string items returns False"""
        schema = ArraySchema(type="array", items=NumberSchema(type="number"))
        assert check_all_types_are_strings(schema) is False

    def test_returns_true_for_object_with_string_properties(self):
        """Test that ObjectSchema with string properties returns True"""
        schema = ObjectSchema(
            type="object",
            properties={
                "name": StringSchema(type="string"),
                "description": StringSchema(type="string"),
            },
        )
        assert check_all_types_are_strings(schema) is True

    def test_returns_false_for_object_with_non_string_properties(self):
        """Test that ObjectSchema with non-string properties returns False"""
        schema = ObjectSchema(
            type="object",
            properties={"name": StringSchema(type="string"), "age": NumberSchema(type="number")},
        )
        assert check_all_types_are_strings(schema) is False
