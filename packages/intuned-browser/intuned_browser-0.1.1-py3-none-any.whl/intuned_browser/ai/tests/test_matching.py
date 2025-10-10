import logging

import pytest

# Optional imports with warning
try:
    from runtime import launch_chromium
except ImportError:
    launch_chromium = None

    logging.warning("Runtime dependencies are not available. Some test features will be disabled.")

from intuned_browser.ai.types import MatchMode
from intuned_browser.ai.utils.matching import match_strings_with_dom_content
from intuned_browser.ai.utils.matching import normalize_spacing
from intuned_browser.ai.utils.matching import rank_match
from intuned_browser.ai.utils.matching import remove_punctuation_and_spaces
from intuned_browser.ai.utils.matching import replace_with_best_matches
from intuned_browser.ai.utils.matching import select_best_match


class TestNormalizeSpacing:
    """Test cases for normalize_spacing function"""

    def test_multiple_spaces(self):
        """Test that multiple spaces are replaced with single space"""
        result = normalize_spacing(text="hello    world")
        assert result == "hello world"

    def test_newlines_and_tabs(self):
        """Test that newlines and tabs are replaced with spaces"""
        result = normalize_spacing(text="hello\nworld\tthere")
        assert result == "hello world there"

    def test_mixed_whitespace(self):
        """Test handling of mixed whitespace characters"""
        result = normalize_spacing(text="  hello\n\n  world\t\tthere  ")
        assert result == "hello world there"

    def test_empty_string(self):
        """Test handling of empty string"""
        result = normalize_spacing(text="")
        assert result == ""

    def test_only_whitespace(self):
        """Test string with only whitespace"""
        result = normalize_spacing(text="   \n\t  ")
        assert result == ""


class TestRemovePunctuationAndSpaces:
    """Test cases for remove_punctuation_and_spaces function"""

    def test_basic_punctuation(self):
        """Test removal of basic punctuation"""
        result = remove_punctuation_and_spaces(s="Hello, World!")
        assert result == "HelloWorld"

    def test_all_punctuation_types(self):
        """Test removal of various punctuation marks"""
        result = remove_punctuation_and_spaces(s="Test@#$%^&*()_+-=[]{}|;':\",./<>?")
        assert result == "Test"

    def test_spaces_removal(self):
        """Test removal of spaces"""
        result = remove_punctuation_and_spaces(s="hello world there")
        assert result == "helloworldthere"

    def test_mixed_content(self):
        """Test mixed punctuation and spaces"""
        result = remove_punctuation_and_spaces(s="Hello, World! How are you?")
        assert result == "HelloWorldHowareyou"

    def test_empty_string(self):
        """Test empty string"""
        result = remove_punctuation_and_spaces(s="")
        assert result == ""


class TestRankMatch:
    """Test cases for rank_match function"""

    def test_exact_match(self):
        """Test ranking of exact matches"""
        result = rank_match(original="Hello World", match="Hello World")
        assert result == "HIGH"

    def test_case_insensitive_match(self):
        """Test case insensitive matching"""
        result = rank_match(original="Hello World", match="hello world")
        assert result == "HIGH"

    def test_punctuation_difference(self):
        """Test matching with punctuation differences"""
        result = rank_match(original="Hello, World!", match="Hello World")
        assert result == "HIGH"

    def test_long_string_high_similarity(self):
        """Test long strings with high similarity"""
        original = "This is a very long string with more than twenty characters"
        match = "This is a very long string with more than twenty character"
        result = rank_match(original=original, match=match)
        assert result == "HIGH"

    def test_completely_different_strings(self):
        """Test completely different strings"""
        result = rank_match(original="Hello World", match="Goodbye Universe")
        assert result == "LOW"

    def test_short_string_partial_match(self):
        """Test short strings with partial match"""
        result = rank_match(original="Hello", match="Hell")
        assert result == "LOW"


