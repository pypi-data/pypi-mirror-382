import pytest

# Optional imports with warning
try:
    from runtime import launch_chromium
except ImportError:
    launch_chromium = None
    import logging

    logging.warning("Runtime dependencies are not available. Some test features will be disabled.")

from intuned_browser.common.ensure_browser_scripts import ensure_browser_scripts


@pytest.mark.asyncio
async def test_ensure_browser_scripts():
    if launch_chromium is None:
        pytest.skip("Runtime dependencies not available")
    async with launch_chromium() as (_, page):
        await ensure_browser_scripts(page)
        assert await page.evaluate("typeof window.__INTUNED__") == "object"
        assert await page.evaluate("typeof window.__INTUNED__") == "object"
