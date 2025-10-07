import pytest
from runtime import launch_chromium

from intuned_browser import resolve_url


class TestResolveUrl:
    """Tests for the resolve_url function."""

    @pytest.mark.asyncio
    async def test_relative_url_simple_path(self):
        """Test converting a simple relative path with string base URL."""
        result = await resolve_url(url="/path/to/page", base_url="https://mhtml-viewer.com")
        assert result == "https://mhtml-viewer.com/path/to/page"

    @pytest.mark.asyncio
    async def test_relative_url_with_query(self):
        """Test converting relative URL with query parameters."""
        result = await resolve_url(url="/search?q=test&page=1", base_url="https://mhtml-viewer.com")
        assert result == "https://mhtml-viewer.com/search?q=test&page=1"

    @pytest.mark.asyncio
    async def test_relative_url_with_fragment(self):
        """Test converting relative URL with fragment."""
        result = await resolve_url(url="/page#section1", base_url="https://mhtml-viewer.com")
        assert result == "https://mhtml-viewer.com/page#section1"

    @pytest.mark.asyncio
    async def test_relative_url_with_special_characters(self):
        """Test URL encoding of special characters."""
        result = await resolve_url(url="/path with spaces/file.html", base_url="https://mhtml-viewer.com")
        assert result == "https://mhtml-viewer.com/path%20with%20spaces/file.html"

    @pytest.mark.asyncio
    async def test_relative_url_with_encoded_characters(self):
        """Test that already encoded characters are not double-encoded."""
        result = await resolve_url(url="/path%20with%20spaces/file.html", base_url="https://mhtml-viewer.com")
        assert result == "https://mhtml-viewer.com/path%20with%20spaces/file.html"

    @pytest.mark.asyncio
    async def test_already_full_url(self):
        """Test that full URLs are returned unchanged."""
        full_url = "https://other-site.com/path/to/page"
        result = await resolve_url(url=full_url, base_url="https://mhtml-viewer.com")
        assert result == full_url

    @pytest.mark.asyncio
    async def test_relative_url_current_directory(self):
        """Test relative URL starting with dot."""
        result = await resolve_url(url="./page.html", base_url="https://mhtml-viewer.com/folder/")
        assert result == "https://mhtml-viewer.com/folder/page.html"

    @pytest.mark.asyncio
    async def test_relative_url_parent_directory(self):
        """Test relative URL going to parent directory."""
        result = await resolve_url(url="../other/page.html", base_url="https://mhtml-viewer.com/folder/subfolder/")
        assert result == "https://mhtml-viewer.com/folder/other/page.html"

    @pytest.mark.asyncio
    async def test_query_parameter_encoding(self):
        """Test that query parameters are properly encoded."""
        result = await resolve_url(url="/search?q=hello world&filter=a+b", base_url="https://mhtml-viewer.com")
        print("RESULT: ", result)
        assert result == "https://mhtml-viewer.com/search?q=hello%20world&filter=a%2Bb"

    @pytest.mark.asyncio
    async def test_relative_url_with_page_basic(self):
        """Test converting relative URL using Page object as base."""
        async with launch_chromium(headless=True) as (_, page):
            await page.goto("https://google.com")

            result = await resolve_url(url="/new/path", page=page)
            assert result == "https://www.google.com/new/path"

    @pytest.mark.asyncio
    async def test_already_full_url_with_page(self):
        """Test that full URLs are returned unchanged even with Page object."""
        async with launch_chromium(headless=True) as (_, page):
            await page.goto("https://google.com")

            full_url = "https://other-site.com/different/path"
            result = await resolve_url(url=full_url, page=page)
            assert result == full_url

    @pytest.mark.asyncio
    async def test_page_with_query_and_fragment(self):
        """Test using Page object with complex URL structure."""
        async with launch_chromium(headless=True) as (_, page):
            await page.goto("https://www.google.com")

            result = await resolve_url(url="/new/path", page=page)
            # Should use only scheme and netloc from page URL
            assert "https://www.google.com/new/path" in result


