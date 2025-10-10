import logging
from typing import Any
from typing import Literal
from typing import overload

from playwright.async_api import Locator
from playwright.async_api import Page

from intuned_browser.ai.extract_structured_data_using_ai import extract_structured_data_using_ai
from intuned_browser.ai.types import ContentItem
from intuned_browser.ai.types import ImageObject
from intuned_browser.ai.types import JsonSchema  # Import TypedDict for autocomplete
from intuned_browser.ai.types import SUPPORTED_MODELS
from intuned_browser.ai.utils import compress_string_spaces
from intuned_browser.ai.utils.build_images import build_images_from_page_or_handle
from intuned_browser.ai.utils.matching.matching import create_xpath_mapping
from intuned_browser.ai.utils.matching.matching import validate_xpath_mapping
from intuned_browser.ai.utils.validate_schema import check_all_types_are_strings
from intuned_browser.ai.utils.validate_schema import validate_schema
from intuned_browser.common.hash_object import hash_object
from intuned_browser.helpers.extract_markdown import extract_markdown
from intuned_browser.helpers.utils.get_simplified_html import get_simplified_html
from intuned_browser.intuned_services import cache

logger = logging.getLogger(__name__)


# Overload for page/locator-based extraction
@overload
async def extract_structured_data(
    source: Page | Locator,
    data_schema: JsonSchema,
    *,
    prompt: str | None = None,
    strategy: Literal["IMAGE", "MARKDOWN", "HTML"] = "HTML",
    model: SUPPORTED_MODELS = "claude-3-5-haiku-latest",
    api_key: str | None = None,
    enable_dom_matching: bool | None = False,
    enable_cache: bool | None = True,
    max_retires: int | None = 3,
) -> Any: ...


# Overload for content-based extraction
@overload
async def extract_structured_data(
    content: list[ContentItem] | ContentItem,
    data_schema: JsonSchema,
    *,
    prompt: str | None = None,
    max_retires: int | None = 3,
    enable_cache: bool | None = True,
    model: SUPPORTED_MODELS = "claude-3-5-haiku-latest",
    api_key: str | None = None,
) -> Any: ...


