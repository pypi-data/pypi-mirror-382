import pytest
from runtime import launch_chromium

from intuned_browser import wait_for_dom_settled


@pytest.mark.asyncio
@pytest.mark.headed
async def test_dom_settlement_timeout():
    """Test DOM settlement timeout_s handling."""
    async with launch_chromium(headless=False) as (_, page):
        # Create a page with continuous mutations
        await page.goto("data:text/html,<html><body><div id='target'></div></body></html>")

        # Start continuous DOM mutations that stop after 5 seconds
        await page.evaluate("""
            const intervalId = setInterval(() => {
                const target = document.getElementById('target');
                const div = document.createElement('div');
                div.textContent = Date.now();
                target.appendChild(div);

                // Remove old elements to prevent memory issues
                if (target.children.length > 10) {
                    target.removeChild(target.firstChild);
                }
            }, 100);

            // Stop mutations after 5 seconds
            setTimeout(() => {
                clearInterval(intervalId);
            }, 5000);
        """)
        await wait_for_dom_settled(source=page, settle_duration=2, timeout_s=10)


@pytest.mark.asyncio
@pytest.mark.headed
async def test_dom_settlement_with_interaction():
    async with launch_chromium(headless=False) as (_, page):
        await page.goto("https://www.galvestoncountytx.gov/county-offices/purchasing/solicitations-bids")
        await wait_for_dom_settled(source=page, settle_duration=1, timeout_s=5.0)
        loading = await page.get_by_text("Loading...").is_visible()
        assert not loading, "Loading indicator should not be visible after DOM settles."


@pytest.mark.asyncio
@pytest.mark.headed
async def test_should_handle_no_mutation_gracefully():
    async with launch_chromium(headless=False) as (_, page):
        await page.goto("data:text/html,<html><body><div id='target'></div></body></html>")
        await wait_for_dom_settled(source=page, settle_duration=1, timeout_s=5.0)
        print("DOM settled after initial load.")


@pytest.mark.asyncio
@pytest.mark.headed
async def test_dom_settlement_specific_element():
    """Test DOM settlement watching specific element while ignoring others."""
    async with launch_chromium(headless=False) as (_, page):
        # Create page with two separate elements
        await page.goto("""
            data:text/html,
            <html>
                <body>
                    <div id='watched-element'></div>
                    <div id='ignored-element'></div>
                </body>
            </html>
        """)

        # Start mutations on both elements, with watched element stopping after 3 seconds
        await page.evaluate("""
            const watchedElement = document.getElementById('watched-element');
            const ignoredElement = document.getElementById('ignored-element');

            // Start continuous mutations on ignored element (should not affect settlement)
            const ignoredInterval = setInterval(() => {
                const div = document.createElement('div');
                div.textContent = `Ignored: ${Date.now()}`;
                ignoredElement.appendChild(div);

                if (ignoredElement.children.length > 5) {
                    ignoredElement.removeChild(ignoredElement.firstChild);
                }
            }, 50);

            // Start mutations on watched element, then stop after 3 seconds
            const watchedInterval = setInterval(() => {
                const div = document.createElement('div');
                div.textContent = `Watched: ${Date.now()}`;
                watchedElement.appendChild(div);

                if (watchedElement.children.length > 3) {
                    watchedElement.removeChild(watchedElement.firstChild);
                }
            }, 200);

            // Stop mutations on watched element after 3 seconds
            // (ignored element continues mutating)
            setTimeout(() => {
                clearInterval(watchedInterval);
            }, 3000);

            // Clean up ignored interval after test
            setTimeout(() => {
                clearInterval(ignoredInterval);
            }, 15000);
        """)
        await wait_for_dom_settled(
            source=page.locator("#watched-element"),
            settle_duration=1,
            timeout_s=10,
        )


@pytest.mark.asyncio
@pytest.mark.headed
async def test_wait_for_dom_settled_simple_decorator():
    """Test simple decorator usage: @wait_for_dom_settled"""

    @wait_for_dom_settled(settle_duration=3)
    async def click_and_add_content(page):
        await page.evaluate("""
            const button = document.createElement('button');
            button.id = 'test-button';
            button.textContent = 'Click me';
            document.body.appendChild(button);

            button.addEventListener('click', () => {
                const div = document.createElement('div');
                div.textContent = 'Content added!';
                div.id = 'new-content';
                document.body.appendChild(div);
            });
        """)
        await page.wait_for_timeout(3000)
        await page.click("#test-button")

    async with launch_chromium(headless=False) as (_, page):
        await page.goto("data:text/html,<html><body></body></html>")
        await click_and_add_content(page)

        # Verify the content was added and DOM settled
        content = await page.locator("#new-content").text_content()
        assert content == "Content added!"


