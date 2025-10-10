import os

import pytest
from dotenv import load_dotenv

# Optional imports with warning
try:
    from runtime import launch_chromium
    from runtime.context.context import IntunedContext
    from runtime.context.context import IntunedRunContext
except ImportError:
    launch_chromium = None
    IntunedContext = None
    IntunedRunContext = None
    import logging

    logging.warning("Runtime dependencies are not available. Some test features will be disabled.")

from intuned_browser.ai import extract_structured_data
from intuned_browser.ai.types import ImageUrlContentItem
from intuned_browser.ai.types import TextContentItem

load_dotenv()

# Test HTML templates
PRODUCT_LIST_TEMPLATE = """
<div class="product-list">
  <div class="product" data-id="1">
    <h2 class="title">iPhone 14 Pro</h2>
    <div class="price">$999</div>
    <div class="stock">In Stock</div>
    <div class="rating">4.5</div>
    <ul class="features">
      <li>5G Capable</li>
      <li>A16 Bionic</li>
      <li>48MP Camera</li>
    </ul>
  </div>
  <div class="product" data-id="2">
    <h2 class="title">MacBook Air M2</h2>
    <div class="price">$1199</div>
    <div class="stock">Low Stock</div>
    <div class="rating">4.8</div>
    <ul class="features">
      <li>M2 Chip</li>
      <li>13.6" Display</li>
      <li>18hr Battery</li>
    </ul>
  </div>
  <div class="product" data-id="3">
    <h2 class="title">AirPods Pro</h2>
    <div class="price">$249</div>
    <div class="stock">Out of Stock</div>
    <div class="rating">4.7</div>
    <ul class="features">
      <li>Active Noise Cancellation</li>
      <li>Spatial Audio</li>
      <li>Water Resistant</li>
    </ul>
  </div>
</div>
"""

ARTICLE_TEMPLATE = """
<article class="blog-post">
  <header>
    <h1>The Future of AI in 2024</h1>
    <div class="metadata">
      <span class="author">John Doe</span>
      <time datetime="2024-03-15">March 15, 2024</time>
      <span class="read-time">8 min read</span>
    </div>
    <div class="tags">
      <span class="tag">AI</span>
      <span class="tag">Technology</span>
      <span class="tag">Future</span>
    </div>
  </header>
  <div class="content">
    <p>Artificial Intelligence has seen remarkable growth in recent years...</p>
    <h2>Key Developments</h2>
    <ul>
      <li>Advanced Language Models</li>
      <li>Computer Vision Breakthroughs</li>
      <li>Ethical AI Guidelines</li>
    </ul>
    <p>These advancements are reshaping industries...</p>
  </div>
  <footer>
    <div class="engagement">
      <span class="likes">1.2k likes</span>
      <span class="comments">83 comments</span>
      <span class="shares">456 shares</span>
    </div>
  </footer>
</article>
"""

USER_PROFILE_TEMPLATE = """
<div class="user-profile">
  <div class="profile-header">
    <img src="https://example.com/avatar.jpg" alt="User Avatar" class="avatar" />
    <h1 class="name">Sarah Wilson</h1>
    <div class="status">Premium Member</div>
  </div>
  <div class="profile-stats">
    <div class="stat">
      <span class="value">1,234</span>
      <span class="label">Followers</span>
    </div>
    <div class="stat">
      <span class="value">567</span>
      <span class="label">Following</span>
    </div>
    <div class="stat">
      <span class="value">89</span>
      <span class="label">Posts</span>
    </div>
  </div>
  <div class="profile-details">
    <div class="location">📍 San Francisco, CA</div>
    <div class="bio">Tech enthusiast & photographer 📱 📸</div>
    <div class="joined-date">Joined: January 2020</div>
  </div>
  <div class="badges">
    <span class="badge">🏆 Top Contributor</span>
    <span class="badge">✨ Trending Creator</span>
    <span class="badge">🎯 Pro User</span>
  </div>
</div>
"""


