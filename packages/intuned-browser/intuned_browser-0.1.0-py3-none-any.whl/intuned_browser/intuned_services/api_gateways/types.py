from dataclasses import dataclass
from enum import Enum
from typing import Any


class GatewayMode(Enum):
    DIRECT = "direct"
    GATEWAY = "gateway"


@dataclass
class GatewayConfig:
    functions_domain: str | None = None
    workspace_id: str | None = None
    project_id: str | None = None

    def __post_init__(self):
        try:
            from runtime.env import get_functions_domain
            from runtime.env import get_project_id
            from runtime.env import get_workspace_id

            self.functions_domain = get_functions_domain()
            self.workspace_id = get_workspace_id()
            self.project_id = get_project_id()
        except ImportError as e:
            raise RuntimeError("Intuned Runtime SDK is required to use Intuned AI Gateway.") from e


@dataclass
class ModelConfig:
    model: str
    api_key: str | None = None
    extra_headers: dict[str, Any] | None = None
    base_url: str | None = None
