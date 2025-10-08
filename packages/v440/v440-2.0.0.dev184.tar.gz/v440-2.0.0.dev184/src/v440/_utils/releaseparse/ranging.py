from __future__ import annotations

import operator
from typing import *

__all__ = ["torange"]


def torange(key: slice, length: int) -> range:
    step: int = calcstep(key.step)
    start: int = calcstart(key.start, length=length, bwd=step < 0)
    stop: int = calcstop(key.stop, length=length, bwd=step < 0)
    ans: range = range(start, stop, step)
    return ans


def calcstep(value: Optional[SupportsIndex]) -> int:
    if value is None:
        return 1
    return operator.index(value)


def calcstart(value: Optional[SupportsIndex], *, length: int, bwd: bool) -> int:
    if value is None:
        if bwd:
            return length - 1
        else:
            return 0
    ans: int = operator.index(value)
    if ans >= 0:
        return ans
    return max(-bwd, ans + length)


def calcstop(value: Optional[SupportsIndex], *, length: int, bwd: bool) -> int:
    if value is None:
        if bwd:
            return -1
        else:
            return length
    ans: int = operator.index(value)
    if ans >= 0:
        return ans
    return max(-bwd, ans + length)