class TestExtractStructuredData:
    """Tests for extract_structured_data functionality"""

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_html_strategy(self):
        """Test extracting product list using HTML strategy"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                try:
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                except:
                    await page.reload()
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                data = await extract_structured_data(
                    source=page,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema={
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Product name"},
                                "price": {"type": "string", "description": "Product price"},
                                "stock": {"type": "string", "description": "Stock status"},
                                "rating": {"type": "string", "description": "Product rating"},
                            },
                            "required": ["title", "price", "stock"],
                        },
                    },
                    prompt="please Extract product information including title, price, stock status, and rating... .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=False,
                )

                assert isinstance(data, list)
                assert len(data) == 3
                assert data[0]["title"] == "iPhone 14 Pro"
                assert data[0]["price"] == "$999"
                assert data[0]["stock"] == "In Stock"

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_markdown_strategy(self):
        """Test extracting article data using MARKDOWN strategy"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                try:
                    await page.set_content(ARTICLE_TEMPLATE)
                except:
                    await page.reload()
                    await page.set_content(ARTICLE_TEMPLATE)
                data = await extract_structured_data(
                    source=page,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Article title"},
                            "author": {"type": "string", "description": "Author name"},
                            "date": {"type": "string", "description": "Publication date"},
                            "readTime": {"type": "string", "description": "Reading time"},
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Article tags",
                            },
                        },
                        "required": ["title", "author", "tags"],
                    },
                    prompt="please Extract article metadata including title, author, date, read time, and tags. .",
                    strategy="MARKDOWN",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=False,
                )

                assert data["title"] == "The Future of AI in 2024"
                assert data["author"] == "John Doe"
                assert "AI" in data["tags"]
                assert "Technology" in data["tags"]

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_image_strategy(self):
        """Test extracting user profile using IMAGE strategy"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                try:
                    await page.set_content(USER_PROFILE_TEMPLATE)
                except Exception:
                    await page.reload()
                data = await extract_structured_data(
                    source=page,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "User's name"},
                            "status": {"type": "string", "description": "Membership status"},
                            "followers": {"type": "string", "description": "Number of followers"},
                            "following": {"type": "string", "description": "Number of following"},
                            "location": {"type": "string", "description": "User's location"},
                            "badges": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "User's badges",
                            },
                        },
                        "required": ["name", "status", "location"],
                    },
                    prompt="please Extract user profile information including name, status, follower counts, location, and badges. .",
                    strategy="IMAGE",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=False,
                )

                assert data["name"] == "Sarah Wilson"
                assert data["status"] == "Premium Member"
                assert data["location"] == "San Francisco, CA"
                assert len(data["badges"]) == 3

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_array_of_strings(self):
        """Test extracting array of strings"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                try:
                    await page.set_content(ARTICLE_TEMPLATE)
                except:
                    await page.reload()
                    await page.set_content(ARTICLE_TEMPLATE)
                data = await extract_structured_data(
                    source=page,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema={
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of article tags",
                        "minItems": 2,
                        "maxItems": 5,
                        "uniqueItems": True,
                    },
                    prompt="Extract all unique tags from the article. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=False,
                )

                assert isinstance(data, list)
                assert len(data) >= 2
                assert len(data) <= 5
                assert len(set(data)) == len(data)  # Check uniqueness
                assert "AI" in data
                assert "Technology" in data

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_array_of_objects(self):
        """Test extracting array of objects"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                try:
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                except:
                    await page.reload()
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                data = await extract_structured_data(
                    source=page,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema={
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "features": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["title", "features"],
                        },
                        "minItems": 1,
                    },
                    prompt="Extract each product's title and list of features. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=False,
                )

                assert isinstance(data, list)
                assert data[0]["title"] == "iPhone 14 Pro"
                assert isinstance(data[0]["features"], list)
                assert "5G Capable" in data[0]["features"]

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_nested_object_with_mixed_types(self):
        """Test extracting nested object with mixed types"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                await page.set_content(USER_PROFILE_TEMPLATE)
                data = await extract_structured_data(
                    source=page,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema={
                        "type": "object",
                        "properties": {
                            "user": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "status": {"type": "string"},
                                },
                                "required": ["name", "status"],
                            },
                            "stats": {
                                "type": "object",
                                "properties": {
                                    "followers": {"type": "string"},
                                    "following": {"type": "string"},
                                    "posts": {"type": "string"},
                                },
                                "required": ["followers", "following", "posts"],
                            },
                            "badges": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["user", "stats"],
                    },
                    prompt="Extract user profile information with nested stats. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=False,
                )

                assert data["user"]["name"] == "Sarah Wilson"
                assert data["user"]["status"] == "Premium Member"
                assert data["stats"]["followers"] == "1,234"
                assert isinstance(data["badges"], list)

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_object_with_string_constraints(self):
        """Test extracting object with string constraints"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                try:
                    await page.set_content(ARTICLE_TEMPLATE)
                except:
                    await page.reload()
                    await page.set_content(ARTICLE_TEMPLATE)
                data = await extract_structured_data(
                    source=page,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "minLength": 10,
                                "maxLength": 100,
                            },
                            "author": {
                                "type": "string",
                                "pattern": "^[A-Za-z ]+$",
                            },
                            "readTime": {
                                "type": "string",
                                "pattern": "^\\d+ min read$",
                            },
                        },
                        "required": ["title", "author", "readTime"],
                    },
                    prompt="Extract article metadata with specific string formats. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=False,
                )

                assert 10 <= len(data["title"]) <= 100
                assert data["author"].replace(" ", "").isalpha()
                assert data["readTime"].endswith("min read")
                assert data["readTime"].split()[0].isdigit()

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_dom_matching_fails_with_non_string_types(self):
        """Test that DOM matching fails when using non-string types"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                try:
                    await page.set_content(USER_PROFILE_TEMPLATE)
                except:
                    await page.reload()
                    await page.set_content(USER_PROFILE_TEMPLATE)
                with pytest.raises(
                    ValueError, match="For DOM matching, all types of the extraction fields must be STRINGS"
                ):
                    await extract_structured_data(
                        source=page,
                        api_key=os.getenv("ANTHROPIC_API_KEY"),
                        data_schema={
                            "type": "object",
                            "properties": {
                                "followers": {"type": "number"},
                                "following": {"type": "number"},
                            },
                            "required": ["followers", "following"],
                        },
                        prompt="Extract follower counts. .",
                        strategy="HTML",
                        model="claude-3-5-sonnet-20240620",
                        enable_dom_matching=True,
                    )

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_non_string_types_work_with_dom_matching_disabled(self):
        """Test that non-string types work when DOM matching is disabled"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                try:
                    await page.set_content(USER_PROFILE_TEMPLATE)
                except Exception:
                    await page.reload()
                data = await extract_structured_data(
                    source=page,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema={
                        "type": "object",
                        "properties": {
                            "followers": {"type": "number"},
                            "following": {"type": "number"},
                        },
                        "required": ["followers", "following"],
                    },
                    prompt="Extract follower counts as numbers. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=False,
                )

                assert isinstance(data["followers"], int | float)
                assert isinstance(data["following"], int | float)

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_caching_with_dom_matching(self):
        """Test caching behavior with DOM matching enabled"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                try:
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                except:
                    await page.reload()
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                schema = {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "price": {"type": "string"},
                    },
                    "required": ["title", "price"],
                }

                # First extraction
                first_result = await extract_structured_data(
                    source=page.locator(".product").first,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema=schema,
                    prompt="Extract product title and price. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=True,
                )

                # Second extraction with same content
                second_result = await extract_structured_data(
                    source=page.locator(".product").first,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema=schema,
                    prompt="Extract product title and price. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=True,
                )

                assert second_result == first_result

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_cache_invalidation_on_dom_changes(self):
        """Test that cache is invalidated when DOM changes"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                schema = {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "price": {"type": "string"},
                    },
                    "required": ["title", "price"],
                }

                # First extraction
                try:
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                except:
                    await page.reload()
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                first_result = await extract_structured_data(
                    source=page.locator(".product").first,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema=schema,
                    prompt="Extract product title and price. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=True,
                )

                # Change content and extract again
                modified_template = PRODUCT_LIST_TEMPLATE.replace("iPhone 14 Pro", "iPhone 15 Pro").replace(
                    "$999", "$1099"
                )
                await page.set_content(modified_template)

                second_result = await extract_structured_data(
                    source=page.locator(".product").first,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema=schema,
                    prompt="Extract product title and price. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=True,
                )

                assert second_result != first_result
                assert second_result["title"] == "iPhone 15 Pro"
                assert second_result["price"] == "$1099"

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_caching_without_dom_matching(self):
        """Test caching behavior when DOM matching is disabled"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                schema = {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "price": {"type": "string"},
                    },
                    "required": ["title", "price"],
                }

                # First extraction
                try:
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                except:
                    await page.reload()
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                first_result = await extract_structured_data(
                    source=page.locator(".product").first,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema=schema,
                    prompt="Extract product title and price. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=False,
                )

                # Change content but should still get cached result
                modified_template = PRODUCT_LIST_TEMPLATE.replace("iPhone 14 Pro", "iPhone 15 Pro").replace(
                    "$999", "$1099"
                )
                await page.set_content(modified_template)

                second_result = await extract_structured_data(
                    source=page.locator(".product").first,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema=schema,
                    prompt="Extract product title and price. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=False,
                )

                assert second_result != first_result
                assert second_result["title"] == "iPhone 15 Pro"
                assert second_result["price"] == "$1099"

    @pytest.mark.asyncio
    async def test_cache_with_dom_changes(self):
        """Test that cache is invalidated when DOM changes"""
        if IntunedContext is None or launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            async with launch_chromium(headless=False) as (_, page):
                schema = {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "price": {"type": "string"},
                    },
                    "required": ["title", "price"],
                }

                # First extraction
                try:
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                except:
                    await page.reload()
                    await page.set_content(PRODUCT_LIST_TEMPLATE)
                first_result = await extract_structured_data(
                    source=page.locator(".product").first,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema=schema,
                    prompt="Extract product title and price.. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=True,
                )

                # Change content and extract again
                modified_template = PRODUCT_LIST_TEMPLATE.replace("Water Resistant", "NON RELEVANT DOM")
                await page.set_content(modified_template)

                second_result = await extract_structured_data(
                    source=page.locator(".product").first,
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    data_schema=schema,
                    prompt="Extract product title and price.. .",
                    strategy="HTML",
                    model="claude-3-5-sonnet-20240620",
                    enable_dom_matching=True,
                )

                assert second_result == first_result
                assert second_result["title"] == "iPhone 14 Pro"
                assert second_result["price"] == "$999"


