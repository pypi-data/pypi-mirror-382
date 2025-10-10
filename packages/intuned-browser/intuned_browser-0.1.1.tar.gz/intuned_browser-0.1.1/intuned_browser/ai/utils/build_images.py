import asyncio
import logging

from playwright.async_api import ElementHandle
from playwright.async_api import Page
from playwright.async_api import ViewportSize

from intuned_browser.ai.types import DataExtractionError
from intuned_browser.ai.types import ImageObject

logger = logging.getLogger(__name__)


async def capture_full_page_images_with_overlap(page: Page, options: dict[str, int] | None = None) -> list[bytes]:
    """
    Capture full page images with overlap between slices

    Args:
        page: Playwright Page object
        options: Dictionary with 'slice_height' and 'overlap' keys

    Returns:
        List of image buffers as bytes
    """
    if options is None:
        options = {
            "overlap": 200,
            "slice_height": 1000,
        }

    # Get total page height
    total_height = await page.evaluate("() => document.body.scrollHeight")

    current_height = 0
    buffers: list[bytes] = []

    while current_height < total_height:
        if len(buffers) > 10:
            logger.info(f"Page height exceeds maximum capture limit, only first {total_height}px will be captured")
            break

        # Set viewport size
        await page.set_viewport_size(ViewportSize(width=1200, height=options["slice_height"]))

        # Scroll to current position with overlap consideration
        scroll_y = current_height - (options["overlap"] if current_height > 0 else 0)
        await page.evaluate(f"() => window.scrollTo(0, {scroll_y})")

        # Wait for content to load
        await asyncio.sleep(0.5)  # equivalent to waitForTimeout(500)

        # Take screenshot
        buffer = await page.screenshot()
        buffers.append(buffer)

        # Move to next slice position
        current_height += options["slice_height"] - options["overlap"]

    return buffers


async def build_images_from_page_or_handle(
    page: Page, search_region_handler: ElementHandle | None = None
) -> DataExtractionError | list[ImageObject]:
    """
    Build images from page or specific element handle

    Args:
        page: Playwright Page object
        search_region_handler: Optional ElementHandle for specific region

    Returns:
        Result object containing either list of image buffers or error
    """
    # Store original viewport size
    original_viewport_size = page.viewport_size

    # Set standard viewport size
    await page.set_viewport_size(ViewportSize(width=1200, height=800))

    try:
        if search_region_handler:
            # Get bounding box of the element
            size = await search_region_handler.bounding_box()

            if not size:
                raise DataExtractionError(
                    "The specified search region is not visible or does not exist.", error_type="element_not_found"
                )

            # Screenshot the specific element
            screenshot = await search_region_handler.screenshot(type="png")
            return [{"image_type": "png", "data": screenshot}]

        # Capture full page images with overlap
        full_page_images = await capture_full_page_images_with_overlap(page)
        return [{"image_type": "png", "data": img} for img in full_page_images]

    finally:
        # Restore original viewport size if it existed
        if original_viewport_size:
            await page.set_viewport_size(
                ViewportSize(width=original_viewport_size["width"], height=original_viewport_size["height"])
            )