class TestGetAnchorHref:
    """Tests for the get_anchor_href function."""

    @pytest.mark.asyncio
    async def test_get_anchor_href_basic(self):
        """Test getting href from a basic anchor element."""
        async with launch_chromium(headless=True) as (_, page):
            # Navigate to a base URL so relative links resolve properly
            await page.goto("https://www.google.com")
            await page.set_content("""
                <html>
                    <body>
                        <a href="/test/path" id="test-link">Test Link</a>
                    </body>
                </html>
            """)

            locator = page.locator("#test-link")
            result = await resolve_url(url=locator)
            assert "https://www.google.com/test/path" in result

    @pytest.mark.asyncio
    async def test_get_anchor_href_full_url(self):
        """Test getting href from anchor with full URL."""
        async with launch_chromium(headless=True) as (_, page):
            await page.set_content("""
                <html>
                    <body>
                        <a href="https://other-site.com/page" id="external-link">External Link</a>
                    </body>
                </html>
            """)

            locator = page.locator("#external-link")
            result = await resolve_url(url=locator)
            assert result == "https://other-site.com/page"

    @pytest.mark.asyncio
    async def test_get_anchor_href_with_query_and_fragment(self):
        """Test getting href from anchor with query parameters and fragment."""
        async with launch_chromium(headless=True) as (_, page):
            await page.goto("https://google.com")
            await page.set_content("""
                <html>
                    <body>
                        <a href="/search?q=test&page=1#results" id="complex-link">Search Link</a>
                    </body>
                </html>
            """)

            locator = page.locator("#complex-link")
            result = await resolve_url(url=locator)
            assert "https://www.google.com/search?q=test&page=1#results" in result

    @pytest.mark.asyncio
    async def test_get_anchor_href_non_anchor_element_error(self):
        """Test that non-anchor elements raise ValueError."""
        async with launch_chromium(headless=True) as (_, page):
            await page.set_content("""
                <html>
                    <body>
                        <div id="not-anchor">Not a link</div>
                    </body>
                </html>
            """)

            locator = page.locator("#not-anchor")

            with pytest.raises(ValueError, match="Expected an anchor element, got DIV"):
                await resolve_url(url=locator)

    @pytest.mark.asyncio
    async def test_get_anchor_href_button_element_error(self):
        """Test that button elements raise ValueError."""
        async with launch_chromium(headless=True) as (_, page):
            await page.set_content("""
                <html>
                    <body>
                        <button id="button-element">Click me</button>
                    </body>
                </html>
            """)

            locator = page.locator("#button-element")

            with pytest.raises(ValueError, match="Expected an anchor element, got BUTTON"):
                await resolve_url(url=locator)

    @pytest.mark.asyncio
    async def test_get_anchor_href_empty_href(self):
        """Test getting href from anchor with empty href attribute."""
        async with launch_chromium(headless=True) as (_, page):
            await page.goto("https://www.google.com")
            await page.set_content("""
                <html>
                    <body>
                        <a href="" id="empty-link">Empty Link</a>
                    </body>
                </html>
            """)

            locator = page.locator("#empty-link")
            result = await resolve_url(url=locator)
            # Empty href should resolve to current page URL
            assert result == "https://www.google.com/"

    @pytest.mark.asyncio
    async def test_get_anchor_href_hash_only(self):
        """Test getting href from anchor with hash-only href."""
        async with launch_chromium(headless=True) as (_, page):
            await page.goto("https://www.google.com")
            await page.set_content("""
                <html>
                    <body>
                        <a href="#section1" id="hash-link">Hash Link</a>
                    </body>
                </html>
            """)

            locator = page.locator("#hash-link")
            result = await resolve_url(url=locator)
            assert result == "https://www.google.com/#section1"
