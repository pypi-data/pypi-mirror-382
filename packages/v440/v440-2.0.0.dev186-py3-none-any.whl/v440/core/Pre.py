from __future__ import annotations

from typing import *

from v440._utils.Cfg import Cfg
from v440._utils.QualStringer import QualStringer

__all__ = ["Pre"]


class Pre(QualStringer):

    __slots__ = ()
    string: str
    lit: str
    num: int

    def _cmp(self: Self) -> tuple:
        if not self:
            return (frozenset("0"),)
        return frozenset("1"), self.lit, self.num

    @classmethod
    def _lit_parse(cls: type, value: str) -> str:
        return Cfg.cfg.data["phases"][value]

    def _string_fset_minus(self: Self, value: str) -> None:
        raise ValueError
