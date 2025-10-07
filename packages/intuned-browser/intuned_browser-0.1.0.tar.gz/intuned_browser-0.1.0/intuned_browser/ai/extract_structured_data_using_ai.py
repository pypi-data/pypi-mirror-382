import json
import logging

import litellm
from jsonschema import ValidationError
from playwright.async_api import Page

# Optional import with warning
try:
    from runtime.context.context import IntunedContext
except ImportError:
    IntunedContext = None
    logging.warning("IntunedContext is not available. Some tracking features will be disabled.")

from intuned_browser.ai.prompts.extract_structured_data_prompt import create_extraction_messages
from intuned_browser.ai.prompts.extract_structured_data_prompt import create_reask_messages_for_validation
from intuned_browser.ai.tools.extraction_tools import get_extraction_tools
from intuned_browser.ai.types import ExtractDataOutput
from intuned_browser.ai.types import ImageObject
from intuned_browser.ai.types import JsonSchema
from intuned_browser.ai.types.models import SUPPORTED_MODELS
from intuned_browser.ai.utils.collect_strings import collect_strings
from intuned_browser.ai.utils.matching.matching import replace_with_best_matches
from intuned_browser.ai.utils.safe_json_loads import format_schema
from intuned_browser.ai.utils.safe_json_loads import recursively_replace_strings
from intuned_browser.ai.utils.safe_json_loads import remove_none_from_dict
from intuned_browser.ai.utils.safe_json_loads import safe_json_loads
from intuned_browser.ai.utils.validate_schema import validate_tool_call_schema
from intuned_browser.common.get_ai_tracking_headers import get_ai_tracking_headers
from intuned_browser.common.get_environment_variable import get_environment_variable
from intuned_browser.intuned_services.api_gateways import GatewayFactory

logger = logging.getLogger(__name__)

litellm.set_verbose = False
litellm.return_response_headers = True


async def _extract_data_from_page(
    *,
    model: SUPPORTED_MODELS,
    schema_to_be_extracted: JsonSchema,
    prompt: str = "",
    content: str = "",
    images: list[ImageObject] | None = None,
    api_key: str | None = None,
    max_retries: int = 3,
) -> ExtractDataOutput:
    """
    Extract structured data from content using LangChain and the specified model.
    Now uses APIGateway for unified routing.
    """
    # Get the extraction tools
    extraction_tools = get_extraction_tools(schema_to_be_extracted)
    extraction_prompt = create_extraction_messages(prompt, content, images)

    # Initialize message history
    message_history = extraction_prompt.copy()
    try:
        current_context = IntunedContext.current().run_context
    except LookupError:
        current_context = None
    # Get auth headers if using gateway mode

    ai_intuned_headers = get_ai_tracking_headers(
        environment=get_environment_variable("RUN_ENVIRONMENT"),
        job_id=current_context.job_id if current_context else None,
        job_run_id=current_context.job_run_id if current_context else None,
        type="DYNAMIC_LIST",
        run_id=current_context.run_id if current_context else None,
    )

    # Extract data with retries
    is_gateway = False
    extraction_result = None
    remaining_retries = max_retries
    gateway = GatewayFactory.create_ai_gateway()
    accumulated_cost = 0.0
    while remaining_retries > 0:
        try:
            # Use the current message history as messages
            messages = message_history

            # Use the gateway for completion
            response = await gateway.acompletion(
                model=model,
                tools=extraction_tools,
                messages=messages,
                api_key=api_key,
                extra_headers=ai_intuned_headers,
            )

            # Process the tool calls (rest of your existing logic remains the same)

            response_message = response.choices[0].message

            if response._response_headers and response._response_headers.get("x-ai-cost-in-cents"):
                accumulated_cost += float(response._response_headers["x-ai-cost-in-cents"])
                is_gateway = True
            else:
                accumulated_cost += response.usage.total_tokens

            if len(response_message.tool_calls) > 0:
                tool_call = response_message.tool_calls[0]

                if tool_call.function.name == "no_data_found":
                    logger.info("No data found in the content matching the schema")
                    if is_gateway:
                        logger.info(f"AI cost: ${accumulated_cost:.4f}")
                    else:
                        logger.info(f"AI total tokens: ${accumulated_cost:.4f}")
                    return None

                # Extract the data from the tool call
                try:
                    extraction_result = json.loads(tool_call.function.arguments)
                    if not extraction_result:
                        logging.warning("Tool call returned empty arguments")
                        if is_gateway:
                            logger.info(f"AI cost: ${accumulated_cost:.4f}")
                        else:
                            logger.info(f"AI total tokens: ${accumulated_cost:.4f}")
                        return []
                except Exception as json_error:
                    logging.error(f"Error parsing tool call result: {json_error}")
                    logging.debug(f"Tool call args: {tool_call.function.arguments}")
                    raise ValueError(f"Failed to parse tool call result: {json_error}") from json_error
            else:
                # Fallback to parsing the content directly if no tool calls
                try:
                    extraction_result = safe_json_loads(content=response_message.content)
                except Exception as json_error:
                    logging.error(f"Error parsing response content: {json_error}")
                    logging.debug(f"Response content: {response.content}")
                    raise ValueError(f"Failed to parse response content: {json_error}") from json_error

            # Validate the result against the schema
            validation_errors = validate_tool_call_schema(
                instance=remove_none_from_dict(dict_obj=extraction_result),
                schema=schema_to_be_extracted,
            )

            # If there are no validation errors, return the result
            if not validation_errors:
                if is_gateway:
                    logger.info(f"AI cost: ${accumulated_cost:.4f}")
                else:
                    logger.info(f"AI total tokens: ${accumulated_cost:.4f}")
                return extraction_result

            # If there are validation errors, handle them directly
            logger.info(f"Found {len(validation_errors)} validation errors")
            remaining_retries -= 1
            if remaining_retries == 0:
                logging.error(f"Ran out of retries ({max_retries}) due to validation errors")
                if is_gateway:
                    logger.info(f"AI cost: ${accumulated_cost:.4f}")
                else:
                    logger.info(f"AI total tokens: ${accumulated_cost:.4f}")
                raise RuntimeError(f"Ran out of retries ({max_retries}) due to validation errors")

            reask_messages = create_reask_messages_for_validation(
                response=response, validation_errors=validation_errors
            )
            message_history = (
                message_history
                + [{"role": "assistant", "content": response_message.content}]
                + [
                    {
                        "role": "assistant",
                        "tool_calls": response_message.tool_calls,
                    }
                ]
                + reask_messages
            )
            continue

        except ValidationError as validation_error:
            logger.info(f"Extraction failed due to validation errors, retrying: {validation_error}")
            remaining_retries -= 1
            if remaining_retries == 0:
                logging.error(f"Ran out of retries ({max_retries}) due to validation errors")
                if is_gateway:
                    logger.info(f"AI cost: ${accumulated_cost:.4f}")
                else:
                    logger.info(f"AI total tokens: ${accumulated_cost:.4f}")
                raise RuntimeError(f"Ran out of retries ({max_retries})") from validation_error

            # Build a reask message
            if "response" in locals() and response:
                reask_messages = create_reask_messages_for_validation(
                    response=response, validation_errors=[str(validation_error)]
                )
                message_history = extraction_prompt + reask_messages
            else:
                error_message = f"The previous extraction had the following errors: {str(validation_error)}"
                message_history = message_history + [{"role": "user", "content": error_message}]

        except Exception as general_error:
            import traceback

            logging.error(f"Extraction failed with exception: {general_error}")
            logging.error(f"Stack trace: {traceback.format_exc()}")
            if is_gateway:
                logger.info(f"AI cost: ${accumulated_cost:.4f}")
            else:
                logger.info(f"AI total tokens: ${accumulated_cost:.4f}")
            raise general_error

    # If all retries fail, return the last extraction result (may be None)
    return extraction_result


