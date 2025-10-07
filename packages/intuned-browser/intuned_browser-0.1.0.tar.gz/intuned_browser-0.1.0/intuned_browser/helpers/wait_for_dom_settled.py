import functools
import logging
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import overload

from playwright.async_api import Locator
from playwright.async_api import Page

logger = logging.getLogger(__name__)


# Overload 1: Direct call with source and action
@overload
async def wait_for_dom_settled(
    source: Page | Locator,
    action: Callable[[], Awaitable[Any]],
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> Any: ...


# Overload 2: Direct call with source only (original behavior)
@overload
async def wait_for_dom_settled(
    source: Page | Locator,
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> bool: ...


# Overload 3: Decorator without arguments
@overload
def wait_for_dom_settled(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]: ...


# Overload 4: Decorator factory with arguments
@overload
def wait_for_dom_settled(
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]: ...


def wait_for_dom_settled(
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Unified function that waits for DOM to settle. Supports multiple usage patterns:

    1. Direct call: Execute an action and wait for DOM to settle
        ```python
        await wait_for_dom_settled(page, action, settle_duration=0.5, timeout_s=30.0)
        # or
        await wait_for_dom_settled(source=page, func=action)
        ```

    2. Direct call without action: Just wait for DOM to settle
        ```python
        await wait_for_dom_settled(page, settle_duration=0.5, timeout_s=30.0)
        # or
        await wait_for_dom_settled(source=page)
        ```

    3. Decorator without arguments: Decorates a function that has page/source in its arguments
        ```python
        @wait_for_dom_settled
        async def my_function(page: Page, ...):
            ...
        # or
        decorated = wait_for_dom_settled(func=my_function)
        ```

    4. Decorator with arguments: Decorates a function with custom settle/timeout settings
        ```python
        @wait_for_dom_settled(settle_duration=1.0, timeout_s=60.0)
        async def my_function(page: Page, ...):
            ...
        ```

    Args:
        source: Playwright page or locator object (when used as direct call)
        action/func: Async function to execute (when used as direct call or decorator)
        settle_duration: Duration in seconds to wait for DOM to stabilize (default: 0.5)
        timeout_s: Maximum time to wait for DOM to settle (default: 30.0)

    Returns:
        Result of the action, boolean (for source-only call), decorated function, or decorator
    """
    # Case 1a: Direct call with source and func as keyword arguments
    # await wait_for_dom_settled(source=page, func=action)
    if "source" in kwargs and "func" in kwargs:
        source = kwargs["source"]
        action = kwargs["func"]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)
        return _wait_for_dom_settled_core(
            source=source,
            func=action,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    # Case 1b: Direct call with source only (original behavior)
    # await wait_for_dom_settled(source=page)
    if "source" in kwargs and "func" not in kwargs:
        source = kwargs["source"]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)
        return _wait_for_dom_settled_original(
            source=source,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    # Case 2a: Direct call with source and action as positional arguments
    # await wait_for_dom_settled(page, action, ...)
    if len(args) >= 2 and isinstance(args[0], Page | Locator) and callable(args[1]):
        source = args[0]
        action = args[1]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)
        return _wait_for_dom_settled_core(
            source=source,
            func=action,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    # Case 2b: Direct call with source only as positional argument
    # await wait_for_dom_settled(page)
    if len(args) == 1 and isinstance(args[0], Page | Locator):
        source = args[0]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)
        return _wait_for_dom_settled_original(
            source=source,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    # Case 3a: Used as decorator with func keyword argument
    # decorated_func = wait_for_dom_settled(func=my_function)
    # OR bound method: wait_for_dom_settled(func=page.locator(...).click)
    if "func" in kwargs and len(args) == 0:
        func = kwargs["func"]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)

        # Check if it's a bound method with page attribute
        if hasattr(func, "__self__") and hasattr(func.__self__, "page"):
            extracted_page = func.__self__.page
            if isinstance(extracted_page, Page):
                return _wait_for_dom_settled_core(
                    source=extracted_page,
                    func=func,
                    settle_duration=settle_duration,
                    timeout_s=timeout_s,
                )

        return _create_decorated_function(func, settle_duration=settle_duration, timeout_s=timeout_s)

    # Case 3b: Used as decorator without arguments (positional)
    # @wait_for_dom_settled
    if len(args) == 1 and callable(args[0]) and not isinstance(args[0], Page | Locator):
        func = args[0]
        return _create_decorated_function(func, settle_duration=0.5, timeout_s=30.0)

    # Case 4: Used as decorator factory with arguments
    # @wait_for_dom_settled(settle_duration=1.0, timeout_s=60.0)
    settle_duration = kwargs.get("settle_duration", 0.5)
    timeout_s = kwargs.get("timeout_s", 30.0)

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        return _create_decorated_function(func, settle_duration=settle_duration, timeout_s=timeout_s)

    return decorator


def _create_decorated_function(
    func: Callable[..., Awaitable[Any]],
    settle_duration: float,
    timeout_s: float,
) -> Callable[..., Awaitable[Any]]:
    """Helper to create a decorated function with DOM waiting."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Find the Page or Locator object in function arguments
        source_obj = None
        for arg in args:
            if isinstance(arg, Page | Locator):
                source_obj = arg
                break
        if source_obj is None:
            source_obj = kwargs.get("page") or kwargs.get("source")

        if not source_obj:
            logger.error("No Page or Locator object found in function arguments")
            raise ValueError("No Page or Locator object found in function arguments")

        async def func_with_args():
            return await func(*args, **kwargs)

        return await _wait_for_dom_settled_core(
            source=source_obj,
            func=func_with_args,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    return wrapper


async def _wait_for_dom_settled_core(
    *,
    source: Page | Locator,
    func: Callable[..., Awaitable[Any]],
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
):
    """Core function that executes the provided function and then waits for DOM to settle."""
    logger.debug(f"Source object: {source}")

    # Execute the function first
    result = await func()

    # Then wait for DOM to settle
    await _wait_for_dom_settled_original(
        source=source,
        settle_duration=settle_duration,
        timeout_s=timeout_s,
    )

    return result


async def _wait_for_dom_settled_original(
    source: Page | Locator,
    *,
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> bool:
    """Original DOM settlement detection logic."""
    settle_duration_ms = int(settle_duration * 1000)
    timeout_ms = int(timeout_s * 1000)

    # Get the page object
    if isinstance(source, Locator):
        page_obj = source.page
        element_handle = await source.element_handle()
    else:
        page_obj = source
        element_handle = await page_obj.evaluate_handle("document.documentElement")

    js_code = f"""
    (target) => {{
        return new Promise((resolve, reject) => {{
            if (!target) {{
                reject(new Error('Target element not found'));
                return;
            }}

            let mutationTimer;
            let timeoutTimer;
            let settled = false;

            const observer = new MutationObserver(() => {{
                if (settled) return;

                clearTimeout(mutationTimer);
                mutationTimer = setTimeout(() => {{
                    settled = true;
                    observer.disconnect();
                    clearTimeout(timeoutTimer);
                    resolve(true);
                }}, {settle_duration_ms});
            }});

            timeoutTimer = setTimeout(() => {{
                settled = true;
                observer.disconnect();
                clearTimeout(mutationTimer);
                reject(new Error('DOM timed out settling after {timeout_ms} ms'));
            }}, {timeout_ms});

            observer.observe(target, {{
                childList: true,
                subtree: true,
                attributes: true,
                characterData: true
            }});

            // Initial timer for already-stable DOM
            mutationTimer = setTimeout(() => {{
                settled = true;
                observer.disconnect();
                clearTimeout(timeoutTimer);
                resolve(true);
            }}, {settle_duration_ms});
        }});
    }}
    """

    try:
        result = await page_obj.evaluate(js_code, element_handle)
        return result
    except Exception as e:
        logger.warning(f"DOM settlement detection failed: {e}")
        return False
