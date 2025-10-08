from abc import abstractmethod
from typing import *

import setdoc
from datarepr import datarepr

from v440._utils.BaseStringer import BaseStringer

__all__ = ["SlotStringer"]


class SlotStringer(BaseStringer):
    __slots__ = ()

    string: str

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, **self._todict())

    @abstractmethod
    def _todict(self: Self) -> dict: ...
