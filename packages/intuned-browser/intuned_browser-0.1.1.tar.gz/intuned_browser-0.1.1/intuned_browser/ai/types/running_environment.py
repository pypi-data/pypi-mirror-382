from enum import Enum


class RunningEnvironment(str, Enum):
    AUTHORING = "AUTHORING"
    PUBLISHED = "PUBLISHED"
