from collections.abc import Sequence
from typing import Any

from litellm import ModelResponse

from intuned_browser.ai.utils import create_human_message
from intuned_browser.ai.utils import create_system_message
from intuned_browser.ai.utils import get_extraction_images


def get_extraction_system_prompt(prompt: str) -> str:
    """
    Returns the system prompt for data extraction.

    Returns:
        str: System prompt for data extraction
    """
    return create_system_message(f"""You are a data analyst whose job is to extract structured data from an HTML page.
    Please ensure that the data is extracted exactly as it appears in the HTML, without any additional formatting or alterations.
    Extract the structured data exactly as it is in the HTML.
    If you don't find a specific field just don't return the field.
    Call `extract_data_from_content` tool with the extracted data as the argument of this tool.
    {prompt}
    """)


def get_extraction_human_prompt(content) -> str:
    """
    Returns the human prompt for data extraction.

    Returns:
        str: Human prompt for data extraction
    """
    return create_human_message(f"""
    I need you to extract structured data from the following content:
    {content}
    """)


def _flatten_array(nested_array):
    """
    Flattens a 2D array (array of arrays) into a 1D array.

    Args:
        nested_array: List of lists to flatten

    Returns:
        List: Flattened 1D list
    """
    return [item for subarray in nested_array for item in subarray]


def create_extraction_messages(
    prompt: str, content: str, images: Sequence[bytes] | None = None
) -> list[dict[str, Any]]:
    if images and len(images) > 0:
        return _flatten_array(
            [
                get_extraction_system_prompt(prompt),
                get_extraction_human_prompt(content),
                get_extraction_images(images),
            ]
        )
    return _flatten_array(
        [
            get_extraction_system_prompt(prompt),
            get_extraction_human_prompt(content),
        ]
    )


def create_reask_messages_for_validation(*, response: ModelResponse, validation_errors: Sequence[str | dict[str, Any]]):
    """
    Creates messages to reask the model after validation errors.

    Args:
        response: The last response from the LLM
        validation_errors: List of validation errors

    Returns:
        A list of messages to add to the conversation
    """
    # Create error message
    error_message = f"The previous extraction had the following validation errors: {validation_errors}"

    # Extract the single tool call from response.tool_calls[0]
    tool_calls = response.choices[0].message.tool_calls
    if not tool_calls:
        # If no tool calls are present, return an error message directly
        return [{"role": "user", "content": f"{error_message} Please re-extract the data using the same tool."}]

    if len(tool_calls) != 1:
        # If there are multiple tool calls, raise an error
        raise ValueError("Expected exactly one tool call in the response.")

    # Get the first (and only) tool call
    tool_call = tool_calls[0]
    tool_id = tool_call.id

    tool_name = tool_call.function.name
    return [
        {
            "role": "tool",
            "tool_call_id": tool_id,
            "content": f"{error_message} Please re-extract the data using the same tool '{tool_name}'.",
        }
    ]
