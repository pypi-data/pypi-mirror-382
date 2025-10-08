from __future__ import annotations

import operator
from typing import *

from v440._utils.releaseparse import ranging


def numeral(value: SupportsIndex) -> int:
    ans: int = operator.index(value)
    if ans < 0:
        raise ValueError
    else:
        return ans


def setitem(data: tuple, key: Any, value: Any) -> tuple:
    f: Callable
    k: int | range
    v: int | tuple[int]
    if type(key) is slice:
        f = setitem_range
        k = ranging.torange(key, len(data))
        v = tuple(map(numeral, value))
    else:
        f = setitem_int
        k = operator.index(key)
        v = numeral(value)
    return f(data, k, v)


def setitem_int(data: tuple, key: int, value: int) -> tuple:
    if key < len(data):
        edit: list = list(data)
        edit[key] = value
        return tuple(edit)
    if value == 0:
        return data
    data += (0,) * (key - len(data))
    data += (value,)
    return data


def setitem_range(data: tuple, key: range, value: tuple[int]) -> tuple:
    edit: list = list(data)
    while len(edit) < max(key.start + 1, key.stop):
        edit.append(0)
    edit[key.start : key.stop : key.step] = value
    while len(edit) and not edit[-1]:
        edit.pop()
    ans: tuple = tuple(edit)
    return ans
