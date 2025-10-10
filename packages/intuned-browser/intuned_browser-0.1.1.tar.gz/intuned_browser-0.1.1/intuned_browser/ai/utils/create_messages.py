import base64
from typing import Any

from intuned_browser.ai.types import ImageObject


def create_human_message(str):
    return [{"role": "user", "content": str}]


def create_assistant_message(str):
    return [{"role": "assistant", "content": str}]


def create_system_message(str):
    return [{"role": "system", "content": str}]


def create_image_message(image: ImageObject) -> dict[str, Any]:
    """Create an image message from an ImageObject.

    Args:
        image: ImageObject with image_type and data
    Returns:
        Dictionary with image message format
    """
    base64_encoded_image = base64.b64encode(image["data"]).decode("utf-8")
    # Use the actual image type from the object
    mime_type = f"image/{image['image_type']}"
    return {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_encoded_image}"}}


def get_extraction_images(images: list[ImageObject]) -> list[dict[str, Any]]:
    """
    Returns the images to be used in the extraction process.

    Args:
        images: List of ImageObject with image_type and data
    Returns:
        List of messages containing the images
    """
    image_messages = []
    for image in images:
        image_messages.append(create_image_message(image))
    images_messages_array = [{"role": "user", "content": image_messages}]
    return images_messages_array
