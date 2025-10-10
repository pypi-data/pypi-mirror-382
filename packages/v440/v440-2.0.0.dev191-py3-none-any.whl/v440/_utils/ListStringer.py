import collections
from abc import abstractmethod
from typing import *

import setdoc
from datarepr import datarepr

from v440._utils.BaseStringer import BaseStringer
from v440._utils.guarding import guard

__all__ = ["ListStringer"]


class ListStringer(BaseStringer, collections.abc.MutableSequence):

    __slots__ = ("_data",)
    data: tuple
    string: str

    @setdoc.basic
    def __add__(self: Self, other: Any) -> Self:
        alt: tuple
        try:
            alt = tuple(other)
        except Exception:
            return NotImplemented
        ans: Self = type(self)()
        ans.data = self.data + alt
        return ans

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.data)

    @setdoc.basic
    def __contains__(self: Self, other: Any) -> bool:
        return other in self.data

    @setdoc.basic
    def __delitem__(self: Self, key: Any) -> None:
        data: list = list(self.data)
        del data[key]
        self.data = data

    @setdoc.basic
    def __getitem__(self: Self, key: Any) -> Any:
        return self.data[key]

    @setdoc.basic
    def __iadd__(self: Self, other: Any, /) -> Self:
        self.data = self.data + tuple(other)
        return self

    @setdoc.basic
    def __imul__(self: Self, other: Any, /) -> Self:
        self.data = self.data * other
        return self

    @setdoc.basic
    def __iter__(self: Self) -> Iterator:
        return iter(self.data)

    @setdoc.basic
    def __len__(self: Self) -> int:
        return len(self.data)

    @setdoc.basic
    def __mul__(self: Self, other: Any) -> Self:
        ans: Self = type(self)()
        ans.data = self.data * other
        return ans

    @setdoc.basic
    def __radd__(self: Self, other: Any) -> Self:
        alt: tuple
        try:
            alt = tuple(other)
        except Exception:
            return NotImplemented
        ans: Self = type(self)()
        ans.data = alt + self.data
        return ans

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, list(self))

    @setdoc.basic
    def __reversed__(self: Self) -> reversed:
        return reversed(self.data)

    @setdoc.basic
    def __rmul__(self: Self, other: Any) -> Self:
        return self * other

    @setdoc.basic
    def __setitem__(self: Self, key: Any, value: Any) -> None:
        data: list = list(self.data)
        data[key] = value
        self.data = data

    def _cmp(self: Self) -> tuple:
        return tuple(map(self._sort, self.data))

    @classmethod
    @abstractmethod
    def _data_parse(cls: type, value: list) -> Iterable: ...

    @classmethod
    @abstractmethod
    def _sort(cls: type, value: Any): ...

    def append(self: Self, value: Self, /) -> None:
        "This method appends value to self."
        data: list = list(self.data)
        data.append(value)
        self.data = data

    def clear(self: Self) -> None:
        "This method clears the data."
        self.data = ()

    def count(self: Self, value: Any) -> int:
        "This method counts the occurences of value."
        return self.data.count(value)

    @property
    @setdoc.basic
    def data(self: Self) -> tuple:
        return self._data

    @data.setter
    @guard
    def data(self: Self, value: Iterable) -> None:
        self._data = tuple(self._data_parse(list(value)))

    def extend(self: Self, value: Self, /) -> None:
        "This method extends self by value."
        data: list = list(self.data)
        data.extend(value)
        self.data = data

    @setdoc.basic
    def index(self: Self, *args: Any) -> None:
        return self.data.index(*args)

    @setdoc.basic
    def insert(
        self: Self,
        index: SupportsIndex,
        value: Any,
        /,
    ) -> None:
        data: list = list(self.data)
        data.insert(index, value)
        self.data = data

    def pop(self: Self, index: SupportsIndex = -1, /) -> Any:
        "This method pops an item."
        data: list = list(self.data)
        ans: Any = data.pop(index)
        self.data = data
        return ans

    def remove(self: Self, value: Any, /) -> None:
        "This method removes the first occurence of value."
        data: list = list(self.data)
        data.remove(value)
        self.data = data

    def reverse(self: Self) -> None:
        "This method reverses the order of the data."
        data: list = list(self.data)
        data.reverse()
        self.data = data

    def sort(self: Self, *, key: Any = None, reverse: Any = False) -> None:
        "This method sorts the data."
        data: list = list(self.data)
        k: Any = self._sort if key is None else key
        r: bool = bool(reverse)
        data.sort(key=k, reverse=r)
        self.data = data
