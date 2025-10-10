from abc import ABCMeta, abstractmethod
from typing import *

import setdoc
import unhash

from v440._utils.guarding import guard

__all__ = ["BaseStringer"]


class BaseStringer(metaclass=ABCMeta):
    __slots__ = ()

    string: str

    @abstractmethod
    @setdoc.basic
    def __bool__(self: Self) -> bool: ...

    @setdoc.basic
    def __eq__(self: Self, other: Any) -> bool:
        if type(self) is type(other):
            return self._cmp() == other._cmp()
        else:
            return False

    @setdoc.basic
    def __format__(self: Self, format_spec: Any) -> str:
        try:
            return self._format(str(format_spec))
        except Exception:
            msg: str = "Invalid format specifier %r for object of type %r"
            msg %= (format_spec, type(self).__name__)
            raise TypeError(msg) from None

    @setdoc.basic
    def __ge__(self: Self, other: Any) -> bool:
        if type(self) is type(other):
            return self._cmp() >= other._cmp()
        else:
            return NotImplemented

    @setdoc.basic
    def __gt__(self: Self, other: Any) -> bool:
        if type(self) is type(other):
            return self._cmp() > other._cmp()
        else:
            return NotImplemented

    __hash__ = unhash

    @abstractmethod
    @setdoc.basic
    def __init__(self: Self, string: Any) -> None: ...

    @setdoc.basic
    def __le__(self: Self, other: Any) -> bool:
        if type(self) is type(other):
            return self._cmp() <= other._cmp()
        else:
            return NotImplemented

    @setdoc.basic
    def __lt__(self: Self, other: Any) -> bool:
        if type(self) is type(other):
            return self._cmp() < other._cmp()
        else:
            return NotImplemented

    @setdoc.basic
    def __ne__(self: Self, other: Any) -> bool:
        return not (self == other)

    @abstractmethod
    @setdoc.basic
    def __repr__(self: Self) -> str: ...

    @classmethod
    def __subclasshook__(cls: type, other: type, /) -> bool:
        "This magic classmethod can be overwritten for a custom subclass check."
        return NotImplemented

    @setdoc.basic
    def __str__(self: Self) -> str:
        return self._format("")

    @abstractmethod
    def _cmp(self: Self) -> Any: ...

    @abstractmethod
    def _format(self: Self, format_spec: str) -> str: ...

    @abstractmethod
    def _string_fset(self: Self, value: str) -> None: ...

    @setdoc.basic
    def copy(self: Self) -> Self:
        return type(self)(self)

    @property
    def string(self: Self) -> str:
        "This property represents self as str."
        return self._format("")

    @string.setter
    @guard
    def string(self: Self, value: Any) -> None:
        self._string_fset(str(value).lower())
