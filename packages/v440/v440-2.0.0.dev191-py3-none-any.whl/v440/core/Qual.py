from __future__ import annotations

from typing import *

import setdoc

from v440._utils.Pattern import Pattern
from v440._utils.SlotStringer import SlotStringer
from v440.core.Dev import Dev
from v440.core.Post import Post
from v440.core.Pre import Pre

__all__ = ["Qual"]


class Qual(SlotStringer):

    __slots__ = ("_pre", "_post", "_dev")
    string: str
    pre: Pre
    post: Post
    dev: Dev

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.pre or self.post or self.dev)

    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self._pre = Pre()
        self._post = Post()
        self._dev = Dev()
        self.string = string

    def _cmp(self: Self) -> tuple:
        ans: tuple = ()
        if self.pre:
            ans += (self.pre.lit, self.pre.num)
        elif self.post is not None:
            ans += ("z", 0)
        elif self.dev is None:
            ans += ("z", 0)
        else:
            ans += ("", 0)
        ans += (self.post, self.dev)
        return ans

    def _format(self: Self, format_spec: str) -> str:
        if format_spec:
            raise ValueError
        ans: str = str(self.pre)
        if self.post:
            ans += "." + str(self.post)
        if self.dev:
            ans += "." + str(self.dev)
        return ans

    @classmethod
    def _none_empty(cls: type, value: Optional[str]) -> str:
        if value is None:
            return ""
        else:
            return value

    def _string_fset(self: Self, value: str) -> None:
        m: Any = Pattern.QUAL.bound.search(value.lower())
        self.pre.string = self._none_empty(m.group("pre"))
        self.post.string = self._none_empty(m.group("post"))
        self.dev.string = self._none_empty(m.group("dev"))

    def _todict(self: Self) -> dict:
        return dict(pre=self.pre, post=self.post, dev=self.dev)

    @property
    def dev(self: Self) -> Dev:
        "This property represents the stage of development."
        return self._dev

    def isdevrelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a dev-release."
        return bool(self.dev)

    def isprerelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a pre-release."
        return bool(self.pre) or bool(self.dev)

    def ispostrelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a post-release."
        return bool(self.post)

    @property
    def post(self: Self) -> Post:
        return self._post

    @property
    def pre(self: Self) -> Pre:
        return self._pre
