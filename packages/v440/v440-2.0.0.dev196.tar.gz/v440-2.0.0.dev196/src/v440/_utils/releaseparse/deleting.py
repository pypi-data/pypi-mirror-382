from __future__ import annotations

import operator
from typing import *

from v440._utils.releaseparse import ranging


def delitem(data: tuple, key: Any) -> bool:
    if type(key) is slice:
        return delitem_slice(data, key)
    else:
        return delitem_index(data, key)


def delitem_index(data: tuple, key: SupportsIndex) -> tuple:
    i: int = operator.index(key)
    if i >= len(data):
        return data
    l: list = list(data)
    del l[i]
    return tuple(l)


def delitem_slice(data: tuple, key: slice) -> tuple:
    r: range = ranging.torange(key, len(data))
    k: Any
    keys: list = list()
    for k in r:
        if k < len(data):
            keys.append(k)
    keys.sort(reverse=True)
    editable: list = list(data)
    for k in keys:
        del editable[k]
    return tuple(editable)
