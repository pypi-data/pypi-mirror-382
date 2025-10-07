# this should take data as a generic type T and return a generic type T
from typing import TypeVar

T = TypeVar("T")


def filter_empty_values(data: T) -> T:
    if isinstance(data, dict):
        filtered = {}
        for k, v in data.items():
            # Recursively filter the value
            filtered_value = filter_empty_values(v)

            # Skip if the filtered value is empty
            if _is_empty(filtered_value):
                continue

            filtered[k] = filtered_value
        return filtered

    elif isinstance(data, list):
        filtered = []
        for item in data:
            # Recursively filter each item
            filtered_item = filter_empty_values(item)

            # Skip if the filtered item is empty
            if _is_empty(filtered_item):
                continue

            filtered.append(filtered_item)
        return filtered

    else:
        # For non-dict/list types, return as-is
        return data


def _is_empty(value: T) -> bool:
    """
    Helper function to check if a value should be considered empty.

    Args:
        value: The value to check

    Returns:
        bool: True if the value is considered empty, False otherwise
    """
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, (list | dict)) and len(value) == 0:
        return True
    return False
