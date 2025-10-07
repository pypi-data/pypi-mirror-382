from typing import overload
from urllib.parse import quote
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

from playwright.async_api import Locator
from playwright.async_api import Page


@overload
async def resolve_url(
    *,
    url: str,
    base_url: str,
) -> str: ...


@overload
async def resolve_url(
    *,
    url: str,
    page: Page,
) -> str: ...


@overload
async def resolve_url(
    *,
    url: Locator,
) -> str: ...


async def resolve_url(
    *,
    url: str | Locator,
    base_url: str | None = None,
    page: Page | None = None,
) -> str:
    # Handle Locator/ElementHandle case
    if isinstance(url, (Locator)):
        if base_url is not None or page is not None:
            raise ValueError("base_url and page parameters are not needed when url is Locator")

        # Validate it's an anchor element
        element_name = await url.evaluate("(element) => element.tagName")
        if element_name != "A":
            raise ValueError(f"Expected an anchor element, got {element_name}")

        # Extract absolute href (browser automatically resolves relative URLs)
        return await url.evaluate("(element) => element.href")

    # Handle string URL case
    elif isinstance(url, str):
        # Validate that exactly one of base_url or page is provided
        if base_url is not None and page is not None:
            raise ValueError("Cannot provide both 'base_url' and 'page' parameters. Please provide only one.")
        if base_url is None and page is None:
            raise ValueError("Must provide either 'base_url' or 'page' parameter when url is a string.")

        relative_url = url

        # Extract base URL from Page object or use string directly
        if page is not None:
            parsed_url = urlparse(page.url)
            base_url_str = f"{parsed_url.scheme}://{parsed_url.netloc}"
        else:
            base_url_str = base_url

        # Check if the URL is already absolute
        parsed_relative = urlparse(relative_url)
        if parsed_relative.scheme and parsed_relative.netloc:
            return relative_url

        # Join base and relative URLs
        full_url = urljoin(base_url_str, relative_url)

        # Parse the full URL
        parsed_full = urlparse(full_url)

        # Encode the path and query
        encoded_path = quote(parsed_full.path, safe="/%")
        encoded_query = quote(parsed_full.query, safe="=&%")

        # Reconstruct the URL with encoded components
        return urlunparse(
            (
                parsed_full.scheme,
                parsed_full.netloc,
                encoded_path,
                parsed_full.params,
                encoded_query,
                parsed_full.fragment,
            )
        )

    else:
        raise TypeError(f"url must be str, Locator, got {type(url)}")
