import logging
from collections.abc import Callable

from playwright.async_api import Locator
from playwright.async_api import Page

from intuned_browser.helpers.download_file import download_file
from intuned_browser.helpers.types import Attachment
from intuned_browser.helpers.types import S3Configs
from intuned_browser.helpers.upload_file import upload_file_to_s3
from intuned_browser.helpers.utils.get_mode import is_generate_code_mode

logger = logging.getLogger(__name__)


async def save_file_to_s3(
    page: Page,
    trigger: str | Locator | Callable[[Page], None],
    *,
    timeout_s: int = 5,
    configs: S3Configs | None = None,
    file_name_override: str | None = None,
    content_type: str | None = None,
) -> Attachment:
    if not isinstance(page, Page):
        raise ValueError("page must be a playwright Page object")
    download = await download_file(page, trigger, timeout_s=timeout_s)
    if not is_generate_code_mode():
        try:
            from runtime_helpers import extend_timeout

            extend_timeout()
        except ImportError:
            logger.info(
                "Intuned Runtime not available: extend_timeout() was not called. Install 'intuned-runtime' to enable this feature."
            )
    attachment: Attachment = await upload_file_to_s3(
        download, configs=configs, file_name_override=file_name_override, content_type=content_type
    )
    return attachment
