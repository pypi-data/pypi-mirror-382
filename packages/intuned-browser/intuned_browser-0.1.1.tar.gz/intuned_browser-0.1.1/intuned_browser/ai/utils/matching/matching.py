import logging
import string
from typing import Literal

from playwright.async_api import ElementHandle
from playwright.async_api import Page

from intuned_browser.ai.types import MatchMode
from intuned_browser.ai.types import MatchResult
from intuned_browser.common import ensure_browser_scripts

# Logger
logger = logging.getLogger(__name__)


def normalize_spacing(*, text: str) -> str:
    """
    Normalize spacing in a string by replacing multiple spaces with a single space,
    and removing newlines and tabs. Also converts the text to lowercase.

    Args:
        text (str): The input string to normalize.

    Returns:
        str: The normalized string with consistent spacing and in lowercase.
    """
    # Replace newlines and tabs with spaces
    normalized = text.replace("\n", " ").replace("\t", " ")

    # Replace multiple spaces with a single space
    normalized = " ".join(normalized.split())

    return normalized.strip()


def remove_punctuation_and_spaces(*, s: str) -> str:
    """
    Removes all punctuation characters and spaces from the string.

    Args:
        s: The input string

    Returns:
        String with punctuation and spaces removed
    """
    return "".join(c for c in s if c not in string.punctuation and c != " ")


MatchRank = Literal["HIGH", "LOW"]


def rank_match(*, original: str, match: str) -> MatchRank:
    """
    Rank the quality of a match between two strings.

    Args:
        original: The original string
        match: The potential match

    Returns:
        'HIGH' for good matches, 'LOW' for poor matches
    """
    try:
        from Levenshtein import ratio as ratio_function

        normalized_original = normalize_spacing(text=original).lower()
        normalized_match = normalize_spacing(text=match).lower()
        ratio: float = ratio_function(normalized_original, normalized_match)

        len_original = len(normalized_original)
        if len_original > 20 and ratio > 0.85:
            return "HIGH"

        normalized_original = remove_punctuation_and_spaces(s=normalized_original)
        normalized_match = remove_punctuation_and_spaces(s=normalized_match)

        if normalized_original == normalized_match:
            return "HIGH"

        return "LOW"
    except ImportError:
        logging.warning("Levenshtein package not found, falling back to simple comparison")
        # Fallback if Levenshtein is not available
        normalized_original = remove_punctuation_and_spaces(s=normalize_spacing(text=original).lower())
        normalized_match = remove_punctuation_and_spaces(s=normalize_spacing(text=match).lower())

        if normalized_original == normalized_match:
            return "HIGH"

        return "LOW"


def select_best_match(*, original: str, matches: list[MatchResult]) -> str | None:
    """
    Select the best matc h from a list of potential matches.

    Args:
        original: The original string to match
        matches: List of potential matches

    Returns:
        The best matching string or None if no good match is found
    """
    exact_matches = [match for match in matches if match.get("match_mode") != MatchMode.FUZZY]

    if exact_matches:
        return exact_matches[0]["matched_value"]

    fuzzy_matches = [match for match in matches if match.get("match_mode") == MatchMode.FUZZY]

    # rank the fuzzy matches
    ranked_fuzzy_matches = [
        (match, rank_match(original=original, match=match["matched_value"])) for match in fuzzy_matches
    ]

    # drop all low ranked matches
    ranked_fuzzy_matches = [match for match in ranked_fuzzy_matches if match[1] == "HIGH"]

    fuzzy_matches = [match[0] for match in ranked_fuzzy_matches]

    if ranked_fuzzy_matches:
        # Sort fuzzy matches by fuzzy_distance in ascending order
        sorted_fuzzy_matches = sorted(fuzzy_matches, key=lambda x: x["fuzzy_distance"] or float("inf"))
        return sorted_fuzzy_matches[0]["matched_value"]

    return None


