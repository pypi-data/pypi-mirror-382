import hashlib
import json
from typing import Any
from typing import Literal


def _serialize(obj: Any, treat_arrays_as_unsorted_lists: bool) -> str:
    if isinstance(obj, dict) and hasattr(obj, "items") and callable(obj.items):
        # Handle dict-like objects (including custom Map-like objects)
        if hasattr(obj, "items"):
            return _serialize(list(obj.items()), treat_arrays_as_unsorted_lists)
    elif isinstance(obj, list):
        serialized_sorted_array = [_serialize(el, treat_arrays_as_unsorted_lists) for el in obj]

        if treat_arrays_as_unsorted_lists:
            serialized_sorted_array = sorted(serialized_sorted_array)

        return f"[{','.join(serialized_sorted_array)}]"
    elif isinstance(obj, dict) and obj is not None:
        acc = ""
        keys = sorted(obj.keys())
        acc += f"{{{json.dumps(keys)}"
        for key in keys:
            acc += f"{_serialize(obj[key], treat_arrays_as_unsorted_lists)},"

        return f"{acc}}}"

    return json.dumps(obj)


def hash_object(
    obj: Any,
    treat_arrays_as_unsorted_lists: bool = False,
    hash_algorithm: Literal["SHA256"] = "SHA256",
    encoding: Literal["hex"] = "hex",
) -> str:
    hash_obj = hashlib.new(hash_algorithm.lower())
    serialized = _serialize(obj, treat_arrays_as_unsorted_lists)
    hash_obj.update(serialized.encode("utf-8"))
    return hash_obj.hexdigest() if encoding == "hex" else hash_obj.digest()