async def extract_structured_data_using_ai(
    *,
    page: Page | None = None,
    api_key: str | None = None,
    enable_dom_matching: bool = False,
    json_schema: JsonSchema,
    model: SUPPORTED_MODELS,
    content: str,
    prompt: str = "",
    images: list[ImageObject] | None = None,
    max_retries: int = 3,
) -> ExtractDataOutput:
    try:
        # Format the schema
        logger.info("Formatting schema")
        formatted_schema, is_array = format_schema(schema_to_be_extracted=json_schema)

        # Extract data
        logger.info(f"Extracting data using model: {model}")
        extraction_result = await _extract_data_from_page(
            api_key=api_key,
            model=model,
            content=content,
            schema_to_be_extracted=formatted_schema,
            prompt=prompt,
            max_retries=max_retries,
            images=images,
        )

        if not extraction_result:
            logger.info("No data found in the page content matching the schema")
            return ExtractDataOutput(extracted_data=extraction_result)
        extraction_data = extraction_result
        if is_array:
            # ignore number of entities
            extraction_data = extraction_data["extracted_data"]  # type: ignore

        # Skip DOM matching if disabled
        if enable_dom_matching or not page:
            return ExtractDataOutput(extracted_data=extraction_data)

        # Match strings with DOM elements for better accuracy
        logger.info("Matching extracted strings with DOM elements")
        strings_to_match = collect_strings(data_structure=extraction_data)

        if not strings_to_match:
            logging.warning("No strings to match with DOM elements")
            return ExtractDataOutput(extracted_data=None)

        replacements = await replace_with_best_matches(strings_to_match=strings_to_match, page_object=page)
        matched_data = recursively_replace_strings(data_structure=extraction_data, replacements=replacements)
        logger.info("Data extraction completed successfully")
        return ExtractDataOutput(extracted_data=matched_data)
    except Exception as e:
        logging.error(f"Error extracting data from page: {str(e)}")
        raise RuntimeError(f"Failed to extract data from page: {str(e)}") from e
