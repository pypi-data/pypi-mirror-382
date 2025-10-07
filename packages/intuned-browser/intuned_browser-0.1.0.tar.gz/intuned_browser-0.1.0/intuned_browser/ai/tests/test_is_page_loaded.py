import os

import pytest
from dotenv import load_dotenv
from runtime import launch_chromium
from runtime.context.context import IntunedContext

from intuned_browser.ai.is_page_loaded import is_page_loaded

load_dotenv(override=True)


FULLY_LOADED_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fully Loaded Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; }
        .content { margin: 20px 0; }
        .footer { background: #e0e0e0; padding: 20px; }
        .image { width: 200px; height: 150px; background: #ccc; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Welcome to Our Website</h1>
        <nav>
            <a href="#home">Home</a> | 
            <a href="#about">About</a> | 
            <a href="#contact">Contact</a>
        </nav>
    </div>
    <div class="content">
        <h2>Main Content</h2>
        <p>This page is fully loaded with all content visible.</p>
        <div class="image">Image Placeholder</div>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
    </div>
    <div class="footer">
        <p>&copy; 2024 Test Company. All rights reserved.</p>
    </div>
</body>
</html>
"""

LOADING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading Page</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0;
            background: #f5f5f5;
        }
        .loading-container {
            text-align: center;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .loading-text {
            font-size: 18px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="loading-container">
        <div class="spinner"></div>
        <div class="loading-text">Loading, please wait...</div>
    </div>
</body>
</html>
"""

BLANK_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blank Page</title>
    <style>
        body { margin: 0; padding: 0; background: white; }
    </style>
</head>
<body>
    <!-- Completely blank page -->
</body>
</html>
"""

PARTIALLY_LOADED_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Partially Loaded Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .loaded { opacity: 1; }
        .loading { opacity: 0.3; }
        .placeholder { 
            background: #ddd; 
            height: 100px; 
            margin: 10px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        }
    </style>
</head>
<body>
    <h1 class="loaded">Website Header</h1>
    <div class="placeholder loading">Content Loading...</div>
    <div class="placeholder loading">Images Loading...</div>
    <div class="placeholder loading">More Content Loading...</div>
    <p class="loaded">Some content has loaded but other parts are still loading.</p>
</body>
</html>
"""

ERROR_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error Page</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0;
            background: #ffe6e6;
        }
        .error-container {
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .error-code { font-size: 48px; color: #e74c3c; font-weight: bold; }
        .error-message { font-size: 18px; color: #666; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">404</div>
        <div class="error-message">Page Not Found</div>
        <p>The page you are looking for could not be found.</p>
    </div>
</body>
</html>
"""


@pytest.mark.asyncio
@pytest.mark.headed
async def test_detect_fully_loaded_page():
    """Should detect fully loaded page"""
    with IntunedContext() as ctx:
        async with launch_chromium(headless=False) as (_, page):
            await page.set_content(FULLY_LOADED_PAGE)

            # Wait for content to be visible
            await page.wait_for_selector("h1", timeout=5000)
            #  = os.getenv("OPENAI_")
            result = await is_page_loaded(
                page,
                model="gpt-4o-2024-05-13",
                timeout_s=10,
            )

            assert result


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.headed
async def test_detect_loading_page_with_spinner():
    with IntunedContext() as ctx:
        async with launch_chromium(headless=False) as (_, page):
            await page.set_content(LOADING_PAGE)

            # Wait for spinner to be visible
            await page.wait_for_selector(".spinner", timeout=5000)
            #  = os.getenv("OPENAI_")
            result = await is_page_loaded(page, model="gpt-4o-2024-05-13", timeout_s=10)

            assert result is False


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.headed
async def test_detect_blank_page():
    """Should detect blank page"""
    with IntunedContext() as ctx:
        async with launch_chromium(headless=False) as (_, page):
            await page.set_content(BLANK_PAGE)

            result = await is_page_loaded(
                page,
                model="gpt-4o-2024-05-13",
                timeout_s=10,
            )

            # Blank page should be detected as not loaded or unknown
            assert result is False


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.headed
async def test_handle_partially_loaded_page():
    """Should handle partially loaded page"""

    with IntunedContext() as ctx:
        async with launch_chromium(headless=False) as (_, page):
            await page.set_content(PARTIALLY_LOADED_PAGE)

            # Wait for some content to be visible
            await page.wait_for_selector("h1", timeout=5000)
            #  = os.getenv("OPENAI_")
            result = await is_page_loaded(
                page, model="gpt-4o-2024-05-13", timeout_s=10, api_key=os.environ.get("OPENAI_API_KEY")
            )

            # Could be any response depending on how AI interprets it
            assert result is False


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.headed
async def test_handle_error_page():
    """Should handle error page"""
    with IntunedContext() as ctx:
        async with launch_chromium(headless=False) as (_, page):
            await page.set_content(ERROR_PAGE)

            # Wait for error content to be visible
            await page.wait_for_selector(".error-code", timeout=5000)
            #  = os.getenv("OPENAI_")
            result = await is_page_loaded(
                page,
                model="gpt-4o-2024-05-13",
                timeout_s=10,
            )

            # Error page is loaded (even though it shows an error)
            assert result


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.headed
async def test_works_with_claude_model():
    """Should work with claude-3-5-sonnet-20240620"""
    with IntunedContext() as ctx:
        async with launch_chromium(headless=False) as (_, page):
            await page.set_content(FULLY_LOADED_PAGE)

            result = await is_page_loaded(
                page, model="claude-3-5-sonnet-20240620", api_key=os.environ.get("ANTHROPIC_API_KEY")
            )

            assert result
