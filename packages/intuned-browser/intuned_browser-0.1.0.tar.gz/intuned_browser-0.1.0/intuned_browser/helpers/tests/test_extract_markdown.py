import pytest
from runtime import launch_chromium

from intuned_browser import extract_markdown


class TestToMarkdown:
    """Tests for the extract_markdown function."""

    @pytest.mark.asyncio
    async def test_locator_conversion(self):
        """Test converting Playwright locator to markdown."""
        async with launch_chromium(headless=True) as (_, page):
            # Create a test page with content
            await page.set_content("""
               <html>
                   <body>
                       <div id="test-content">
                           <h2>Test Header</h2>
                           <p>Test paragraph with <em>italic</em> text.</p>
                       </div>
                   </body>
               </html>
           """)

            locator = page.locator("#test-content")
            result = await extract_markdown(locator)

            assert "## Test Header" in result
            assert "Test paragraph with _italic_ text." in result

    @pytest.mark.asyncio
    async def test_locator_with_nested_elements(self):
        """Test converting locator with nested elements to markdown."""
        async with launch_chromium(headless=True) as (_, page):
            await page.set_content("""
               <html>
                   <body>
                       <article id="article">
                           <header>
                               <h1>Article Title</h1>
                               <p class="meta">By Author Name</p>
                           </header>
                           <section>
                               <p>First paragraph of content.</p>
                               <p>Second paragraph with <code>inline code</code>.</p>
                           </section>
                       </article>
                   </body>
               </html>
           """)

            locator = page.locator("#article")
            result = await extract_markdown(locator)

            assert "# Article Title" in result
            assert "By Author Name" in result
            assert "First paragraph of content." in result
            assert "`inline code`" in result

    @pytest.mark.asyncio
    async def test_convert_page_to_markdown(self):
        """Test converting page to markdown."""
        async with launch_chromium(headless=True) as (_, page):
            await page.set_content("""
               <html>
                   <body>
                       <div id="test-content">
                           <h2>Test Header</h2>
                           <p>Test paragraph with <em>italic</em> text.</p>
                           </div>
                       </body>
                   </html>
               """)

            result = await extract_markdown(page)

            assert "## Test Header" in result
            assert "Test paragraph with _italic_ text." in result
