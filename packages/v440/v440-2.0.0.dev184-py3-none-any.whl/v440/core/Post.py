from __future__ import annotations

from typing import *

from v440._utils.QualStringer import QualStringer

__all__ = ["Post"]


class Post(QualStringer):

    __slots__ = ()
    string: str
    phase: str
    num: int

    def _cmp(self: Self) -> int:
        if self.phase:
            return self.num
        else:
            return -1

    @classmethod
    def _phase_parse(cls: type, value: str) -> str:
        if value in ("post", "r", "rev"):
            return "post"
        else:
            raise ValueError

    def _string_fset_minus(self: Self, value: str) -> None:
        self._phase = "post"
        self._num = int(value)
