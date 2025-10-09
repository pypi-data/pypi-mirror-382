# modified from: https://github.com/microsoft/MoGe/blob/6b8b43db567ca4b08615c39b42cffd6c76cada29/moge/utils/tools.py

import math
from typing import Any, Generator, MutableMapping


def traverse_nested_dict_keys(
    d: dict[str, dict],
) -> Generator[tuple[str, ...], None, None]:
    for k, v in d.items():
        if isinstance(v, dict):
            for sub_key in traverse_nested_dict_keys(v):
                yield (k,) + sub_key
        else:
            yield (k,)


def get_nested_dict(d: dict[str, dict], keys: tuple[str, ...], default: Any = None):
    for k in keys:
        d = d.get(k, default)
        if d is None:
            break
    return d


def set_nested_dict(d: dict[str, dict], keys: tuple[str, ...], value: Any):
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value


def key_average(list_of_dicts: list) -> dict[str, Any]:
    """
    Returns a dictionary with the average value of each key in the input list of dictionaries.
    """
    _nested_dict_keys = set()
    for d in list_of_dicts:
        _nested_dict_keys.update(traverse_nested_dict_keys(d))
    _nested_dict_keys = sorted(_nested_dict_keys)
    result = {}
    for k in _nested_dict_keys:
        values = []
        for d in list_of_dicts:
            v = get_nested_dict(d, k)
            if v is not None and not math.isnan(v):
                values.append(v)
        avg = sum(values) / len(values) if values else float("nan")
        set_nested_dict(result, k, avg)
    return result


def flatten_nested_dict(
    d: dict[str, Any], parent_key: tuple[str, ...] = None
) -> dict[tuple[str, ...], Any]:
    """
    Flattens a nested dictionary into a single-level dictionary, with keys as tuples.
    """
    items = []
    if parent_key is None:
        parent_key = ()
    for k, v in d.items():
        new_key = parent_key + (k,)
        if isinstance(v, MutableMapping):
            items.extend(flatten_nested_dict(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)
