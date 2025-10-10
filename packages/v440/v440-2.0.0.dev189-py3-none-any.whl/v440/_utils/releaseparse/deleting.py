from __future__ import annotations

import operator
from typing import *

from overloadable import Overloadable

from v440._utils.releaseparse import ranging


@Overloadable
def delitem(data: tuple, key: Any) -> bool:
    return type(key) is slice


@delitem.overload(False)
def delitem(data: tuple, key: SupportsIndex) -> tuple:
    i: int = operator.index(key)
    if i >= len(data):
        return data
    l: list = list(data)
    del l[i]
    return tuple(l)


@delitem.overload(True)
def delitem(data: tuple, key: slice) -> tuple:
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
