import logging
from typing import Any

import pytest

from intuned_browser import validate_data_using_schema
from intuned_browser.helpers.types import ValidationError


@pytest.mark.asyncio
async def test_validate_data_using_schema_valid() -> None:
    """Test validation with valid data."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    }

    data: dict[str, Any] = {
        "name": "John Doe",
        "age": 30,
        "extra_field": "allowed",
    }

    validate_data_using_schema(data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_invalid() -> None:
    """Test validation with invalid data (missing required field)."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    }

    invalid_data: dict[str, Any] = {"name": "John Doe"}  # Missing required 'age' field

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Data validation failed" in str(exc_info.value)
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_list() -> None:
    """Test validation with list of valid objects."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        },
    }

    data: list[dict[str, Any]] = [
        {"name": "John Doe", "age": 30, "extra": "field"},
        {"name": "Jane Doe", "age": 25, "other": "value"},
    ]

    validate_data_using_schema(data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_list_invalid() -> None:
    """Test validation with list containing invalid object."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        },
    }

    invalid_data: list[dict[str, Any]] = [
        {"name": "John Doe", "age": 30},
        {"name": "Jane Doe", "age": "25"},  # age should be integer, not string
    ]

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    logging.debug(f"exc_info: {exc_info}")
    assert "Data validation failed" in str(exc_info.value)
    assert exc_info.value.data == invalid_data


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_type() -> None:
    """Test validation with Attachment custom type."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "name": {"type": "string"},
        },
        "required": ["file", "name"],
    }

    # Valid data that matches Attachment structure
    valid_data: dict[str, Any] = {
        "file": {
            "file_name": "documents/report.pdf",
            "bucket": "my-bucket",
            "region": "us-east-1",
            "endpoint": None,
            "suggested_file_name": "Monthly Report.pdf",
            "file_type": "document",
        },
        "name": "Test File Upload",
    }

    validate_data_using_schema(valid_data, schema)


@pytest.mark.asyncio
async def test_validate_data_using_schema_attachment_type_invalid() -> None:
    """Test validation with invalid Attachment data."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file": {"type": "attachment"},
            "name": {"type": "string"},
        },
        "required": ["file", "name"],
    }

    # Invalid data - missing required Attachment fields
    invalid_data: dict[str, Any] = {
        "file": {
            "file_name": "documents/report.pdf",
            # Missing required fields: bucket, region, suggested_file_name
        },
        "name": "Test File Upload",
    }

    with pytest.raises(ValidationError) as exc_info:
        validate_data_using_schema(invalid_data, schema)
    assert "Data validation failed" in str(exc_info.value)
    assert exc_info.value.data == invalid_data
