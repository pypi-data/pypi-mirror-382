from enum import Enum

from pydantic import BaseModel
from pydantic import Field


class RunningEnvironment(Enum):
    AUTHORING = "AUTHORING"
    PUBLISHED = "PUBLISHED"


class S3Configs(BaseModel):
    """Configuration for S3 storage."""

    access_key: str | None = Field(description="Access key for S3 storage", default=None)
    secret_key: str | None = Field(description="Secret key for S3 storage", default=None)
    bucket_name: str | None = Field(description="Name of the S3 bucket", default=None)
    region: str | None = Field(description="Region where the S3 bucket is located", default=None)
    endpoint: str | None = Field(description="Custom endpoint URL for S3 (optional)", default=None)
