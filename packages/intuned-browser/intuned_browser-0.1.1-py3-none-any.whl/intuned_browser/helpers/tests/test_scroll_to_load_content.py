import pytest
from runtime import launch_chromium

from intuned_browser.helpers import scroll_to_load_content

# HTML for testing whole page scrolling with dynamic content loading
scroll_whole_page_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 20px; }
        .item { height: 300px; margin: 10px; background: #ddd; padding: 20px; border: 1px solid #999; }
    </style>
</head>
<body>
    <div id="content">
        <div class="item">Item 1</div>
        <div class="item">Item 2</div>
        <div class="item">Item 3</div>
        <div class="item">Item 4</div>
        <div class="item">Item 5</div>
        <div class="item">Item 6</div>
    </div>
    <script>
        let itemCount = 6;
        let maxItems = 15;
        
        window.addEventListener('scroll', () => {
            if (itemCount >= maxItems) return;
            
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight;
            const clientHeight = document.documentElement.clientHeight;
            
            if (scrollTop + clientHeight >= scrollHeight - 100) {
                itemCount++;
                const newItem = document.createElement('div');
                newItem.className = 'item';
                newItem.textContent = 'Item ' + itemCount;
                document.getElementById('content').appendChild(newItem);
            }
        });
    </script>
</body>
</html>
"""

# HTML for testing container scrolling with dynamic content loading
scroll_specific_container_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 20px; }
        #scrollable-container {
            height: 400px;
            overflow-y: auto;
            border: 2px solid #333;
            padding: 10px;
        }
        .container-item { height: 150px; margin: 10px; background: #aaf; padding: 15px; }
    </style>
</head>
<body>
    <h1>Container Scroll Test</h1>
    <div id="scrollable-container">
        <div class="container-item">Container Item 1</div>
        <div class="container-item">Container Item 2</div>
        <div class="container-item">Container Item 3</div>
    </div>
    <script>
        let containerItemCount = 3;
        let maxContainerItems = 8;
        const container = document.getElementById('scrollable-container');
        
        container.addEventListener('scroll', () => {
            if (containerItemCount >= maxContainerItems) return;
            
            if (container.scrollTop + container.clientHeight >= container.scrollHeight - 50) {
                containerItemCount++;
                const newItem = document.createElement('div');
                newItem.className = 'container-item';
                newItem.textContent = 'Container Item ' + containerItemCount;
                container.appendChild(newItem);
            }
        });
    </script>
</body>
</html>
"""


@pytest.mark.asyncio
async def test_scroll_whole_page_default_params():
    """Test scrolling the whole page with default parameters."""
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content(scroll_whole_page_html)

        # Get initial item count
        initial_count = await page.locator(".item").count()
        assert initial_count == 6

        # Scroll to load content
        await scroll_to_load_content(source=page)

        # Verify more items were loaded
        final_count = await page.locator(".item").count()
        assert final_count > initial_count
        assert final_count <= 15  # Max items defined in HTML


@pytest.mark.asyncio
async def test_scroll_whole_page_with_custom_params():
    """Test scrolling the whole page with custom max_scrolls and progress callback."""
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content(scroll_whole_page_html)

        # Track scroll progress
        scroll_progress_calls = []

        def on_progress():
            scroll_progress_calls.append(1)

        # Scroll with limited max_scrolls
        await scroll_to_load_content(source=page, max_scrolls=3, on_scroll_progress=on_progress, delay_s=0.05)

        # Verify progress callback was called
        assert len(scroll_progress_calls) > 0
        assert len(scroll_progress_calls) <= 3

        # Verify some items were loaded
        final_count = await page.locator(".item").count()
        assert final_count >= 6


@pytest.mark.asyncio
async def test_scroll_container_default_params():
    """Test scrolling a specific container with default parameters."""
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content(scroll_specific_container_html)

        # Get the scrollable container
        container = page.locator("#scrollable-container")

        # Get initial item count
        initial_count = await page.locator(".container-item").count()
        assert initial_count == 3

        # Scroll container to load content
        await scroll_to_load_content(source=container)

        # Verify more items were loaded
        final_count = await page.locator(".container-item").count()
        assert final_count > initial_count
        assert final_count <= 8  # Max items defined in HTML


@pytest.mark.asyncio
async def test_scroll_container_with_custom_params():
    """Test scrolling a container with custom min_height_change and delay."""
    async with launch_chromium(headless=False) as (_, page):
        await page.set_content(scroll_specific_container_html)

        # Get the scrollable container
        container = page.locator("#scrollable-container")

        initial_count = await page.locator(".container-item").count()

        # Scroll with custom parameters
        await scroll_to_load_content(
            source=container,
            min_height_change=50,  # Lower threshold for detecting changes
            delay_s=0.2,  # Longer delay between scrolls
            max_scrolls=10,
        )

        # Verify items were loaded
        final_count = await page.locator(".container-item").count()
        assert final_count > initial_count