@pytest.mark.asyncio
@pytest.mark.headed
async def test_wait_for_dom_settled_parameterized_decorator():
    """Test parameterized decorator usage: @wait_for_dom_settled(settle_duration=1.0)"""

    @wait_for_dom_settled(settle_duration=1.0, timeout_s=10)
    async def add_delayed_content(page):
        await page.evaluate("""
            // Add content immediately
            const div1 = document.createElement('div');
            div1.textContent = 'Immediate content';
            div1.id = 'immediate';
            document.body.appendChild(div1);

            // Add more content after a short delay
            setTimeout(() => {
                const div2 = document.createElement('div');
                div2.textContent = 'Delayed content';
                div2.id = 'delayed';
                document.body.appendChild(div2);
            }, 200);
        """)

    async with launch_chromium(headless=False) as (_, page):
        await page.goto("data:text/html,<html><body></body></html>")
        await add_delayed_content(page)

        # Both immediate and delayed content should be present
        immediate = await page.locator("#immediate").text_content()
        delayed = await page.locator("#delayed").text_content()
        assert immediate == "Immediate content"
        assert delayed == "Delayed content"


@pytest.mark.asyncio
@pytest.mark.headed
async def test_wait_for_dom_settled_direct_call_with_source():
    """Test direct async call: await wait_for_dom_settled(source=page, func=my_func)"""

    async def modify_dom():
        await page.evaluate("""
            const div = document.createElement('div');
            div.textContent = 'Direct call content';
            div.id = 'direct-content';
            document.body.appendChild(div);
        """)
        return "function completed"

    async with launch_chromium(headless=False) as (_, page):
        await page.goto("data:text/html,<html><body></body></html>")

        result = await wait_for_dom_settled(source=page, func=modify_dom, settle_duration=0.5, timeout_s=10)

        assert result == "function completed"
        content = await page.locator("#direct-content").text_content()
        assert content == "Direct call content"


@pytest.mark.asyncio
@pytest.mark.headed
async def test_wait_for_dom_settled_bound_method():
    """Test bound method extraction: await wait_for_dom_settled(func=page.locator(...).click)"""
    async with launch_chromium(headless=False) as (_, page):
        await page.goto("data:text/html,<html><body></body></html>")

        # Create a button that adds content when clicked
        await page.evaluate("""
            const button = document.createElement('button');
            button.id = 'bound-test-button';
            button.textContent = 'Bound method test';
            document.body.appendChild(button);

            button.addEventListener('click', () => {
                const div = document.createElement('div');
                div.textContent = 'Bound method worked!';
                div.id = 'bound-content';
                document.body.appendChild(div);
            });
        """)

        # Use bound method - should automatically extract page
        await wait_for_dom_settled(func=page.locator("#bound-test-button").click, settle_duration=0.5)

        content = await page.locator("#bound-content").text_content()
        assert content == "Bound method worked!"


@pytest.mark.asyncio
@pytest.mark.headed
async def test_wait_for_dom_settled_with_locator():
    """Test decorator with locator argument"""

    @wait_for_dom_settled(settle_duration=2)
    async def modify_specific_element(locator):
        await locator.evaluate("""
            element => {
                element.textContent = 'Modified by locator';
                element.style.backgroundColor = 'yellow';
            }
        """)

    async with launch_chromium(headless=False) as (_, page):
        await page.goto("data:text/html,<html><body><div id='target'>Original text</div></body></html>")

        target_locator = page.locator("#target")
        await modify_specific_element(target_locator)

        content = await target_locator.text_content()
        assert content == "Modified by locator"


@pytest.mark.asyncio
@pytest.mark.headed
async def test_wait_for_dom_settled_error_no_page_object():
    """Test error case when no Page or Locator object is found"""

    @wait_for_dom_settled
    async def function_without_page_object(some_string):
        return f"processed: {some_string}"

    async with launch_chromium(headless=False) as (_, page):
        await page.goto("data:text/html,<html><body></body></html>")

        with pytest.raises(ValueError) as exc_info:
            await function_without_page_object("test")

        assert "No Page or Locator object found in function arguments" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.headed
async def test_wait_for_dom_settled_with_page_kwarg():
    """Test decorator when page is passed as keyword argument"""

    @wait_for_dom_settled
    async def add_content_with_kwarg(*, page, content_text):
        await page.evaluate(f"""
            const div = document.createElement('div');
            div.textContent = '{content_text}';
            div.id = 'kwarg-content';
            document.body.appendChild(div);
        """)

    async with launch_chromium(headless=False) as (_, page):
        await page.goto("data:text/html,<html><body></body></html>")

        await add_content_with_kwarg(page=page, content_text="Keyword argument test")

        content = await page.locator("#kwarg-content").text_content()
        assert content == "Keyword argument test"


@pytest.mark.asyncio
@pytest.mark.headed
async def test_wait_for_dom_settled_multiple_dom_changes():
    """Test that DOM settlement waits for multiple rapid changes to complete"""

    @wait_for_dom_settled(settle_duration=0.8)
    async def trigger_multiple_changes(page):
        await page.evaluate("""
            // Create multiple rapid DOM changes
            for (let i = 0; i < 5; i++) {
                setTimeout(() => {
                    const div = document.createElement('div');
                    div.textContent = `Change ${i + 1}`;
                    div.className = 'change-item';
                    document.body.appendChild(div);
                }, i * 100);
            }
        """)

    async with launch_chromium(headless=False) as (_, page):
        await page.goto("data:text/html,<html><body></body></html>")

        await trigger_multiple_changes(page)

        # All 5 changes should be present after DOM settles
        change_items = await page.locator(".change-item").count()
        assert change_items == 5

        # Check that all expected content is there
        for i in range(1, 6):
            content = await page.locator(f".change-item:nth-child({i})").text_content()
            assert content == f"Change {i}"
