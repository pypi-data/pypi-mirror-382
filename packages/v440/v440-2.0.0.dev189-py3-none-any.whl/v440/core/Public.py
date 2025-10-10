from __future__ import annotations

from typing import *

import setdoc

from v440._utils.Pattern import Pattern
from v440._utils.SlotStringer import SlotStringer
from v440.core.Base import Base
from v440.core.Qual import Qual

__all__ = ["Public"]


class Public(SlotStringer):

    __slots__ = ("_base", "_qual")

    string: str
    base: Base
    qual: Qual

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.base or self.qual)

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._base = Base()
        self._qual = Qual()
        self.string = string

    def _cmp(self: Self) -> tuple:
        return self.base, self.qual

    def _format(self: Self, format_spec: str) -> str:
        return format(self.base, format_spec) + format(self.qual)

    def _string_fset(self: Self, value: str) -> None:
        match: Any = Pattern.PUBLIC.leftbound.search(value)
        self.base.string = value[: match.end()]
        self.qual.string = value[match.end() :]

    def _todict(self: Self) -> dict:
        return dict(base=self.base, qual=self.qual)

    @property
    def base(self: Self) -> Base:
        "This property represents the version base."
        return self._base

    @property
    def qual(self: Self) -> Qual:
        "This property represents the qualification."
        return self._qual
