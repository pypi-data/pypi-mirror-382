from __future__ import annotations

import operator
from functools import partial
from typing import *

from v440._utils.releaseparse import ranging


def getitem(data: tuple, key: SupportsIndex | slice) -> list:
    ans: int | tuple
    if type(key) is slice:
        r: range = ranging.torange(key, len(data))
        f: partial = partial(getitem_int, data)
        ans = list(map(f, r))
    else:
        ans = getitem_int(data, operator.index(key))
    return ans


def getitem_int(data: tuple[int], key: int) -> int:
    if key < len(data):
        return data[key]
    else:
        return 0
