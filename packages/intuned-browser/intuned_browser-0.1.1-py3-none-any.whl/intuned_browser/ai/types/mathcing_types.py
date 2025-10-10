from enum import Enum
from typing import TypedDict


class MatchMode(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    FUZZY = "fuzzy"


class MatchSource(str, Enum):
    ATTRIBUTE = "attribute"
    TEXT_CONTENT = "text_content"
    DIRECT_TEXT_NODE = "direct_text_node"


class MatchResult(TypedDict):
    xpath: str
    match_source: MatchSource
    attribute: str | None
    tag: str
    matched_value: str
    matched_source_value: str
    match_mode: MatchMode
    fuzzy_distance: int | None  # Store the fuzzy match score if match_mode is FUZZY
