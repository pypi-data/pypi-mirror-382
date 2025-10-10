import operator
from abc import abstractmethod
from typing import *

import setdoc
from datarepr import datarepr

from v440._utils.BaseStringer import BaseStringer
from v440._utils.guarding import guard

__all__ = ["QualStringer"]


class QualStringer(BaseStringer):
    __slots__ = ("_lit", "_num")

    string: str
    lit: str
    num: int

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return self.lit != ""

    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self._lit = ""
        self._num = 0
        self.string = string

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(
            type(self).__name__,
            lit=self.lit,
            num=self.num,
        )

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        if self.lit:
            return self.lit + str(self.num)
        else:
            return ""

    @classmethod
    @abstractmethod
    def _lit_parse(cls: type, value: str) -> str: ...

    def _string_fset(self: Self, value: str) -> None:
        if value == "":
            self._lit = ""
            self._num = 0
            return
        x: str = value.rstrip("0123456789")
        y: str = value[len(x) :]
        if x == "-":
            self._string_fset_minus(y)
            return
        x = x.lower()
        x = x.replace("-", ".")
        x = x.replace("_", ".")
        if x.endswith("."):
            x = x[:-1]
            if not y:
                raise ValueError
        if x.startswith("."):
            x = x[1:]
        if not x:
            raise ValueError
        self._lit = self._lit_parse(x)
        self._num = int("0" + y)

    @abstractmethod
    def _string_fset_minus(self: Self, value: str) -> None: ...

    @property
    def num(self: Self) -> int:
        return self._num

    @num.setter
    @guard
    def num(self: Self, value: SupportsIndex) -> None:
        y: int = operator.index(value)
        if y < 0:
            raise ValueError
        if y and not self.lit:
            self.string = y
        else:
            self._num = y

    @property
    def lit(self: Self) -> str:
        return self._lit

    @lit.setter
    @guard
    def lit(self: Self, value: Any) -> None:
        x: str = str(value).lower()
        if x:
            self._lit = self._lit_parse(x)
        elif self.num:
            self.string = self.num
        else:
            self._lit = ""
