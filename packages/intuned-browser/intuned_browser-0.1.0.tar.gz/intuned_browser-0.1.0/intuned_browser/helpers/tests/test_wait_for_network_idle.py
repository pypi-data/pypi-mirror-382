import asyncio

import pytest
from runtime import launch_chromium

from intuned_browser import wait_for_network_settled


class TestWaitForNetworkIdle:
    @pytest.mark.asyncio
    @pytest.mark.headed
    async def test_with_network_idle_wait_click_element_1(self):
        @wait_for_network_settled(timeout_s=10)
        async def click_element(page, selector, timeout_s=10):
            await page.locator(selector).first.click(timeout=timeout_s * 1000)

        async with launch_chromium(headless=False) as (_, page):
            await page.goto("https://www.txsmartbuy.gov/esbd?")
            await asyncio.sleep(10)
            await click_element(page=page, selector="xpath=(//*[@id='Next'])[1]", timeout_s=10)
            current_page = await page.locator("[aria-label='Current Page']").first.text_content()
            assert current_page == "2"

    @pytest.mark.asyncio
    @pytest.mark.headed
    async def test_with_network_idle_wait_click_element_2(self):
        @wait_for_network_settled(timeout_s=10)
        async def click_element(page, selector, timeout_s=10):
            await page.locator(selector).first.click(timeout=timeout_s * 1000)

        async with launch_chromium(headless=False) as (_, page):
            await page.goto("https://www.biddingo.com/soundtransit", timeout=0)
            await asyncio.sleep(3)
            await click_element(page=page, selector="[aria-label='Next page']", timeout_s=10)
            current_page = await page.locator(".mat-paginator-range-label").first.text_content()
            assert "11" in current_page

    @pytest.mark.asyncio
    @pytest.mark.headed
    async def test_with_network_idle_wait_press_key_combination(self):
        @wait_for_network_settled(timeout_s=10)
        async def press_key_combination(page, key_combination):
            await page.keyboard.press(key_combination)

        async with launch_chromium(headless=False) as (_, page):
            await page.goto("https://www.txsmartbuy.gov/esbd?&page=3")
            await asyncio.sleep(10)
            await page.click("input[name='agencyNumber']")
            await press_key_combination(page=page, key_combination="Enter")
            current_page = await page.locator("[aria-label='Current Page']").first.text_content()
            assert current_page == "1"

    @pytest.mark.asyncio
    @pytest.mark.headed
    async def test_with_network_idle_wait_enter_text_and_click(self):
        @wait_for_network_settled(timeout_s=10)
        async def enter_text_and_click(page, text_selector, click_selector, text):
            await page.fill(text_selector, text)
            await page.click(click_selector)

        async with launch_chromium(headless=False) as (_, page):
            await page.goto("https://www.txsmartbuy.gov/esbd?&page=3", timeout=20000)
            await asyncio.sleep(10)
            await enter_text_and_click(
                page=page,
                text_selector="input[name='agencyNumber']",
                click_selector="#content > div > div > form > div.browse-contract-search-actions [type='submit']",
                text="123456",
            )
            await page.get_by_text("No results found", exact=False).first.text_content()

    @pytest.mark.asyncio
    @pytest.mark.headed
    async def test_wait_for_click_element_3(self):
        @wait_for_network_settled(timeout_s=10)
        async def click_element(page, selector, timeout_s=10):
            await page.locator(selector).first.click(timeout=timeout_s * 1000)

        async with launch_chromium(headless=False) as (_, page):
            await page.goto("https://www.commbuys.com/bso/view/search/external/advancedSearchBid.xhtml")
            await asyncio.sleep(4)
            await click_element(page=page, selector="#bidSearchForm\\:btnBidSearch", timeout_s=10)
            assert await page.locator("[aria-label='Page 1']").first.is_visible()

    @pytest.mark.asyncio
    async def test_with_network_idle_wait_core(self):
        async with launch_chromium(headless=False) as (_, page):
            await page.goto("https://www.commbuys.com/bso/view/search/external/advancedSearchBid.xhtml")
            await wait_for_network_settled(
                page=page,
                func=page.locator("#bidSearchForm\\:btnBidSearch").click,
            )
            assert "commbuys.com" in page.url

    @pytest.mark.asyncio
    @pytest.mark.headed
    async def test_no_page_object_found_in_function_arguments(self):
        async with launch_chromium(headless=False) as (_, page):
            await page.goto("https://mhtml-viewer.com/test-html2")

            # Test with a function that doesn't have a page object
            async def some_function_without_page():
                return "test"

            with pytest.raises(Exception) as exc_info:
                decorated_func = wait_for_network_settled(func=some_function_without_page)
                await decorated_func()
            assert "No Page object found in function arguments" in str(exc_info.value)
