import asyncio
import logging
from typing import Literal
from typing import overload

from playwright.async_api import Page

from intuned_browser.ai.is_page_loaded import is_page_loaded
from intuned_browser.ai.types import SUPPORTED_MODELS
from intuned_browser.helpers.wait_for_network_settled import wait_for_network_settled

_timeout_padding = 3  # seconds§


@overload
async def go_to_url(
    page: Page,
    url: str,
    *,
    timeout_s: int = 30,
    retries: int = 3,
    wait_for_load_state: str = "load",
    throw_on_timeout: bool = True,
    wait_for_load_using_ai: Literal[False] = False,
) -> None:
    """Navigate to URL without AI loading detection."""
    ...


@overload
async def go_to_url(
    page: Page,
    url: str,
    *,
    timeout_s: int = 30,
    retries: int = 3,
    wait_for_load_state: str = "load",
    throw_on_timeout: bool = True,
    wait_for_load_using_ai: Literal[True],
    model: str | None = "gpt-4o-2024-08-06",
    api_key: str | None = None,
) -> None:
    """Navigate to URL with AI loading detection."""
    ...


@wait_for_network_settled()
async def go_to_url(
    page: Page,
    url: str,
    *,
    timeout_s: int = 30,
    retries: int = 3,
    wait_for_load_state: str = "load",
    throw_on_timeout: bool = True,
    wait_for_load_using_ai: bool = False,
    model: SUPPORTED_MODELS = "gpt-4o-2024-08-06",
    api_key: str | None = None,
) -> None:
    for i in range(retries):
        try:
            current_timeout = (timeout_s * (2**i)) * 1000
            try:
                await asyncio.wait_for(
                    page.goto(url, timeout=current_timeout, wait_until=wait_for_load_state),
                    timeout=current_timeout / 1000 + _timeout_padding,
                )
            except asyncio.TimeoutError as e:  # noqa
                raise asyncio.TimeoutError(  # noqa
                    f"Page.goto timed out but did not throw an error. Consider using a proxy.\n"
                    f"(URL: {url}, timeout: {timeout_s * 1000}ms)"
                ) from e
            break
        except (Exception, asyncio.TimeoutError) as e:  # noqa
            await asyncio.sleep(2)
            if i == retries - 1:
                logging.error(f"Failed to open URL: {url}. Error: {e}")
                if throw_on_timeout:
                    raise e
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout_s * 1000)
    except Exception as e:
        logging.error(f"Failed to wait for networkidle on URL: {url}. Error: {e}")

    if not wait_for_load_using_ai:
        return

    # Retry AI page loading check up to 'retries' times
    for i in range(retries):
        is_loaded = False

        try:
            is_loaded = await is_page_loaded(page, model=model, timeout_s=3, api_key=api_key)
            logging.debug(f"is_loaded (attempt {i + 1}/{retries}): {is_loaded}")

            if is_loaded:
                return
        except Exception as e:
            logging.debug(f"Failed to check if page is loaded: {url}. Error: {e}")
            is_loaded = False

        # If this was the last attempt and page still not loaded, throw error
        if i == retries - 1:
            if throw_on_timeout:
                raise ValueError(f"Page never loaded: {url}")
            return

        # Wait before next retry (not needed after last attempt since we return/raise above)
        await asyncio.sleep(5)
