from typing import Any


def collect_strings(*, data_structure: dict[str, Any] | list[dict[str, Any]] | None | str) -> list[str]:
    """
    Recursively collect all string values from a nested data structure.

    Args:
        data_structure: The data structure to collect strings from

    Returns:
        A list of all string values found in the data structure
    """
    strings = []

    if data_structure is None:
        return strings

    if isinstance(data_structure, str):
        strings.append(data_structure)
    elif isinstance(data_structure, int | float):
        strings.append(str(data_structure))
    elif isinstance(data_structure, list):
        for item in data_structure:
            strings.extend(collect_strings(data_structure=item))
    elif isinstance(data_structure, dict):
        for value in data_structure.values():
            strings.extend(collect_strings(data_structure=value))

    return strings
