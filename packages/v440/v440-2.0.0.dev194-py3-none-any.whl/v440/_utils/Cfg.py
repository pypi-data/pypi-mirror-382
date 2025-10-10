import enum
import functools
import tomllib
from importlib import resources
from typing import *


class Cfg(enum.Enum):
    cfg = None

    @functools.cached_property
    def data(self: Self) -> dict:
        "This cached property holds the cfg data."
        text: str = resources.read_text("v440._utils", "cfg.toml")
        ans: dict = tomllib.loads(text)
        return ans
