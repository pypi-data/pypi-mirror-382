from __future__ import annotations

import operator
import string as string_
from typing import *

import setdoc

from v440._utils.ListStringer import ListStringer

__all__ = ["Local"]


class Local(ListStringer):
    __slots__ = ()

    string: str
    data: tuple

    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self._data = ()
        self.string = string

    @classmethod
    def _data_parse(cls: type, value: list) -> Iterable:
        return tuple(map(cls._item_parse, value))

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        return ".".join(map(str, self))

    @classmethod
    def _item_parse(cls: type, value: Any) -> int | str:
        ans: Optional[int | str]
        try:
            ans = operator.index(value)
        except Exception:
            ans = str(value).lower()
            if ans.strip(string_.digits + string_.ascii_lowercase):
                raise
            if not ans.strip(string_.digits):
                ans = int(ans)
        else:
            if ans < 0:
                raise ValueError
        return ans

    @classmethod
    def _sort(cls: type, value: Any) -> tuple[bool, int | str]:
        return type(value) is int, value

    def _string_fset(self: Self, value: str) -> None:
        if value == "":
            self.data = ()
            return
        v: str = value
        if v.startswith("+"):
            v = v[1:]
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self.data = v.split(".")
