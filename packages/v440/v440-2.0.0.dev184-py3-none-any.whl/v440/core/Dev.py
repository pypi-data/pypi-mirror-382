from __future__ import annotations

from typing import *

from v440._utils.QualStringer import QualStringer

__all__ = ["Dev"]


class Dev(QualStringer):

    __slots__ = ()
    string: str
    phase: str
    num: int

    def _cmp(self: Self) -> tuple:
        if self.phase:
            return 0, self.num
        else:
            return (1,)

    @classmethod
    def _phase_parse(cls: type, value: str) -> str:
        if value == "dev":
            return "dev"
        else:
            raise ValueError

    def _string_fset_minus(self: Self, value: str) -> None:
        raise ValueError