async def extract_structured_data(
    source: Page | Locator | None = None,
    data_schema: JsonSchema | None = None,
    *,
    content: list[ContentItem] | ContentItem | None = None,
    prompt: str | None = None,
    strategy: Literal["IMAGE", "MARKDOWN", "HTML"] = "HTML",
    enable_dom_matching: bool | None = False,
    enable_cache: bool | None = True,
    max_retires: int | None = 3,
    model: SUPPORTED_MODELS = "claude-3-5-haiku-latest",
    api_key: str | None = None,
) -> Any:
    # Handle content-based extraction
    if content is not None and source is None:
        if data_schema is None:
            raise ValueError("data_schema is required for content-based extraction")
        return await _extract_structured_data_from_content(
            content=content,
            data_schema=data_schema,
            prompt=prompt,
            model=model,
            api_key=api_key,
            max_retires=max_retires,
            enable_cache=enable_cache,
        )

    # Handle page/locator-based extraction
    if source is None or data_schema is None:
        raise ValueError("source and data_schema are required for page/locator-based extraction")

    page_or_locator = source

    # Validate input using pydantic models
    try:
        # Convert TypedDict to Pydantic for validation
        parsed_schema = validate_schema(data_schema)
        if not parsed_schema:
            raise ValueError("Invalid data schema provided.")
    except Exception as e:
        raise ValueError(f"Invalid extract data input: {str(e)}") from e

    page_object = page_or_locator if isinstance(page_or_locator, Page) else page_or_locator.page

    # deny DOM matching if the schema is not valid
    if enable_dom_matching and not check_all_types_are_strings(parsed_schema):
        raise ValueError("For DOM matching, all types of the extraction fields must be STRINGS, to match with the DOM.")

    # We have 3 kind of extractions: image, html and markdown. These 3 strategies will call the same model, the only difference is what we pass to it.
    if strategy == "HTML":
        if not isinstance(page_or_locator, Page):
            container_handle = await page_or_locator.element_handle()
        else:
            container_handle = await page_or_locator.locator("html").element_handle()

        # Get simplified HTML
        simplified_html = await get_simplified_html(container_handle)
        cache_key = None
        # Create cache key
        if enable_cache:
            cache_key = hash_object(
                {
                    "pageUrl": page_object.url,
                    "data_schema": parsed_schema.model_dump()
                    if hasattr(parsed_schema, "model_dump")
                    else parsed_schema,
                    "model": model,
                    "strategy": strategy,
                    "prompt": prompt,
                    "search_region": str(page_or_locator) if isinstance(page_or_locator, Locator) else "",
                    **({"html": compress_string_spaces(simplified_html)} if not enable_dom_matching else {}),
                },
                treat_arrays_as_unsorted_lists=True,
            )

            # Check cache
            cached_result = await cache.get(cache_key)
            if cached_result:
                # dom matching is enabled and the result is cached, check if xpaths still have the matched text
                if enable_dom_matching and isinstance(cached_result, dict) and "matchesMapping" in cached_result:
                    # Validate DOM matches using XPath mapping
                    is_valid = await validate_xpath_mapping(page_object, cached_result["matchesMapping"])
                    if is_valid:
                        logger.info("Returning cached result with valid DOM matching")
                        return cached_result["result"]
                elif not enable_dom_matching:
                    logger.info("Returning cached result")
                    return cached_result

        # Extract using AI
        result = await extract_structured_data_using_ai(
            page=page_object,
            api_key=api_key,
            enable_dom_matching=enable_dom_matching,
            json_schema=data_schema,
            model=model,
            content=simplified_html,
            prompt=prompt,
            images=[],
            max_retries=max_retires,
        )
        if not result:
            raise Exception(result["error"]["context"])

        if enable_cache:
            # Cache result
            if not enable_dom_matching:
                await cache.set(cache_key, result.extracted_data)
            else:
                # Create XPath mapping for DOM validation
                dom_validation_hash = await create_xpath_mapping(page_object, result.extracted_data)
                results_to_cache = {"result": result.extracted_data, "matchesMapping": dom_validation_hash}
                await cache.set(cache_key, results_to_cache)

        return result.extracted_data

    elif strategy == "IMAGE":
        # Get container handle
        container_handle = None
        if isinstance(page_or_locator, Locator):
            container_handle = await page_or_locator.element_handle()

        # Build images
        images = await build_images_from_page_or_handle(page_object, container_handle)

        # Create cache key
        cache_key = hash_object(
            {
                "pageUrl": page_object.url,
                "data_schema": parsed_schema.model_dump() if hasattr(parsed_schema, "model_dump") else parsed_schema,
                "model": model,
                "strategy": strategy,
                "prompt": prompt,
                "search_region": str(page_or_locator) if isinstance(page_or_locator, Locator) else "",
                **({"html": await page_object.locator("html").inner_html()} if not enable_dom_matching else {}),
            },
            treat_arrays_as_unsorted_lists=True,
        )

        # Check cache
        if enable_cache:
            cached_result = await cache.get(cache_key)
            if cached_result:
                if enable_dom_matching and isinstance(cached_result, dict) and "matchesMapping" in cached_result:
                    # Validate DOM matches using XPath mapping
                    is_valid = await validate_xpath_mapping(page_object, cached_result["matchesMapping"])
                    if is_valid:
                        logger.info("Returning cached result with valid DOM matching")
                        return cached_result["result"]
                elif not enable_dom_matching:
                    logger.info("Returning cached result")
                    return cached_result

        # Extract using AI
        result = await extract_structured_data_using_ai(
            page=page_object,
            api_key=api_key,
            enable_dom_matching=enable_dom_matching,
            json_schema=data_schema,
            model=model,
            content="Extract structured data from the following images.",
            prompt=prompt,
            images=images,
            max_retries=max_retires,
        )

        if not result:
            raise Exception(result["error"]["context"])

        # Cache result
        if enable_cache:
            if not enable_dom_matching:
                await cache.set(cache_key, result.extracted_data)
            else:
                # Create XPath mapping for DOM validation
                dom_validation_hash = await create_xpath_mapping(page_object, result.extracted_data)
                results_to_cache = {"result": result.extracted_data, "matchesMapping": dom_validation_hash}
                await cache.set(cache_key, results_to_cache)

        return result.extracted_data

    elif strategy == "MARKDOWN":
        # Get container handle
        container_handle = None
        if isinstance(page_or_locator, Locator):
            container_handle = await page_or_locator.element_handle()
        else:
            container_handle = await page_or_locator.locator("html").element_handle()

        # Get page metadata
        page_title = await page_object.title()
        page_url = page_object.url

        # Convert HTML to markdown
        markdown_content = await extract_markdown(page_object)

        cache_key = hash_object(
            {
                "pageUrl": page_object.url,
                "data_schema": parsed_schema.model_dump() if hasattr(parsed_schema, "model_dump") else parsed_schema,
                "model": model,
                "strategy": strategy,
                "prompt": prompt,
                "search_region": str(page_or_locator) if isinstance(page_or_locator, Locator) else "",
                **(
                    {"html": await page_object.locator("html").inner_html(), "markdown": markdown_content}
                    if not enable_dom_matching
                    else {}
                ),
            },
            treat_arrays_as_unsorted_lists=True,
        )

        # Check cache
        if enable_cache:
            cached_result = await cache.get(cache_key)
            if cached_result:
                if enable_dom_matching and isinstance(cached_result, dict) and "matchesMapping" in cached_result:
                    # Validate DOM matches using XPath mapping
                    is_valid = await validate_xpath_mapping(page_object, cached_result["matchesMapping"])
                    if is_valid:
                        logger.info("Returning cached result with valid DOM matching")
                        return cached_result["result"]
                elif not enable_dom_matching:
                    logger.info("Returning cached result")
                    return cached_result

        # Extract using AI
        result = await extract_structured_data_using_ai(
            page=page_object,
            api_key=api_key,
            enable_dom_matching=enable_dom_matching,
            json_schema=data_schema,
            model=model,
            content=markdown_content,
            prompt=prompt,
            images=[],
            max_retries=max_retires,
        )
        if not result:
            raise Exception(result["error"]["context"])

        # Cache result
        if enable_cache:
            if not enable_dom_matching:
                await cache.set(cache_key, result.extracted_data)
            else:
                # Create XPath mapping for DOM validation
                dom_validation_hash = await create_xpath_mapping(page_object, result.extracted_data)
                results_to_cache = {"result": result.extracted_data, "matchesMapping": dom_validation_hash}
                await cache.set(cache_key, results_to_cache)

        return result.extracted_data


