import os

from aioboto3 import Session

from intuned_browser.common.types import S3Configs


def get_async_s3_session(
    endpoint_url: str | None = None, configs: S3Configs | None = None
) -> tuple[Session, str | None]:
    """
    Get an aioboto3 Session configured for S3 operations.
    Returns a tuple of (session, endpoint_url) that can be used with async context manager.

    Usage:
        session, endpoint = get_async_s3_session(endpoint, configs)
        async with session.client('s3', endpoint_url=endpoint) as s3_client:
            await s3_client.put_object(...)
    """
    region_name = (
        configs.region
        if configs and configs.region
        else os.environ.get("AWS_REGION") or os.environ.get("INTUNED_S3_REGION")
    )
    aws_access_key_id = (
        configs.access_key
        if configs and configs.access_key
        else os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("INTUNED_S3_ACCESS_KEY_ID")
    )
    aws_secret_access_key = (
        configs.secret_key
        if configs and configs.secret_key
        else os.environ.get("AWS_SECRET_ACCESS_KEY") or os.environ.get("INTUNED_S3_SECRET_ACCESS_KEY")
    )

    session = Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )
    return session, endpoint_url