class TestExtractFromContent:
    """Tests for extract_structured_data content-based functionality"""

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_extract_from_single_text_content(self):
        """Test extracting structured data from single text content"""
        text_content: TextContentItem = {
            "type": "text",
            "data": "John Doe, age 30, works as a Software Engineer at Tech Corp. His email is john.doe@techcorp.com and phone number is +1-555-0123.",
        }

        person_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person's full name"},
                "age": {"type": "number", "description": "Person's age"},
                "occupation": {"type": "string", "description": "Person's job title"},
                "company": {"type": "string", "description": "Company name"},
                "email": {"type": "string", "description": "Email address"},
                "phone": {"type": "string", "description": "Phone number"},
            },
            "required": ["name"],
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            result = await extract_structured_data(
                content=text_content,
                model="gpt-4o",
                data_schema=person_schema,
                prompt="Extract person information from the text. .",
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        assert result is not None
        assert result["name"] == "John Doe"
        assert result["age"] == 30
        assert "Software Engineer" in result["occupation"]
        assert "Tech Corp" in result["company"]
        assert result["email"] == "john.doe@techcorp.com"
        assert "555-0123" in result["phone"]

    @pytest.mark.asyncio
    # @pytest.mark.skip
    async def test_extract_array_data_from_text_content(self):
        """Test extracting array data from text content"""
        text_content: TextContentItem = {
            "type": "text",
            "data": """
                Product List:
                1. iPhone 15 - $999 - Apple
                2. Samsung Galaxy S24 - $899 - Samsung
                3. Google Pixel 8 - $699 - Google
            """,
        }

        products_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Product name"},
                    "price": {"type": "string", "description": "Product price"},
                    "brand": {"type": "string", "description": "Product brand"},
                },
                "required": ["name", "price", "brand"],
            },
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            result = await extract_structured_data(
                content=text_content,
                model="gpt-4o",
                data_schema=products_schema,
                prompt="Extract all products with their details...",
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        assert result is not None
        assert len(result) == 3
        assert "iPhone" in result[0]["name"]
        assert "999" in result[0]["price"]
        assert result[0]["brand"] == "Apple"

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_handle_multiple_text_content_items(self):
        """Test handling multiple text content items"""
        text_contents = [
            {
                "type": "text",
                "data": "Customer: Alice Johnson",
            },
            {
                "type": "text",
                "data": "Order ID: ORD-12345",
            },
            {
                "type": "text",
                "data": "Total: $156.78",
            },
        ]

        order_schema = {
            "type": "object",
            "properties": {
                "customer": {"type": "string", "description": "Customer name"},
                "orderId": {"type": "string", "description": "Order identifier"},
                "total": {"type": "string", "description": "Order total amount"},
            },
            "required": ["customer", "orderId", "total"],
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            result = await extract_structured_data(
                content=text_contents,
                model="gpt-4o",
                data_schema=order_schema,
                prompt="Extract order information from the text fragments. .",
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        assert result is not None
        assert result["customer"] == "Alice Johnson"
        assert result["orderId"] == "ORD-12345"
        assert result["total"] == "$156.78"

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_extract_data_from_image_url_content(self):
        """Test extracting data from image URL content"""
        # Using a public test image URL
        image_content: ImageUrlContentItem = {
            "type": "image-url",
            "image_type": "png",
            "data": "https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2-accordion-3-800x513-1?resMode=sharp2&op_usm=1.5,0.65,15,0&wid=1664&hei=1062&qlt=100&fmt=png-alpha&fit=constrain",
        }

        image_schema = {
            "type": "array",
            "items": {
                "type": "string",
                "description": "Todo item shown in the middle panel",
            },
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
        result = await extract_structured_data(
            content=image_content,
            model="gpt-4o",
            data_schema=image_schema,
            prompt="pleasee Extract todo items from the image, they are shown in the middle panel... .",
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        # Check if any todo item contains "Yoga" (based on the TS test expectation)
        assert any("Yoga" in item for item in result)

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_handle_invalid_image_urls_gracefully(self):
        """Test handling invalid image URLs gracefully"""
        image_content: ImageUrlContentItem = {
            "type": "image-url",
            "image_type": "png",
            "data": "https://invalid-url-com/image.png",
        }

        schema = {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
            },
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            with pytest.raises(ValueError, match="Fetching image from URL"):
                await extract_structured_data(
                    content=image_content,
                    model="gpt-4o",
                    data_schema=schema,
                    api_key=os.getenv("OPENAI_API_KEY"),
                )

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_extract_data_from_mixed_text_and_image_content(self):
        """Test extracting data from mixed text and image content"""
        mixed_content = [
            {
                "type": "text",
                "data": "Product: iPhone 15 Pro Max",
            },
            {
                "type": "text",
                "data": "Price: $1,199",
            },
            {
                "type": "image-url",
                "image_type": "png",
                "data": "https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2-accordion-3-800x513-1?resMode=sharp2&op_usm=1.5,0.65,15,0&wid=1664&hei=1062&qlt=100&fmt=png-alpha&fit=constrain",
            },
        ]

        product_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Product name"},
                "price": {"type": "string", "description": "Product price"},
                "imageDescription": {
                    "type": "string",
                    "description": "Description of the product image",
                },
            },
            "required": ["name", "price", "imageDescription"],
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            result = await extract_structured_data(
                content=mixed_content,
                model="gpt-4o",
                data_schema=product_schema,
                prompt="Extract product information from both text and image, thanks",
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        assert result is not None
        assert "iPhone" in result["name"]
        assert "1,199" in result["price"]

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_validate_data_schema(self):
        """Test data schema validation"""
        text_content: TextContentItem = {
            "type": "text",
            "data": "test data",
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            with pytest.raises(ValueError, match="Invalid extract data input"):
                await extract_structured_data(
                    content=text_content,
                    data_schema="invalid schema",  # type: ignore
                    model="gpt-4o",
                    api_key=os.getenv("OPENAI_API_KEY"),
                )

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_validate_model_parameter(self):
        """Test model parameter validation"""
        text_content: TextContentItem = {
            "type": "text",
            "data": "test data",
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            with pytest.raises(RuntimeError):
                await extract_structured_data(
                    content=text_content,
                    data_schema={"type": "object", "properties": {}},
                    model="invalid-model",  # type: ignore
                    api_key=os.getenv("OPENAI_API_KEY"),
                )

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_handle_empty_content_gracefully(self):
        """Test handling empty content gracefully"""
        text_content: TextContentItem = {
            "type": "text",
            "data": "",
        }

        schema = {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Any message found"},
            },
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            result = await extract_structured_data(
                content=text_content,
                model="gpt-4o",
                data_schema=schema,
                prompt="Extract any information from the content.. .",
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        # Should handle empty content gracefully and return some result
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_handle_empty_array_content(self):
        """Test handling empty array content"""
        schema = {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Any message found"},
            },
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            result = await extract_structured_data(
                content=[],
                model="gpt-4o",
                data_schema=schema,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
            assert result is None

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_cache_enabling_disabling(self):
        """Test cache enabling/disabling"""
        text_content: TextContentItem = {
            "type": "text",
            "data": "John Doe",
        }

        schema = {
            "type": "object",
            "properties": {
                "Name": {"type": "string", "description": "User Name"},
            },
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            # Test with cache enabled (default)
            result1 = await extract_structured_data(
                content=text_content,
                model="gpt-4o",
                data_schema=schema,
                enable_cache=True,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            # Test with cache disabled
            result2 = await extract_structured_data(
                content=text_content,
                model="gpt-4o",
                data_schema=schema,
                enable_cache=False,
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        assert result1 is not None
        assert result2 is not None

    @pytest.mark.asyncio
    @pytest.mark.skip
    async def test_max_retries_parameter(self):
        """Test maxRetries parameter"""
        text_content: TextContentItem = {
            "type": "text",
            "data": "Test content for retry behavior",
        }

        schema = {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content summary"},
            },
        }
        with IntunedContext() as ctx:
            ctx.run_context = IntunedRunContext(
                job_id="sample-job",
                job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
                run_id="yyPCx2XF7Eu9nda",
                auth_session_id=None,
            )
            result = await extract_structured_data(
                content=text_content,
                model="gpt-4o-mini",
                data_schema=schema,
                max_retires=1,
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        assert result is None
