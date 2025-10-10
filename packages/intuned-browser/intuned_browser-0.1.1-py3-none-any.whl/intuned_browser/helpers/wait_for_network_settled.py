import asyncio
import functools
import logging
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import overload

from playwright.async_api import Page
from playwright.async_api import Request

logger = logging.getLogger(__name__)


# Overload 1: Direct call with page and action
@overload
async def wait_for_network_settled(
    page: Page,
    action: Callable[[], Awaitable[Any]],
    timeout_s: int = 30,
    max_inflight_requests: int = 0,
) -> Any: ...


# Overload 2: Decorator without arguments
@overload
def wait_for_network_settled(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]: ...


# Overload 3: Decorator factory with arguments
@overload
def wait_for_network_settled(
    timeout_s: int = 30,
    max_inflight_requests: int = 0,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]: ...


def wait_for_network_settled(
    *args: Any,
    **kwargs: Any,
) -> Any:
    # Case 1a: Direct call with page and action as keyword arguments
    # await wait_for_network_settled(page=page, func=action)
    if "page" in kwargs and "func" in kwargs:
        page = kwargs["page"]
        action = kwargs["func"]
        timeout_s = kwargs.get("timeout_s", 30)
        max_inflight_requests = kwargs.get("max_inflight_requests", 0)
        return _wait_for_network_settled_core(
            page=page,
            func=action,
            timeout_s=timeout_s,
            max_inflight_requests=max_inflight_requests,
        )

    # Case 1b: Direct call with page and action as positional arguments
    # await wait_for_network_settled(page, action, ...)
    if len(args) >= 2 and isinstance(args[0], Page) and callable(args[1]):
        page = args[0]
        action = args[1]
        timeout_s = kwargs.get("timeout_s", 30)
        max_inflight_requests = kwargs.get("max_inflight_requests", 0)
        return _wait_for_network_settled_core(
            page=page,
            func=action,
            timeout_s=timeout_s,
            max_inflight_requests=max_inflight_requests,
        )

    # Case 2a: Used as decorator with func keyword argument
    # decorated_func = wait_for_network_settled(func=my_function)
    if "func" in kwargs and len(args) == 0:
        func = kwargs["func"]
        timeout_s = kwargs.get("timeout_s", 30)
        max_inflight_requests = kwargs.get("max_inflight_requests", 0)
        return _create_decorated_function(func, timeout_s=timeout_s, max_inflight_requests=max_inflight_requests)

    # Case 2b: Used as decorator without arguments (positional)
    # @wait_for_network_settled
    if len(args) == 1 and callable(args[0]) and not isinstance(args[0], Page):
        func = args[0]
        return _create_decorated_function(func, timeout_s=30, max_inflight_requests=0)

    # Case 3: Used as decorator factory with arguments
    # @wait_for_network_settled(timeout_s=60)
    timeout_s = kwargs.get("timeout_s", 30)
    max_inflight_requests = kwargs.get("max_inflight_requests", 0)

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        return _create_decorated_function(func, timeout_s=timeout_s, max_inflight_requests=max_inflight_requests)

    return decorator


def _create_decorated_function(
    func: Callable[..., Awaitable[Any]],
    timeout_s: int,
    max_inflight_requests: int,
) -> Callable[..., Awaitable[Any]]:
    """Helper to create a decorated function with network waiting."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Find the page object in function arguments
        page = next((arg for arg in args if isinstance(arg, Page)), None)
        if page is None:
            page = kwargs.get("page")

        if not page:
            logging.error("No Page object found in function arguments")
            raise ValueError("No Page object found in function arguments")

        async def func_with_args():
            return await func(*args, **kwargs)

        return await _wait_for_network_settled_core(
            page=page,
            func=func_with_args,
            timeout_s=timeout_s,
            max_inflight_requests=max_inflight_requests,
        )

    return wrapper


async def _wait_for_network_settled_core(
    *,
    page: Page,
    func: Callable[..., Awaitable[Any]],
    timeout_s: int = 30,
    max_inflight_requests: int = 0,
):
    """Core implementation of network settling logic."""
    logging.debug(f"Page object: {page}")
    network_settled_event = asyncio.Event()
    is_timeout = False
    request_counter = 0
    action_done = False
    pending_requests: set[Request] = set()

    async def maybe_settle():
        if action_done and request_counter <= max_inflight_requests:
            network_settled_event.set()

    def on_request(request: Request):
        nonlocal request_counter
        request_counter += 1
        pending_requests.add(request)
        logging.debug(f"+[{request_counter}]: {request.url}")

    async def on_request_done(request: Request):
        nonlocal request_counter
        # Simulate asynchronous handling
        await asyncio.sleep(0)
        if request in pending_requests:
            request_counter -= 1
            pending_requests.discard(request)
            logging.debug(f"-[{request_counter}]: {request.url}")
            await maybe_settle()

    # Define listener functions to allow proper removal later
    async def handle_request_finished(req: Request):
        await on_request_done(req)

    async def handle_request_failed(req: Request):
        await on_request_done(req)

    # Add listeners
    page.on("request", on_request)
    page.on("requestfinished", handle_request_finished)
    page.on("requestfailed", handle_request_failed)

    async def timeout_task():
        nonlocal is_timeout
        await asyncio.sleep(timeout_s)
        logger.info("waiting for network to settle timed out")
        is_timeout = True
        network_settled_event.set()

    try:
        result = await func()
        action_done = True
        await asyncio.sleep(0.5)
        await maybe_settle()
        timeout_task_handle = asyncio.create_task(timeout_task())
        logger.info("-- Start waiting for network to settle... --")
        while True:
            logger.info(f"waiting for network to settle, {request_counter} requests pending")
            await network_settled_event.wait()
            await asyncio.sleep(0.5)
            if (action_done and request_counter <= max_inflight_requests) or is_timeout:
                if is_timeout:
                    logger.info("Exiting due to timeout, network did not settle")
                else:
                    logger.info("network settled, no pending requests")
                break
            else:
                network_settled_event = asyncio.Event()
        logger.info("-- Finished waiting for network to settle --")
        return result
    finally:
        # Remove listeners using the same function references
        page.remove_listener("request", on_request)
        page.remove_listener("requestfinished", handle_request_finished)
        page.remove_listener("requestfailed", handle_request_failed)
        try:
            timeout_task_handle.cancel()
        except Exception:
            pass
