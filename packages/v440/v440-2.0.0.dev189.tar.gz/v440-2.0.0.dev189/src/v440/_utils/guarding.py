from __future__ import annotations

import functools
from typing import *

from v440.core.VersionError import VersionError


def guard(old: Any) -> Any:
    @functools.wraps(old)
    def new(self: Self, value: Any) -> None:
        backup: str = str(self)
        try:
            old(self, value)
        except VersionError:
            self.string = backup
            raise
        except Exception:
            self.string = backup
            msg: str = "%r is an invalid value for %r"
            target: str = type(self).__name__ + "." + old.__name__
            msg %= (value, target)
            raise VersionError(msg)

    return new
