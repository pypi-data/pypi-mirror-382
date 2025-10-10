from __future__ import annotations

import operator
from typing import *

import setdoc

from v440._utils.guarding import guard
from v440._utils.SlotStringer import SlotStringer
from v440.core.Release import Release

__all__ = ["Base"]


class Base(SlotStringer):

    __slots__ = ("_epoch", "_release")

    string: str
    epoch: int
    release: Release

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.epoch or self.release)

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._epoch = 0
        self._release = Release()
        self.string = string

    def _cmp(self: Self) -> tuple:
        return self.epoch, self.release

    def _format(self: Self, format_spec: str) -> str:
        ans: str = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += format(self.release, format_spec)
        return ans

    def _string_fset(self: Self, value: str) -> None:
        v: str = value
        if v.startswith("v"):
            v = v[1:]
        if "!" not in v:
            self.epoch = 0
            self.release.string = v
            return
        parsed: Iterable = v.split("!")
        self.epoch = int(parsed.pop(0))
        (self.release.string,) = parsed

    def _todict(self: Self) -> dict:
        return dict(epoch=self.epoch, release=self.release)

    @property
    def epoch(self: Self) -> int:
        "This property represents the epoch."
        return self._epoch

    @epoch.setter
    @guard
    def epoch(self: Self, value: Any) -> None:
        v: int = operator.index(value)
        if v < 0:
            raise ValueError
        self._epoch = v

    @property
    def release(self: Self) -> Release:
        "This property represents the release."
        return self._release
