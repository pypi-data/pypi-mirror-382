import os


def get_environment_variable(name: str):
    value = os.getenv(name)
    if value is not None:
        return value
    else:
        raise ValueError(f"Environment variable '{name}' not found.")
