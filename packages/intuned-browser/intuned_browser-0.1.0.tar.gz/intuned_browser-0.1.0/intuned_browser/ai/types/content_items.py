"""Content item types for extract_structured_data content-based extraction."""

from typing import Literal
from typing import Union

from typing_extensions import TypedDict


class TextContentItem(TypedDict):
    """Text content item for content-based extraction.

    Attributes:
        type: The type of the content item, which is always "text".
        data: The text data to extract information from.

    Examples:
        ```python Using Text Content
        from intuned_browser.ai.types import TextContentItem

        text_content: TextContentItem = {
            "type": "text",
            "data": "John Doe, age 30, works as a Software Engineer"
        }
        ```

    Notes:
        - Use this for extracting structured data from plain text.
        - The AI model processes the text directly without preprocessing.
    """

    type: Literal["text"]
    data: str


class ImageBufferContentItem(TypedDict):
    """Image buffer content item for content-based extraction.

    Attributes:
        type: The type of the content item, which is always "image-buffer".
        image_type: The image format - must be one of "png", "jpeg", "gif", or "webp".
        data: The buffer containing the raw image data as bytes.

    Examples:
        ```python Using Image Buffer
        from intuned_browser.ai.types import ImageBufferContentItem

        with open("receipt.png", "rb") as f:
            image_data = f.read()

        image_content: ImageBufferContentItem = {
            "type": "image-buffer",
            "image_type": "png",
            "data": image_data
        }
        ```

    Notes:
        - Use this when you have image data loaded in memory or from local files.
        - Supported formats: PNG, JPEG, GIF, and WebP.
    """

    type: Literal["image-buffer"]
    image_type: Literal["png", "jpeg", "gif", "webp"]
    data: bytes


class ImageUrlContentItem(TypedDict):
    """Image URL content item for content-based extraction.

    Attributes:
        type: The type of the content item, which is always "image-url".
        image_type: The image format - must be one of "png", "jpeg", "gif", or "webp".
        data: The URL pointing to the image resource (must be publicly accessible).

    Examples:
        ```python Using Image URL
        from intuned_browser.ai.types import ImageUrlContentItem

        image_content: ImageUrlContentItem = {
            "type": "image-url",
            "image_type": "jpeg",
            "data": "https://example.com/product-image.jpg"
        }
        ```

    Notes:
        - The SDK automatically fetches the image from the URL.
        - Use this for remote images to avoid manual downloading.
    """

    type: Literal["image-url"]
    image_type: Literal["png", "jpeg", "gif", "webp"]
    data: str


ContentItem = Union[TextContentItem, ImageBufferContentItem, ImageUrlContentItem]
"""
A union type representing content items for AI data extraction from various content types.

Type Information:
    - `TextContentItem`: Content item for text data
    - `ImageBufferContentItem`: Content item for image data stored as bytes buffer
    - `ImageUrlContentItem`: Content item for image data accessible via URL

Examples:
    ```python Using Different Content Types
    from intuned_browser.ai.types import ContentItem

    # Text content
    text: ContentItem = {
        "type": "text",
        "data": "John Doe, age 30"
    }

    # Image buffer content
    with open("image.png", "rb") as f:
        image_buffer: ContentItem = {
            "type": "image-buffer",
            "image_type": "png",
            "data": f.read()
        }

    # Image URL content
    image_url: ContentItem = {
        "type": "image-url",
        "image_type": "jpeg",
        "data": "https://example.com/image.jpg"
    }
    ```

    ```python Multiple Content Items
    from intuned_browser.ai import extract_structured_data

    content_items: list[ContentItem] = [
        {"type": "text", "data": "Product description text"},
        {"type": "image-url", "image_type": "png", "data": "https://example.com/product.png"}
    ]

    result = await extract_structured_data(
        content=content_items,
        model="gpt-4o",
        data_schema={"type": "object", "properties": {"name": {"type": "string"}}}
    )
    ```

Notes:
    - Multiple content items can be passed as a list for comprehensive analysis.
    - Content-based extraction doesn't require web page navigation or DOM access.
"""


class ImageObject(TypedDict):
    """Image object for AI processing.

    Attributes:
        image_type: The image format (e.g., "png", "jpeg", "gif", "webp").
        data: The image data as bytes.
    """

    image_type: Literal["png", "jpeg", "gif", "webp"]
    data: bytes
