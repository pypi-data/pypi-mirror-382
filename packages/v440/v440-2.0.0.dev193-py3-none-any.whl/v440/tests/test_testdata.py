import enum
import functools
import operator
import tomllib
import unittest
from importlib import resources
from typing import *

import iterprod
import packaging.version

from v440 import core
from v440.core.Release import Release
from v440.core.Version import Version
from v440.core.VersionError import VersionError


class Util(enum.Enum):
    util = None

    @functools.cached_property
    def data(self: Self) -> dict:
        text: str = resources.read_text("v440.tests", "testdata.toml")
        data: dict = tomllib.loads(text)
        return data


class TestVersionReleaseAttrs(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["release-data"].items():
            with self.subTest(key=k):
                self.go_data(**v)

    def go_data(
        self: Self,
        query: list,
        attrname: Optional[str] = None,
        args: list | tuple = (),
        kwargs: dict | tuple = (),
        target: Optional[list] = None,
        solution: Any = None,
        queryname: str = "data",
    ) -> None:
        # Test the append method of the release list-like object
        version: Version = Version()
        setattr(version.public.base.release, queryname, query)
        if attrname is not None:
            attr: Any = getattr(version.public.base.release, attrname)
            ans: Any = attr(*args, **dict(kwargs))
            self.assertEqual(ans, solution)
        if target is not None:
            ans: list = list(version.public.base.release)
            self.assertEqual(ans, target)


class TestVersionReleaseVersionError(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["release-VersionError"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        query: list,
    ) -> None:
        version: Version = Version()
        with self.assertRaises(VersionError):
            version.public.base.release.data = query


class TestVersionLocalVersionError(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["local-VersionError"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        query: list,
    ) -> None:
        version: Version = Version()
        with self.assertRaises(VersionError):
            version.local.data = query


class TestVersionLocalGo(unittest.TestCase):
    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["local-attr"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        query: list,
        attrname: Optional[str] = None,
        args: list | tuple = (),
        kwargs: dict | tuple = (),
        target: Optional[list] = None,
        solution: Any = None,
    ) -> None:
        version: Version = Version()
        version.local.data = query
        if attrname is not None:
            attr: Any = getattr(version.local, attrname)
            ans: Any = attr(*args, **dict(kwargs))
            self.assertEqual(ans, solution)
        if target is not None:
            answer: list = list(version.local)
            self.assertEqual(answer, target)


class TestVersionEpochGo(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["epoch"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        full: Any,
        part: Any,
        query: Any = None,
        key: str = "",
    ) -> None:
        msg: str = "epoch %r" % key
        v: Version = Version("1.2.3")
        v.public.base.epoch = query
        self.assertEqual(str(v), full, msg=msg)
        self.assertIsInstance(v.public.base.epoch, int, msg=msg)
        self.assertEqual(v.public.base.epoch, part, msg=msg)


class TestSlicingGo(unittest.TestCase):
    def test_0(self: Self) -> None:
        sli: dict = Util.util.data["slicingmethod"]
        k: str
        v: dict
        for k, v in sli.items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        query: Any,
        change: Any,
        solution: str,
        start: Any = None,
        stop: Any = None,
        step: Any = None,
    ) -> None:
        v: Version = Version(query)
        v.public.base.release[start:stop:step] = change
        self.assertEqual(str(v), solution)


class TestDataProperty(unittest.TestCase):
    def test_0(self: Self) -> None:
        for k, v in Util.util.data["data-property"].items():
            with self.subTest(key=k):
                self.go(**v, key=k)

    def go(
        self: Self,
        query: Any = None,
        solution: Any = None,
        key: str = "",
    ) -> None:
        msg: str = "data-property %r" % key
        version: Version = Version()
        version.string = query
        self.assertEqual(solution, str(version), msg=msg)


class TestVersionRelease(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["release"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(self: Self, query: list, solution: list) -> None:
        release: Release = Release()
        release.data = query
        self.assertEqual(list(release), solution)


class TestVersionSpecifiersGo(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["spec"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(self: Self, string_a: str, string_b: str) -> None:
        version: Version = Version(string_a)
        self.assertEqual(str(version), string_b)


class TestPackagingA(unittest.TestCase):
    def test_0(self: Self) -> None:
        s: str
        x: str
        y: list
        for x, y in Util.util.data["strings"]["valid"].items():
            for s in y:
                with self.subTest(key=x):
                    self.go(text=s)

    def go(self: Self, text: str) -> None:
        a: packaging.version.Version = packaging.version.Version(text)
        b: str = str(a)
        f: str = "0%sr" % len(a.release)
        g: str = format(Version(text), f)
        self.assertEqual(b, g)


class TestPackagingB(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: str
        y: list
        for x, y in Util.util.data["strings"]["valid"].items():
            with self.subTest(key=x):
                self.go(y)

    def go(self: Self, y: list) -> None:
        a: packaging.version.Version
        b: packaging.version.Version
        s: str
        msg: str
        for s in y:
            a = packaging.version.Version(s)
            b = Version(s).packaging()
            msg = f"{s} should match packaging.version.Version"
            self.assertEqual(a, b, msg=msg)


class TestPackagingC(unittest.TestCase):
    def test_0(self: Self) -> None:
        pure: list = list()
        part: list
        for part in Util.util.data["strings"]["valid"].values():
            pure += part
        ops: list = [
            operator.eq,
            operator.ne,
            operator.gt,
            operator.ge,
            operator.le,
            operator.lt,
        ]
        args: tuple
        for args in iterprod.iterprod(pure, pure, ops):
            with self.subTest(args=args):
                self.go(*args)

    def go(self: Self, x: str, y: str, func: Callable, /) -> None:
        a: packaging.version.Version = packaging.version.Version(x)
        b: packaging.version.Version = Version(string=x).packaging()
        c: packaging.version.Version = packaging.version.Version(y)
        d: packaging.version.Version = Version(string=y).packaging()
        native: bool = func(a, c)
        convert: bool = func(b, d)
        msg: str = f"{func} should match for {x!r} and {y!r}"
        self.assertEqual(native, convert, msg=msg)


class TestPackagingField(unittest.TestCase):
    def test_0(self: Self) -> None:
        k: str
        l: list
        for k, l in Util.util.data["strings"]["valid"].items():
            with self.subTest(key=k):
                self.go_list(l)

    def go_list(self: Self, listing: list) -> None:
        x: str
        for x in listing:
            with self.subTest():
                self.go(query=x)

    def go(self: Self, query: str) -> None:
        msg: str = "query=%r" % query
        v: Version = Version(query)
        self.assertEqual(
            v.public.qual.isdevrelease(),
            v.packaging().is_devrelease,
            msg=msg,
        )
        self.assertEqual(
            v.public.qual.isprerelease(),
            v.packaging().is_prerelease,
            msg=msg,
        )
        self.assertEqual(
            v.public.qual.ispostrelease(),
            v.packaging().is_postrelease,
            msg=msg,
        )
        self.assertEqual(
            str(v.public.base),
            v.packaging().base_version,
            msg=msg,
        )
        self.assertEqual(
            str(v.public),
            v.packaging().public,
            msg=msg,
        )
        local_packaging: Optional[str] = v.packaging().local
        if local_packaging is None:
            local_packaging = ""
        self.assertEqual(
            str(v.local),
            str(local_packaging),
            msg=msg,
        )


class TestPackagingExc(unittest.TestCase):
    def test_0(self: Self) -> None:
        k: str
        l: list
        for k, l in Util.util.data["strings"]["exc"].items():
            with self.subTest(key=k):
                self.go_list(l)

    def go_list(self: Self, impure: list, /) -> None:
        x: str
        for x in impure:
            with self.assertRaises(packaging.version.InvalidVersion):
                packaging.version.Version(x)


class TestExc(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: str
        y: list
        for x, y in Util.util.data["strings"]["exc"].items():
            with self.subTest(test_label=x):
                self.go(queries=y)

    def go(self: Self, queries: list) -> None:
        x: str
        for x in queries:
            with self.assertRaises(VersionError):
                Version(x)


class TestSlots(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: Any
        y: Any
        for x, y in Util.util.data["core-non-attributes"].items():
            with self.subTest(test_label=x):
                self.go(**y)

    def go(
        self: Self,
        clsname: str,
        attrname: str,
        attrvalue: Any,
        string: Any = None,
        isimported: Optional[bool] = False,
    ) -> None:
        cls: type
        if isimported:
            cls = getattr(core, clsname)
        else:
            cls = getattr(getattr(core, clsname), clsname)
        obj: Any = cls(string=string)
        with self.assertRaises(AttributeError):
            setattr(obj, attrname, attrvalue)


class TestReleaseAlias(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: Any
        y: Any
        for x, y in Util.util.data["release-key"].items():
            with self.subTest(test_label=x):
                self.go(**y)

    def go(self: Self, steps: list) -> None:
        version: Version = Version()
        step: dict
        for step in steps:
            self.modify(version=version, **step)

    def modify(
        self: Self,
        version: Version,
        name: str,
        value: Any,
        solution: Optional[list] = None,
    ) -> None:
        setattr(version.public.base.release, name, value)
        if solution is None:
            return
        answer: list = list(version.public.base.release)
        self.assertEqual(answer, solution)


if __name__ == "__main__":
    unittest.main()
