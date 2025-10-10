import mdformat
from playwright.async_api import Locator
from playwright.async_api import Page

from intuned_browser.common.ensure_browser_scripts import ensure_browser_scripts


async def extract_markdown(source: Page | Locator) -> str:
    is_page = isinstance(source, Page)
    page_object = source if is_page else source.page
    await ensure_browser_scripts(page_object)
    if is_page:
        handle = await source.locator("body").element_handle()
    else:
        handle = await source.element_handle()

    md = await source.evaluate("(element) => window.__INTUNED__.convertElementToMarkdown(element)", handle.as_element())

    return mdformat.text(md)
