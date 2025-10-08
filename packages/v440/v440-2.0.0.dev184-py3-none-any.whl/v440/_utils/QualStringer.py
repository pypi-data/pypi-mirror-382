import operator
from abc import abstractmethod
from typing import *

import setdoc
from datarepr import datarepr
from overloadable import Overloadable

from v440._utils.BaseStringer import BaseStringer
from v440._utils.guarding import guard

__all__ = ["QualStringer"]


class QualStringer(BaseStringer):
    __slots__ = ("_phase", "_num")

    string: str
    phase: str
    num: int

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return self.phase != ""

    @Overloadable
    @setdoc.basic
    def __init__(self: Self, *args: Any, **kwargs: Any) -> str:
        self._phase = ""
        self._num = 0
        argc: int = len(args) + len(kwargs)
        keys: set = set(kwargs.keys())
        if argc <= 1 and keys <= {"string"}:
            return "string"
        return "slots"

    @__init__.overload("string")
    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self.string = string

    @__init__.overload("slots")
    @setdoc.basic
    def __init__(
        self: Self,
        phase: Any = "",
        num: Any = 0,
    ) -> None:
        self.phase = phase
        self.num = num

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(
            type(self).__name__,
            phase=self.phase,
            num=self.num,
        )

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        if self.phase:
            return self.phase + str(self.num)
        else:
            return ""

    @classmethod
    @abstractmethod
    def _phase_parse(cls: type, value: str) -> str: ...

    def _string_fset(self: Self, value: str) -> None:
        if value == "":
            self._phase = ""
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
        self._phase = self._phase_parse(x)
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
        if y and not self.phase:
            self.string = y
        else:
            self._num = y

    @property
    def phase(self: Self) -> str:
        return self._phase

    @phase.setter
    @guard
    def phase(self: Self, value: Any) -> None:
        x: str = str(value).lower()
        if x:
            self._phase = self._phase_parse(x)
        elif self.num:
            self.string = self.num
        else:
            self._phase = ""
