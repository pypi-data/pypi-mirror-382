from typing import TypedDict


class SimplifiedHtmlOptions(TypedDict, total=False):
    should_include_on_click: bool
    should_include_content_as_prop: bool
    keep_only_visible_elements: bool
    should_include_iframes: bool


async def get_simplified_html(container_handle, options: SimplifiedHtmlOptions | None = None) -> str:
    if options is None:
        options = {}

    tag_name_handle = await container_handle.evaluate_handle("(element) => element.tagName.toLowerCase()")

    tag_name = await tag_name_handle.json_value()
    should_return_full_html = tag_name == "html"

    options_with_default = {
        "shouldIncludeOnClick": options.get("should_include_on_click", False),
        "shouldIncludeContentAsProp": options.get("should_include_content_as_prop", False),
        "keepOnlyVisibleElements": options.get("keep_only_visible_elements", True),
        "shouldIncludeIframes": options.get("should_include_iframes", False),
        "shouldReturnFullHtml": should_return_full_html,
    }

    simplified_html = await container_handle.evaluate(
        """(element, { optionsWithDefault }) => {
            const ALLOWED_ATTRIBUTES= [
            "aria-label",
            "data-name",
            "name",
            "type",
            "placeholder",
            "value",
            "role",
            "title",
            "href",
            "id",
            "alt",
            new RegExp(/^data-/),
            ];

            function truthyFilter(value) {
                return Boolean(value);
            }

            function isElementNode(node) {
                return node.nodeType === node.ELEMENT_NODE;
            }

            const hasAnyAllowedAttribute = (
                element,
                allowedAttributes
            ) => {
                const elementAttributes = element.getAttributeNames();
                const hasAllowedAttribute = !!allowedAttributes.some((attr) => {
                    if (typeof attr === "string") {
                        return element.hasAttribute(attr);
                    } else if (attr instanceof RegExp) {
                        return elementAttributes.some((attrName) => attr.test(attrName));
                    }
                });
                return hasAllowedAttribute;
            };

            function isElementVisible(style) {
                return (
                    style.opacity !== "" &&
                    style.display !== "none" &&
                    style.visibility !== "hidden" &&
                    style.opacity !== "0"
                );
            }

            function isElementInteractive(element, style) {
                return (
                    element.tagName === "A" ||
                    element.tagName === "INPUT" ||
                    element.tagName === "BUTTON" ||
                    element.tagName === "SELECT" ||
                    element.tagName === "TEXTAREA" ||
                    element.hasAttribute("onclick") ||
                    element.hasAttribute("onmousedown") ||
                    element.hasAttribute("onmouseup") ||
                    element.hasAttribute("onkeydown") ||
                    element.hasAttribute("onkeyup") ||
                    style.cursor === "pointer"
                );
            }

            function getDocumentFromIframeElementSafely(element) {
                try {
                    if (element.contentWindow && element.contentWindow.document) {
                        return element.contentWindow.document.documentElement;
                    }
                } catch (error) {
                    return undefined;
                }
            }

            function isInputWithValue(element) {
                return (
                    element.tagName === "INPUT" &&
                    element.value &&
                    element.value.trim()
                );
            }

            function generateSimplifiedDom(
                element,
                interactiveElements,
                document,
                allowedAttributes,
                shouldIncludeContentAsProp,
                keepOnlyVisibleElements
            ) {
                if (element.nodeType === 3 && element.textContent?.trim()) {
                    return document.createTextNode(element.textContent + " ");
                }

                const shouldSkipElementChecks = optionsWithDefault.shouldIncludeIframes
                    ? ["BODY", "HTML", "IFRAME"]
                    : ["BODY", "HTML"].includes(element.nodeName);

                if (!isElementNode(element)) {
                    return null;
                }

                const style = window.getComputedStyle(element);
                const isVisible = isElementVisible(style) || shouldSkipElementChecks;

                if (
                    keepOnlyVisibleElements &&
                    !isVisible &&
                    !isInputWithValue(element)
                ) {
                    return null;
                }

                let children = optionsWithDefault.shouldIncludeIframes &&
                    element.nodeName === "IFRAME"
                    ? [getDocumentFromIframeElementSafely(element)].filter(Boolean)
                    : Array.from(element.childNodes)
                        .map((c) =>
                            generateSimplifiedDom(
                                c,
                                interactiveElements,
                                document,
                                allowedAttributes,
                                shouldIncludeContentAsProp,
                                keepOnlyVisibleElements
                            )
                        )
                        .filter(truthyFilter);

                if (element.tagName === "BODY")
                    children = children.filter((c) => c.nodeType !== 3);

                const interactive = isElementInteractive(element, style) ||
                    element.hasAttribute("role");

                const hasLabel = element.hasAttribute("aria-label") ||
                    element.hasAttribute("name");

                const hasAllowedAttribute = hasAnyAllowedAttribute(
                    element,
                    allowedAttributes
                );

                let includeNode = interactive || hasLabel || hasAllowedAttribute ||
                    shouldSkipElementChecks;

                if (
                    children.length === 0 &&
                    !hasAnyAllowedAttribute(element, allowedAttributes)
                ) {
                    return null;
                }

                if (
                    children.length === 1 &&
                    !hasAnyAllowedAttribute(element, allowedAttributes) &&
                    children[0].nodeType !== 3 &&
                    !(shouldSkipElementChecks && optionsWithDefault.shouldReturnFullHtml)
                ) {
                    return children[0];
                }

                if (!includeNode && children.length === 0) return null;

                if (!includeNode && children.some((c) => c.nodeType === 3)) {
                    includeNode = true;
                }

                if (!includeNode && children.length === 1) {
                    return children[0];
                }

                const container = element.cloneNode();
                const allAttributes = element.getAttributeNames();

                const listOfAttributesToRemove = allAttributes.filter((attr) => {
                    const isAllowedString = allowedAttributes.includes(attr);
                    const isAllowedRegExp = allowedAttributes.some(
                        (regex) => regex instanceof RegExp && regex.test(attr)
                    );
                    return !isAllowedString && !isAllowedRegExp;
                });

                for (const attr of listOfAttributesToRemove) {
                    container.removeAttribute(attr);
                }

                if (interactive) {
                    interactiveElements.push(element);
                }

                if (shouldIncludeContentAsProp && element.textContent) {
                    container.setAttribute("content", element.textContent);
                }

                children.forEach((child) => container.appendChild(child));

                return container;
            }

            function getSimplifiedDomFromElement(
                htmlElement,
                shouldIncludeOnClick,
                shouldIncludeContentAsProp,
                keepOnlyVisibleElements
            ) {
                const interactiveElements = [];

                const allowedAttributes = shouldIncludeOnClick
                    ? [...ALLOWED_ATTRIBUTES, "onclick"]
                    : ALLOWED_ATTRIBUTES;

                const simplifiedDom = generateSimplifiedDom(
                    htmlElement,
                    interactiveElements,
                    htmlElement.ownerDocument,
                    allowedAttributes,
                    shouldIncludeContentAsProp,
                    keepOnlyVisibleElements
                );

                if (!simplifiedDom) return "";

                return simplifiedDom.outerHTML;
            }

            return getSimplifiedDomFromElement(
                element,
                optionsWithDefault.shouldIncludeOnClick,
                optionsWithDefault.shouldIncludeContentAsProp,
                optionsWithDefault.keepOnlyVisibleElements
            );
        }""",
        {
            "optionsWithDefault": options_with_default,
        },
    )

    return simplified_html
