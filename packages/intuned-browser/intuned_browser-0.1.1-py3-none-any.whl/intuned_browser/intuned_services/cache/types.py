from typing import Any

from pydantic import BaseModel


class CacheGetResponse(BaseModel):
    value: dict[str, Any] | None = None


class CacheSetResponse(BaseModel):
    pass


class CacheSetRequest(BaseModel):
    value: Any