class TestSelectBestMatch:
    """Test cases for select_best_match function"""

    def test_exact_match_preferred(self):
        """Test that exact matches are preferred over fuzzy matches"""
        matches = [
            {"matched_value": "Hello Worlds", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 1},
            {"matched_value": "Hello World", "match_mode": MatchMode.FULL, "fuzzy_distance": 0},
        ]
        result = select_best_match(original="Hello World", matches=matches)
        assert result == "Hello World"

    def test_fuzzy_match_ranking(self):
        """Test fuzzy match selection based on distance"""
        matches = [
            {"matched_value": "Hello Worlds", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 1},
            {"matched_value": "Hello World!", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 0.5},
            {"matched_value": "Hello Worldz", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 2},
        ]
        result = select_best_match(original="Hello World", matches=matches)
        assert result == "Hello World!"

    def test_no_good_matches(self):
        """Test when no good matches are found"""
        matches = [
            {"matched_value": "Completely Different", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 10},
        ]
        result = select_best_match(original="Hello World", matches=matches)
        assert result is None

    def test_empty_matches_list(self):
        """Test with empty matches list"""
        result = select_best_match(original="Hello World", matches=[])
        assert result is None

    def test_multiple_exact_matches(self):
        """Test when multiple exact matches exist, first one is selected"""
        matches = [
            {"matched_value": "Hello World!", "match_mode": MatchMode.FULL, "fuzzy_distance": 0},
            {"matched_value": "Hello World", "match_mode": MatchMode.FULL, "fuzzy_distance": 0},
            {"matched_value": "HELLO WORLD", "match_mode": MatchMode.FULL, "fuzzy_distance": 0},
        ]
        result = select_best_match(original="Hello World", matches=matches)
        assert result == "Hello World!"

    def test_fuzzy_match_with_none_distance(self):
        """Test fuzzy matches where some have None as fuzzy_distance"""
        matches = [
            {"matched_value": "Hello Worlds", "match_mode": MatchMode.FUZZY, "fuzzy_distance": None},
            {"matched_value": "Hello World!", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 2},
            {"matched_value": "Hello Wor", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 1},
        ]
        result = select_best_match(original="Hello World", matches=matches)
        assert result == "Hello World!"

    def test_only_low_ranked_fuzzy_matches(self):
        """Test when all fuzzy matches are ranked LOW and should return None"""
        matches = [
            {"matched_value": "Completely Different Text", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 0.5},
            {"matched_value": "Another Unrelated String", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 1},
            {"matched_value": "Not Even Close", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 0.2},
        ]
        result = select_best_match(original="Hello World", matches=matches)
        assert result is None

    def test_mixed_match_modes_with_exact_substring(self):
        """Test with SUBSTRING match mode mixed with others"""
        matches = [
            {"matched_value": "Hello", "match_mode": MatchMode.PARTIAL, "fuzzy_distance": 0},
            {"matched_value": "Hello Worlds", "match_mode": MatchMode.FUZZY, "fuzzy_distance": 1},
            {"matched_value": "World", "match_mode": MatchMode.PARTIAL, "fuzzy_distance": 0},
        ]
        result = select_best_match(original="Hello World", matches=matches)
        assert result == "Hello"  # First non-fuzzy match


@pytest.mark.asyncio
@pytest.mark.headed
class TestDOMMatching:
    """Test cases for DOM matching functions"""

    async def test_match_strings_with_dom_content_basic(self):
        """Test basic string matching in DOM content"""
        if launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        async with launch_chromium(headless=False) as (_, page):
            # Create a simple HTML page for testing
            await page.set_content("""
                <html>
                    <body>
                        <h1>Hello World</h1>
                        <p>This is a test paragraph</p>
                        <span>Another test element</span>
                    </body>
                </html>
            """)

            strings_to_match = ["Hello World", "test paragraph", "Another test"]
            matches = await match_strings_with_dom_content(page_object=page, strings_list=strings_to_match)

            logging.info(f"Matches found: {matches}")

            # Verify that matches were found for each string
            assert "Hello World" in matches
            assert "test paragraph" in matches
            assert "Another test" in matches

    async def test_match_strings_with_container(self):
        """Test string matching within a specific container"""
        if launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        async with launch_chromium(headless=False) as (_, page):
            await page.set_content("""
                <html>
                    <body>
                        <div id="container1">
                            <p>Text in container 1</p>
                        </div>
                        <div id="container2">
                            <p>Text in container 2</p>
                        </div>
                    </body>
                </html>
            """)

            container = await page.locator("#container1").element_handle()
            strings_to_match = ["Text in container 1", "Text in container 2"]

            matches = await match_strings_with_dom_content(
                page_object=page, strings_list=strings_to_match, container=container
            )

            logging.info(f"Container matches: {matches}")

            # Container 1 should only match text within it
            assert "Text in container 1" in matches
            assert "Text in container 2" in matches

    async def test_replace_with_best_matches(self):
        """Test replacing strings with best matches from DOM"""
        if launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        async with launch_chromium(headless=False) as (_, page):
            await page.set_content("""
                <html>
                    <body>
                        <h1>Welcome to Our Website</h1>
                        <p>This is the main content area</p>
                        <button>Click Here!</button>
                    </body>
                </html>
            """)

            strings_to_match = [
                "Welcome to Our Website",  # Exact match
                "main content",  # Partial match
                "Click Here",  # Match without punctuation
                "Non-existent text",  # No match
            ]

            replacements = await replace_with_best_matches(strings_to_match=strings_to_match, page_object=page)

            logging.info(f"Replacements: {replacements}")

            # Verify replacements
            assert "Welcome to Our Website" in replacements
            assert "Non-existent text" in replacements

    async def test_error_handling(self):
        """Test error handling in DOM matching functions"""
        if launch_chromium is None:
            pytest.skip("Runtime dependencies not available")
        async with launch_chromium(headless=False) as (_, page):
            # Don't navigate to any page - page will be empty
            strings_to_match = ["Some text"]

            # This should not raise an exception
            matches = await match_strings_with_dom_content(page_object=page, strings_list=strings_to_match)

            # Should return empty matches on error
            assert matches == {"Some text": []}
