import logging

import pytest
from runtime import launch_chromium

from intuned_browser.helpers.utils import get_simplified_html  # type: ignore


@pytest.mark.asyncio
@pytest.mark.headed12
async def test_basic_html_simplification():
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content("""
        <html>
        <head><title>Basic Test</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a paragraph with some text content.</p>
            <div>
                <span>Nested content</span>
                <ul>
                    <li>List item 1</li>
                    <li>List item 2</li>
                </ul>
            </div>
            <img src="test.jpg" alt="Test image">
        </body>
        </html>
        """)
        await page.wait_for_timeout(1000)

        body_handle = await page.locator("body").element_handle()
        simplified_html = await get_simplified_html(body_handle)

        logging.info(simplified_html)
        assert simplified_html
        assert "<body" in simplified_html


@pytest.mark.asyncio
@pytest.mark.headed
async def test_with_interactive_elements():
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content("""
        <html>
        <body>
            <form>
                <input type="text" name="username" placeholder="Enter username">
                <input type="password" name="password" placeholder="Enter password">
                <textarea name="comments" placeholder="Your comments"></textarea>
                <select name="country">
                    <option value="us">United States</option>
                    <option value="uk">United Kingdom</option>
                </select>
                <button type="submit">Submit</button>
                <button type="button" onclick="alert('clicked')">Click Me</button>
            </form>
            <a href="https://example.com">Link to example</a>
            <div style="cursor: pointer;">Clickable div</div>
            <span onmousedown="console.log('mouse down')">Mouse event span</span>
        </body>
        </html>
        """)
        await page.wait_for_timeout(2000)

        body_handle = await page.locator("body").element_handle()
        simplified_html = await get_simplified_html(body_handle)

        logging.info(simplified_html)
        assert simplified_html
        # Should contain interactive elements like input, button
        assert any(tag in simplified_html.lower() for tag in ["input", "button", "textarea"])


@pytest.mark.asyncio
@pytest.mark.headed
async def test_with_options():
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content("""
        <html>
        <body>
            <div onclick="handleClick()">Clickable content</div>
            <button onclick="submitForm()">Submit Form</button>
            <a href="#" onclick="navigate()">Navigation Link</a>
            <span onmouseup="handleMouse()">Mouse handler</span>
            <div onkeydown="handleKey()">Key handler</div>
            <p>Regular paragraph with lots of text content that should be included as content prop</p>
            <article>
                <h2>Article Title</h2>
                <p>Article content with meaningful text that should be preserved</p>
            </article>
        </body>
        </html>
        """)
        await page.wait_for_timeout(1000)

        body_handle = await page.locator("body").element_handle()
        simplified_html = await get_simplified_html(
            body_handle, options={"should_include_on_click": True, "should_include_content_as_prop": True}
        )

        print(simplified_html)
        assert simplified_html
        assert "<body" in simplified_html
        # Should include onclick attributes when option is enabled
        assert "onclick" in simplified_html
        # Should include content as attribute when option is enabled
        assert "content=" in simplified_html


@pytest.mark.asyncio
@pytest.mark.headed
async def test_invisible_elements_filtered():
    async with launch_chromium(headless=False) as (_, page):
        # Create a page with hidden elements
        await page.set_content("""
        <html>
        <body>
            <div style="display: none;">Hidden div</div>
            <div>Visible div</div>
            <button style="visibility: hidden;">Hidden button</button>
            <button>Visible button</button>
            <span style="opacity: 0;">Invisible span</span>
            <span>Visible span</span>
            <p style="display: block;">Visible paragraph</p>
        </body>
        </html>
        """)

        body_handle = await page.locator("body").element_handle()
        simplified_html = await get_simplified_html(body_handle, options={"keep_only_visible_elements": True})

        logging.info(simplified_html)
        assert "Visible div" in simplified_html or "visible" in simplified_html.lower()
        assert "Hidden div" not in simplified_html
        assert "Hidden button" not in simplified_html
        assert "Invisible span" not in simplified_html


