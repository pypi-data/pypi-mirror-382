import logging
from collections.abc import Awaitable
from collections.abc import Callable
from contextvars import copy_context
from typing import TypeGuard

import validators
from playwright.async_api import Download
from playwright.async_api import ElementHandle
from playwright.async_api import Locator
from playwright.async_api import Page
from playwright.async_api import TimeoutError

from intuned_browser.helpers.resolve_url import resolve_url
from intuned_browser.helpers.utils.get_mode import is_generate_code_mode

logger = logging.getLogger(__name__)


async def get_absolute_url(page: Page, url: str) -> str:
    try:
        url_locator = page.locator(f"a[href='{url}']")
        if await url_locator.count() > 0:
            return await url_locator.evaluate("(el) => el.href")
    except Exception:
        pass
    return await resolve_url(url=url, page=page)


async def download_file(
    page: Page,
    trigger: str | Locator | Callable[[Page], None],
    *,
    timeout_s: int = 5,
) -> Download:
    page_to_download_from = page
    should_close_after_download = False
    is_invalid_url = False

    def is_url(trigger) -> TypeGuard[str]:
        return isinstance(trigger, str)

    def is_locator(trigger) -> TypeGuard[Locator | ElementHandle]:
        return isinstance(trigger, (Locator | ElementHandle))

    def is_callable(trigger) -> TypeGuard[Callable[[Page], Awaitable[None]]]:
        return callable(trigger)

    ctx = copy_context()

    def on_new_page(page: Page) -> None:
        """Callback function to handle new page creation."""

        def new_page_logic():
            logger.info(f"Detected new page opened while processing the download with URL: {page.url}")

            def download_handler(download):
                ctx.run(
                    lambda: logger.info(
                        f"Detected download with URL: {download.url} happened inside page with URL: {page.url} Note that this page is not the original page that called the function."
                    )
                )

            page.on("download", download_handler)

        ctx.run(new_page_logic)

    if is_url(trigger):
        page_to_download_from = await page.context.new_page()
        should_close_after_download = True

    logger.info(f"start to download from {trigger}")
    page_to_download_from.context.on("page", on_new_page)

    try:
        async with page_to_download_from.expect_download(timeout=timeout_s * 1000 + 1000) as download_info:
            if is_url(trigger):
                full_url = await get_absolute_url(page=page, url=trigger)
                is_valid = validators.url(full_url)
                if not is_valid:
                    logger.warning(f"Url is not valid, the download might not be triggered correctly. {full_url}")
                    is_invalid_url = True
                try:
                    response = await page_to_download_from.goto(full_url, wait_until="load", timeout=timeout_s * 1000)
                    content_type = response.headers.get("content-type", "")

                    if content_type.startswith("image/"):
                        await page_to_download_from.evaluate(f"""
                            const link = document.createElement('a');
                            link.href = '{full_url}';
                            link.download = '';  // This forces download
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            """)
                except Exception:
                    pass
            if is_locator(trigger):
                await trigger.click()

            if is_callable(trigger):
                await trigger(page)
    except TimeoutError as e:
        if is_url(trigger) and not is_invalid_url:
            # Check if page is a 404 page by looking for common 404 patterns
            not_found_patterns = [
                "404",
                "not found",
                "page not found",
                "page doesn't exist",
                "page does not exist",
                "resource not found",
            ]
            for pattern in not_found_patterns:
                if await page_to_download_from.get_by_text(pattern, exact=False).count() > 0:
                    page_to_download_from.context.remove_listener("page", on_new_page)
                    raise TimeoutError(f"Download timeout for url:{trigger}. Page appears to be a 404 page.") from e
            raise TimeoutError(f"Download timeout for url:{trigger}. Download was never triggered.") from e
        if is_locator(trigger):
            page_to_download_from.context.remove_listener("page", on_new_page)
            raise TimeoutError(f"Download timeout for locator:{trigger}. Download was never triggered.") from e
        if is_callable(trigger):
            page_to_download_from.context.remove_listener("page", on_new_page)
            raise TimeoutError(f"Download timeout for callable:{trigger}. Download was never triggered.") from e
        if is_url(trigger) and is_invalid_url:
            page_to_download_from.context.remove_listener("page", on_new_page)
            raise TimeoutError(f"Url is not valid, the download did not trigger correctly. {trigger}") from e
    finally:
        if should_close_after_download:
            try:
                await page_to_download_from.close()
            except Exception:
                pass

    download = await download_info.value
    if is_generate_code_mode():
        await download.cancel()

    logger.info(f"Downloaded file successfully by {trigger}")
    page_to_download_from.context.remove_listener("page", on_new_page)

    return download