import aiohttp


async def _extract_structured_data_from_content(
    content: list[ContentItem] | ContentItem,
    data_schema: JsonSchema,
    prompt: str | None = None,
    model: SUPPORTED_MODELS = "claude-3-5-haiku-latest",
    api_key: str | None = None,
    max_retires: int | None = 3,
    enable_cache: bool | None = True,
) -> Any:
    # Validate schema
    try:
        parsed_schema = validate_schema(data_schema)
        if not parsed_schema:
            raise ValueError("Invalid data schema provided.")
    except Exception as e:
        raise ValueError(f"Invalid extract data input: {str(e)}") from e

    # Normalize content to list
    content_list = content if isinstance(content, list) else [content]

    # Process images from buffers - create ImageObject format
    images_from_buffers: list[ImageObject] = [
        {
            "image_type": item["image_type"],
            "data": item["data"],
        }
        for item in content_list
        if item["type"] == "image-buffer"
    ]

    # Process images from URLs - create ImageObject format
    images_from_urls: list[ImageObject] = []
    for item in content_list:
        if item["type"] == "image-url":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(item["data"], ssl=False) as response:
                        if response.status == 200:
                            buffer = await response.read()
                            images_from_urls.append(
                                {
                                    "image_type": item["image_type"],
                                    "data": buffer,
                                }
                            )
                        else:
                            raise Exception(f"HTTP {response.status}")
            except Exception as e:
                raise ValueError(f"Fetching image from URL {item['data']} failed: {e}") from e

    # Combine all images as list[ImageObject]
    images = images_from_urls + images_from_buffers

    # Extract text content
    texts = [item["data"] for item in content_list if item["type"] == "text"]

    # Create cache key if caching is enabled
    cache_key = None
    if enable_cache:
        cache_key = hash_object(
            {
                "system_message": prompt,
                "images": [{"image_type": img["image_type"], "data": img["data"].hex()} for img in images],
                "json_schema": parsed_schema.model_dump() if hasattr(parsed_schema, "model_dump") else parsed_schema,
                "model": model,
                "text": texts,
            },
            treat_arrays_as_unsorted_lists=False,
        )

        # Check cache
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached result")
            return cached_result

    # Extract using AI
    result = await extract_structured_data_using_ai(
        api_key=api_key,
        enable_dom_matching=False,
        json_schema=data_schema,
        model=model,
        content="\n".join(texts),
        prompt=prompt,
        images=images,
        max_retries=max_retires,
    )

    # Cache result if caching is enabled
    if enable_cache and cache_key:
        await cache.set(cache_key, result.extracted_data)
    if not result.extracted_data:
        logger.warning("No extracted data found, returning None")
    return result.extracted_data
