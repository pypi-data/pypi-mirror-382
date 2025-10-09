
from typing import Hashable, Callable, Mapping


def reverse_dict(__d: dict, ignore_unhashable_values: bool = False, unite_duplicates: Callable[[dict[Hashable, list[Hashable]]], Mapping] = None):
    if ignore_unhashable_values:
        __d = remove_unhashable_values(__d)
    if unite_duplicates is not None:
        duplicates, vals = {}, {}
        for k, v in __d.items():
            if v in vals:
                if not duplicates.get(v):
                    duplicates[v] = [vals[v]]
                duplicates[v].append(k)
            else:
                vals[v] = k
        duplicates_data = unite_duplicates(duplicates)
    n = {}
    for k, v in __d.items():
        if unite_duplicates is not None and v in duplicates_data:
            k = duplicates_data[v]
        n[v] = k
    return n


def remove_unhashable_values(d: dict):
    n = d.copy()
    for k, v in d.items():
        try:
            hash(v)
        except TypeError:
            del n[k]
    return n

