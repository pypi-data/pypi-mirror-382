from __future__ import annotations

from typing import *

import packaging.version
import setdoc

from v440._utils.SlotStringer import SlotStringer
from v440.core.Local import Local
from v440.core.Public import Public

__all__ = ["Version"]


class Version(SlotStringer):
    __slots__ = ("_public", "_local")

    string: str
    local: Local
    public: Public

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.local or self.public)

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._public = Public()
        self._local = Local()
        self.string = string

    def _cmp(self: Self) -> tuple:
        return self.public, self.local

    def _format(self: Self, format_spec: str) -> str:
        ans: str = format(self.public, format_spec)
        if self.local:
            ans += "+" + format(self.local)
        return ans

    def _string_fset(self: Self, value: str) -> None:
        parsed: Iterable
        if value.endswith("+"):
            raise ValueError
        elif "+" in value:
            parsed = value.split("+")
        else:
            parsed = value, ""
        self.public.string, self.local.string = parsed

    def _todict(self: Self) -> dict:
        return dict(public=self.public, local=self.local)

    @property
    def local(self: Self) -> Local:
        "This property represents the local identifier."
        return self._local

    def packaging(self: Self) -> packaging.version.Version:
        "This method returns an eqivalent packaging.version.Version object."
        return packaging.version.Version(str(self))

    @property
    def public(self: Self) -> Self:
        "This property represents the public identifier."
        return self._public