async def match_strings_with_dom_content(
    *, page_object: Page, strings_list: list[str], container: ElementHandle | None = None
) -> dict[str, list[MatchResult]]:
    """
    Find matches for strings in the DOM content.

    This function uses the browser scripts to find matches for strings in the DOM.

    Args:
        page_object: The Playwright page object
        strings_list: List of strings to find matches for
        container: Optional container to limit the search scope

    Returns:
        A dictionary mapping strings to their matches
    """
    try:
        # Ensure browser scripts are loaded
        await ensure_browser_scripts(page=page_object)

        # Get the container handle if provided
        if container:
            handle = container
        else:
            handle = await page_object.locator("html").element_handle()

        # Use the browser script to find matches
        matches = await page_object.evaluate(
            """async ([container, searchTexts]) => {
                try {
                    if (typeof window.__INTUNED__ !== 'undefined' &&
                        typeof window.__INTUNED__.matchStringsWithDomContent === 'function') {
                        return await window.__INTUNED__.matchStringsWithDomContent(
                            container,
                            searchTexts
                        );
                    } else {
                        // Fallback if the function is not available
                        return searchTexts.reduce((acc, text) => {
                            acc[text] = [];
                            return acc;
                        }, {});
                    }
                } catch (error) {
                    console.error('Error matching strings with DOM content:', error);
                    return searchTexts.reduce((acc, text) => {
                        acc[text] = [];
                        return acc;
                    }, {});
                }
            }""",
            [handle, strings_list],
        )

        return matches
    except Exception as e:
        logging.warning(f"Error matching strings with DOM content: {e}")

        # Return empty matches if there's an error
        return {string: [] for string in strings_list}


async def replace_with_best_matches(
    *, strings_to_match: list[str], page_object: Page, container: ElementHandle | None = None
) -> dict[str, str | None]:
    """
    Find the best matches for strings in the page content using DOM matching.

    Args:
        strings_to_match: List of strings to find matches for
        page_object: The Playwright page object
        container: Optional container to limit the search scope

    Returns:
        A dictionary mapping original strings to their best matches or None if no match found
    """
    # Find matches for all strings in the DOM
    matches_map = await match_strings_with_dom_content(
        page_object=page_object, strings_list=strings_to_match, container=container
    )

    return {
        string: select_best_match(original=string, matches=matches) if matches else string
        for string, matches in matches_map.items()
    }


async def create_xpath_mapping(page: Page, extracted_data: dict | list) -> dict[str, list[str]]:
    """
    Create a mapping of text values to their XPath locations in the DOM.

    Args:
        page: The Playwright page object
        extracted_data: The extracted data structure (dict, list of dicts, or list of strings)

    Returns:
        A dictionary mapping text values to lists of their XPath locations
    """
    xpath_mapping: dict[str, list[str]] = {}

    unique_values = set()
    await ensure_browser_scripts(page=page)

    if isinstance(extracted_data, dict):
        # Single object
        unique_values.update(str(value) for value in extracted_data.values())
    elif isinstance(extracted_data, list):
        if len(extracted_data) > 0 and isinstance(extracted_data[0], str):
            # Array of strings
            unique_values.update(extracted_data)
        else:
            # Array of objects
            for obj in extracted_data:
                if isinstance(obj, dict):
                    unique_values.update(str(value) for value in obj.values())

    for value in unique_values:
        # Initialize the array for this value
        xpath_mapping[value] = []

        # Find all elements containing this text
        locators = page.get_by_text(value, exact=True)
        count = await locators.count()

        for i in range(count):
            locator = locators.nth(i)

            # Get the element's xpath
            element_info = await locator.evaluate("el => window.__INTUNED__.getElementXPath(el)")
            xpath_mapping[value].append(element_info)

    return xpath_mapping


async def validate_xpath_mapping(page: Page, cached_mapping: dict[str, list[str]]) -> bool:
    """
    Validate that a cached XPath mapping still matches the current DOM state.

    Args:
        page: The Playwright page object
        cached_mapping: The cached mapping of text values to XPath locations

    Returns:
        True if all XPaths still exist and contain the expected text, False otherwise
    """
    try:
        for expected_text, xpaths in cached_mapping.items():
            for xpath in xpaths:
                # Check if element exists and has the expected text
                # faster than playwright .locator because no autowait.
                element_exists = await page.evaluate(
                    """
                    xpath => {
                        const element = document.evaluate(
                            xpath,
                            document,
                            null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE,
                            null
                        ).singleNodeValue;
                        return element !== null;
                    }
                """,
                    xpath,
                )

                if not element_exists:
                    return False

                # Get the text content of the element
                actual_text = await page.evaluate(
                    """
                    xpath => {
                        const element = document.evaluate(
                            xpath,
                            document,
                            null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE,
                            null
                        ).singleNodeValue;
                        return element?.textContent?.trim() || "";
                    }
                """,
                    xpath,
                )

                if actual_text != expected_text:
                    return False

        return True
    except Exception as error:
        logger.error("Error validating XPath mapping: %s", error)
        return False
