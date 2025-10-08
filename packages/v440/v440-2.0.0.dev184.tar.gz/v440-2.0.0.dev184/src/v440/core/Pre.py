from __future__ import annotations

from typing import *

from v440._utils.Cfg import Cfg
from v440._utils.QualStringer import QualStringer

__all__ = ["Pre"]


class Pre(QualStringer):

    __slots__ = ()
    string: str
    phase: str
    num: int

    def _cmp(self: Self) -> tuple:
        if not self:
            return frozenset("0")
        return frozenset("1"), self.phase, self.num

    @classmethod
    def _phase_parse(cls: type, value: str) -> str:
        return Cfg.cfg.data["phases"][value]

    def _string_fset_minus(self: Self, value: str) -> None:
        raise ValueError
