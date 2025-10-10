from __future__ import annotations

from typing import *

import setdoc
from overloadable import Overloadable

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

    @Overloadable
    @setdoc.basic
    def __init__(self: Self, *args: Any, **kwargs: Any) -> str:
        self._base = Base()
        self._qual = Qual()
        argc: int = len(args) + len(kwargs)
        keys: set = set(kwargs.keys())
        if argc <= 1 and keys <= {"string"}:
            return "string"
        return "slots"

    @__init__.overload("string")
    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self.string = string

    @__init__.overload("slots")
    @setdoc.basic
    def __init__(
        self: Self,
        base: Any = "0",
        qual: Any = "",
    ) -> None:
        self.base.string = base
        self.qual.string = qual

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
