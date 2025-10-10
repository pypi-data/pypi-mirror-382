import re

from bs4 import BeautifulSoup
from bs4 import Comment


def sanitize_html(
    html_string: str,
    *,
    remove_scripts: bool = True,
    remove_styles: bool = True,
    remove_svgs: bool = True,
    remove_comments: bool = True,
    remove_long_attributes: bool = True,
    max_attribute_length: int = 500,
    preserve_attributes: list[str] | None = None,
    remove_empty_tags: bool = True,
    preserve_empty_tags: list[str] | None = None,
    minify_whitespace: bool = True,
) -> str:
    if preserve_attributes is None:
        preserve_attributes = ["class", "src"]
    if preserve_empty_tags is None:
        preserve_empty_tags = ["img"]

    # Parse the HTML
    soup = BeautifulSoup(html_string, "html.parser")

    # Remove specified elements
    elements_to_remove = []
    if remove_scripts:
        elements_to_remove.append("script")
    if remove_styles:
        elements_to_remove.append("style")
    if remove_svgs:
        elements_to_remove.append("svg")

    if elements_to_remove:
        for element in soup(elements_to_remove):
            element.decompose()

    # Remove HTML comments
    if remove_comments:
        for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
            comment.extract()

    # Remove long attributes and style attributes
    if remove_long_attributes:
        for tag in soup.find_all():
            for attr, value in list(tag.attrs.items()):
                if attr in preserve_attributes:
                    continue
                if attr == "style" or len(str(value)) > max_attribute_length:
                    del tag.attrs[attr]

    # Remove empty tags
    if remove_empty_tags:
        for tag in soup.find_all():
            if tag.name not in preserve_empty_tags and len(tag.get_text(strip=True)) == 0 and len(tag.find_all()) == 0:
                tag.decompose()

    # Get the cleaned HTML as a string
    sanitized_html = str(soup)

    # Minify whitespace
    if minify_whitespace:
        # Remove white spaces between tags
        sanitized_html = sanitized_html.replace(">\n<", "><")
        # Remove multiple empty lines
        sanitized_html = re.sub(r"\n\s*\n", "\n", sanitized_html)
        # Remove multiple spaces
        sanitized_html = re.sub(r"\s+", " ", sanitized_html)

    return sanitized_html
