import logging
import re
from typing import Any

from intuned_browser.intuned_services.cache.types import CacheGetResponse
from intuned_browser.intuned_services.cache.types import CacheSetRequest
from intuned_browser.intuned_services.cache.types import CacheSetResponse

logger = logging.getLogger(__name__)
try:
    from runtime.backend_functions._call_backend_function import call_backend_function
except ImportError:
    call_backend_function = None

    logger.warning(
        "Runtime dependencies are not available. Cache will not be available. Install 'intuned-runtime' to enable this feature."
    )


forbidden_characters = re.compile(r"[:#]")


def validate_key(key: str) -> str:
    if len(key) < 1:
        raise ValueError("Key must be at least 1 character long")

    if forbidden_characters.search(key):
        raise ValueError('Key cannot contain the following characters: ":" or "#"')

    return key


class Cache:
    async def get(self, key: str) -> Any:
        try:
            if call_backend_function is None:
                logger.warning(
                    "Runtime dependencies are not available. Cache will not be available. Install 'intuned-runtime' to enable this feature."
                )
                return
            parsed_key = validate_key(key)
            response = await call_backend_function(
                name=f"cache/{parsed_key}",
                method="GET",
                validation_model=CacheGetResponse,
            )
            if not response or not response.value:
                return
            return response.value["value"]
        except Exception as e:
            logger.error(f"Error getting cache value for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any) -> None:
        try:
            if call_backend_function is None:
                logger.warning(
                    "Runtime dependencies are not available. Cache will not be available. Install 'intuned-runtime' to enable this feature."
                )
                return
            key_result = validate_key(key)
            request_params = CacheSetRequest(value=value)

            await call_backend_function(
                f"cache/{key_result}", validation_model=CacheSetResponse, method="PUT", params=request_params
            )
        except Exception as e:
            logger.error(f"Error setting cache value for key {key}: {e}")