@pytest.mark.asyncio
@pytest.mark.headed
async def test_full_html_element():
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content("""
        <html lang="en">
        <head>
            <title>Full HTML Test</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <header>
                <h1>Website Header</h1>
                <nav>
                    <a href="/">Home</a>
                    <a href="/about">About</a>
                </nav>
            </header>
            <main>
                <section>
                    <h2>Main Section</h2>
                    <p>Main content area</p>
                </section>
            </main>
            <footer>
                <p>&copy; 2024 Test Site</p>
            </footer>
        </body>
        </html>
        """)
        await page.wait_for_timeout(1000)

        html_handle = await page.locator("html").element_handle()
        simplified_html = await get_simplified_html(html_handle)

        logging.info(simplified_html)
        assert simplified_html
        assert simplified_html.startswith("<html")


@pytest.mark.asyncio
@pytest.mark.headed
async def test_allowed_attributes():
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content("""
        <html>
        <body>
            <div aria-label="Main content area" data-testid="main-div" data-custom="value">
                <input type="text" name="search" placeholder="Search..." value="test value">
                <button role="button" title="Submit search">Search</button>
                <a href="https://example.com" id="main-link">External Link</a>
                <img src="test.jpg" alt="Test image" data-src="fallback.jpg">
            </div>
            <form data-form-id="contact">
                <input type="email" name="email" placeholder="Your email">
                <textarea name="message" placeholder="Your message" title="Message field"></textarea>
            </form>
        </body>
        </html>
        """)

        body_handle = await page.locator("body").element_handle()
        simplified_html = await get_simplified_html(body_handle)

        logging.info(simplified_html)
        assert simplified_html
        # Should preserve allowed attributes
        assert "aria-label=" in simplified_html
        assert "data-" in simplified_html
        assert "name=" in simplified_html
        assert "type=" in simplified_html
        assert "placeholder=" in simplified_html
        assert "role=" in simplified_html
        assert "title=" in simplified_html
        assert "href=" in simplified_html
        assert "id=" in simplified_html
        assert "alt=" in simplified_html


@pytest.mark.asyncio
@pytest.mark.headed
async def test_input_with_values():
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content("""
        <html>
        <body>
            <form>
                <input type="text" name="filled" value="has value" style="display: none;">
                <input type="text" name="empty" value="" style="display: none;">
                <input type="hidden" name="hidden" value="hidden value">
                <input type="text" name="visible" value="visible value">
            </form>
        </body>
        </html>
        """)

        body_handle = await page.locator("body").element_handle()
        simplified_html = await get_simplified_html(body_handle)

        logging.info(simplified_html)
        assert simplified_html
        # Should include hidden inputs with values even when keep_only_visible_elements is True
        assert 'value="has value"' in simplified_html or "has value" in simplified_html
        assert 'value="hidden value"' in simplified_html or "hidden value" in simplified_html


@pytest.mark.asyncio
@pytest.mark.headed
async def test_iframe_handling():
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content("""
        <html>
        <body>
            <div>Main content</div>
            <iframe src="about:blank" title="Test iframe">
                <p>Iframe fallback content</p>
            </iframe>
            <div>More content after iframe</div>
        </body>
        </html>
        """)

        # Test without iframe inclusion
        body_handle = await page.locator("body").element_handle()
        simplified_html_no_iframe = await get_simplified_html(body_handle, options={"should_include_iframes": False})

        # Test with iframe inclusion
        simplified_html_with_iframe = await get_simplified_html(body_handle, options={"should_include_iframes": True})

        logging.info("Without iframe: %s", simplified_html_no_iframe)
        logging.info("With iframe: %s", simplified_html_with_iframe)

        assert simplified_html_no_iframe
        assert simplified_html_with_iframe
        assert "Main content" in simplified_html_no_iframe
        assert "Main content" in simplified_html_with_iframe
