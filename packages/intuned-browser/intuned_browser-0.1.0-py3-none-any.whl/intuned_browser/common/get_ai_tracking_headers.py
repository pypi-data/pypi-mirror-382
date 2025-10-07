from enum import Enum
from typing import Literal

from pydantic import BaseModel

from intuned_browser.common.types import RunningEnvironment


class AiTrackingHeadersParams(BaseModel):
    environment: RunningEnvironment
    type: Literal["DYNAMIC_LIST", "DYNAMIC_OBJECT", "IS_PAGE_LOADED"]
    run_id: str | None = None
    job_id: str | None = None
    job_run_id: str | None = None


def get_ai_tracking_headers(
    environment: RunningEnvironment,
    type: Literal["DYNAMIC_LIST", "DYNAMIC_OBJECT", "IS_PAGE_LOADED"],
    run_id: str | None = None,
    job_id: str | None = None,
    job_run_id: str | None = None,
) -> dict[str, str]:
    # Create and validate the params using Pydantic
    params = AiTrackingHeadersParams(
        environment=environment,
        type=type,
        run_id=run_id,
        job_id=job_id,
        job_run_id=job_run_id,
    )

    headers = {}
    if params.run_id:
        headers["x-intuned-run-id"] = params.run_id
    if params.job_id:
        headers["x-intuned-job-id"] = params.job_id
    if params.job_run_id:
        headers["x-intuned-job-run-id"] = params.job_run_id

    headers["x-intuned-environment"] = (
        params.environment.value if isinstance(params.environment, Enum) else str(params.environment)
    )
    headers["x-intuned-type"] = params.type

    return headers
