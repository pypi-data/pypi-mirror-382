import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import override
from typing import TYPE_CHECKING

from pydantic import BaseModel

from intuned_browser.helpers.utils.get_mode import is_generate_code_mode
from intuned_browser.helpers.utils.get_s3_client import get_async_s3_session

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class UploadedFile:
    file_name: str
    bucket: str
    region: str
    endpoint: str | None
    suggested_file_name: str


def sanitize_key(key):
    """
    Sanitize a key string by replacing non-alphanumeric characters with underscores
    and consolidating multiple underscores into single underscores.
    Args:
        key (str): The input string to sanitize
    Returns:
        str: Sanitized string
    """
    # Replace any non-alphanumeric chars (except .-_/) with underscore
    result = re.sub(r"[^a-zA-Z0-9.\-_/]", "_", key)
    # Replace multiple underscores with single underscore
    result = re.sub(r"_{2,}", "_", result)
    return result


class AttachmentType(str, Enum):
    DOCUMENT = "document"


class Attachment(BaseModel):
    file_name: str
    bucket: str
    region: str
    endpoint: str | None = None
    suggested_file_name: str
    file_type: AttachmentType = AttachmentType.DOCUMENT

    def __json__(self):
        return self.model_dump()

    def to_dict(self) -> dict[str, str]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Attachment":
        return cls.model_validate(data)

    async def get_signed_url(self, expiration: int = 3600 * 24 * 5) -> str:
        """
        Generate a presigned URL for downloading the file from S3.

        Args:
            expiration: URL expiration time in seconds (default: 5 days)

        Returns:
            Presigned URL string
        """
        if is_generate_code_mode():
            return "https://not.real.com"

        session, endpoint_url = get_async_s3_session(endpoint_url=self.endpoint)

        async with session.client("s3", endpoint_url=endpoint_url) as s3_client:  # type: S3Client
            response = await s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket, "Key": self.file_name},
                ExpiresIn=expiration,
                HttpMethod="GET",
            )
        return response

    def get_s3_key(self):
        if self.should_upload_to_r2():
            raise Exception("get_s3_key function is not supported when using a custom s3 endpoint")

        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{self.file_name}"

    def get_file_path(self):
        return self.file_name

    def should_upload_to_r2(self):
        if isinstance(self.endpoint, str) and self.endpoint == "":
            return False
        return True


class SignedUrlAttachment(Attachment):
    _download_signed_url: str

    def __init__(
        self,
        *,
        file_name: str,
        download_signed_url: str,
        suggested_file_name: str,
    ):
        super().__init__(
            file_name=file_name,
            bucket="",
            region="",
            endpoint=None,
            suggested_file_name=suggested_file_name,
            file_type=AttachmentType.DOCUMENT,
        )
        self._download_signed_url = download_signed_url

    @override
    async def get_signed_url(self, expiration: int | None = 3600 * 24 * 5) -> str:
        """Return the pre-signed download URL (already signed, so expiration is ignored)."""
        return self._download_signed_url

    @override
    def get_s3_key(self):
        raise Exception("SignedUrlAttachment does not support get_s3_key function")
