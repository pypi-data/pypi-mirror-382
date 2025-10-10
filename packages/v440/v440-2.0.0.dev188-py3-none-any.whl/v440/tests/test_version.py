import unittest
from typing import *

from v440.core.Local import Local
from v440.core.Qual import Qual
from v440.core.Version import Version
from v440.core.VersionError import VersionError


class TestVersionManipulation(unittest.TestCase):

    def test_version_modification(self: Self) -> None:
        # Create an instance of the v440.Version class
        v: Version = Version("1.2.3")

        # Modify individual parts of the version
        v.public.base.release.major = 2
        v.public.base.release.minor = 5
        v.public.qual.string = "beta.1"
        v.local.string = "local.7.dev"

        # Verify the expected output
        self.assertEqual(str(v), "2.5.3b1+local.7.dev")


class TestVersionLocal(unittest.TestCase):

    def test_version_operations(self: Self) -> None:
        v: Version = Version("1.2.3")
        backup: Local = v.local
        v.local = "local.1.2.3"
        self.assertEqual(str(v), "1.2.3+local.1.2.3")
        self.assertEqual(str(v.local), "local.1.2.3")
        v.local.append("extra")
        self.assertEqual(str(v), "1.2.3+local.1.2.3.extra")
        self.assertEqual(str(v.local), "local.1.2.3.extra")
        v.local.remove(1)
        self.assertEqual(str(v), "1.2.3+local.2.3.extra")
        self.assertEqual(str(v.local), "local.2.3.extra")
        self.assertEqual(v.local[0], "local")
        self.assertEqual(v.local[-1], "extra")
        v.local.sort()
        self.assertEqual(str(v), "1.2.3+extra.local.2.3")
        self.assertEqual(str(v.local), "extra.local.2.3")
        v.local.clear()
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(str(v.local), "")
        v.local = "reset.1.2"
        self.assertEqual(str(v), "1.2.3+reset.1.2")
        self.assertEqual(str(v.local), "reset.1.2")
        self.assertTrue(v.local is backup)


class TestPre(unittest.TestCase):

    def test_pre(self: Self) -> None:
        v: Version = Version("1.2.3")
        backup: Qual = v.public.qual

        # Initial version, no pre-release version
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(str(v.public.qual), "")

        # Set pre-release version to "a1"
        v.public.qual.string = "a1"
        self.assertEqual(str(v), "1.2.3a1")
        self.assertEqual(str(v.public.qual), "a1")

        # Modify pre-release phase to "preview"
        v.public.qual.pre.lit = "preview"
        self.assertEqual(str(v), "1.2.3rc1")
        self.assertEqual(str(v.public.qual), "rc1")

        # Modify subphase to "42"
        v.public.qual.pre.num = 42
        self.assertEqual(str(v), "1.2.3rc42")
        self.assertEqual(str(v.public.qual), "rc42")

        # Change phase to a formatted string "BeTa"
        v.public.qual.pre.lit = "BeTa"
        self.assertEqual(str(v), "1.2.3b42")
        self.assertEqual(str(v.public.qual), "b42")
        self.assertEqual(v.public.qual, backup)

        # Set pre-release to None
        v.public.qual.string = ""
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(str(v.public.qual), "")


class TestExample(unittest.TestCase):

    def test_example_1(self: Self) -> None:
        v: Version = Version("v1.0.0")
        self.assertEqual(str(v), "1")  # Initial version
        self.assertEqual(format(v, "03r"), "1.0.0")  # Initial version formatted

    def test_example_2(self: Self) -> None:
        v: Version = Version("2.5.3")
        self.assertEqual(str(v), "2.5.3")  # Modified version
        v.public.base.release[1] = 64
        v.public.base.release.micro = 4
        self.assertEqual(str(v), "2.64.4")  # Further modified version

    def test_example_3(self: Self) -> None:
        v1: Version = Version("1.6.3")
        v2: Version = Version("1.6.4")
        self.assertEqual(str(v1), "1.6.3")  # v1
        self.assertEqual(str(v2), "1.6.4")  # v2
        # eq
        self.assertFalse(v1 == v2)
        self.assertFalse(v2 == v1)
        self.assertFalse(v1 == str(v1))
        self.assertFalse(v2 == str(v2))
        self.assertTrue(v1 == v1)
        self.assertTrue(v2 == v2)
        self.assertFalse(str(v1) == v1)
        self.assertFalse(str(v2) == v2)
        # ne
        self.assertTrue(v1 != v2)
        self.assertTrue(v2 != v1)
        self.assertTrue(v1 != str(v1))
        self.assertTrue(v2 != str(v2))
        self.assertFalse(v1 != v1)
        self.assertFalse(v2 != v2)
        self.assertTrue(str(v1) != v1)
        self.assertTrue(str(v2) != v2)
        # ge
        self.assertFalse(v1 >= v2)
        self.assertTrue(v2 >= v1)
        with self.assertRaises(Exception):
            v1 >= str(v2)
        with self.assertRaises(Exception):
            str(v1) >= v2
        with self.assertRaises(Exception):
            v2 >= str(v1)
        with self.assertRaises(Exception):
            str(v2) >= v1
        # le
        self.assertFalse(v2 <= v1)
        self.assertTrue(v1 <= v2)
        with self.assertRaises(Exception):
            v1 <= str(v2)
        with self.assertRaises(Exception):
            str(v1) <= v2
        with self.assertRaises(Exception):
            v2 <= str(v1)
        with self.assertRaises(Exception):
            str(v2) <= v1
        # gt
        self.assertFalse(v1 > v2)
        self.assertTrue(v2 > v1)
        with self.assertRaises(Exception):
            v1 > str(v2)
        with self.assertRaises(Exception):
            str(v1) > v2
        with self.assertRaises(Exception):
            v2 > str(v1)
        with self.assertRaises(Exception):
            str(v2) > v1
        # lt
        self.assertFalse(v2 < v1)
        self.assertTrue(v1 < v2)
        with self.assertRaises(Exception):
            v1 < str(v2)
        with self.assertRaises(Exception):
            str(v1) < v2
        with self.assertRaises(Exception):
            v2 < str(v1)
        with self.assertRaises(Exception):
            str(v2) < v1

    def test_example_4(self: Self) -> None:
        v: Version = Version("2.5.3.9")
        self.assertEqual(str(v), "2.5.3.9")  # before sorting
        v.public.base.release.sort()
        self.assertEqual(str(v), "2.3.5.9")  # after sorting

    def test_example_5(self: Self) -> None:
        v: Version = Version("2.0.0-alpha.1")
        self.assertEqual(str(v), "2a1")  # Pre-release version
        v.public.qual.pre.string = "beta.2"
        self.assertEqual(str(v), "2b2")  # Modified pre-release version
        with self.assertRaises(Exception):
            v.public.qual.pre[1] = 4
        self.assertEqual(str(v), "2b2")  # Further modified pre-release version
        v.public.qual.pre.lit = "PrEvIeW"
        self.assertEqual(str(v), "2rc2")  # Even further modified pre-release version

    def test_example_6(self: Self) -> None:
        v: Version = Version("1.2.3")
        v.public.qual.post.string = -1
        v.local.string = "local.7.dev"
        self.assertEqual(str(v), "1.2.3.post1+local.7.dev")  # Post-release version
        self.assertEqual(
            format(v, "02r"), "1.2.3.post1+local.7.dev"
        )  # Formatted version
        v.public.qual.post.string = -2
        self.assertEqual(str(v), "1.2.3.post2+local.7.dev")  # Modified version
        v.public.qual.post.string = ""
        self.assertEqual(str(v), "1.2.3+local.7.dev")  # Modified without post
        v.public.qual.post.string = -3
        v.local.sort()
        self.assertEqual(str(v), "1.2.3.post3+dev.local.7")  # After sorting local
        v.local.append(8)
        self.assertEqual(str(v), "1.2.3.post3+dev.local.7.8")  # Modified with new local
        v.local.string = "3.test.19"
        self.assertEqual(str(v), "1.2.3.post3+3.test.19")  # Modified local again

    def test_example_7(self: Self) -> None:
        v: Version = Version("5.0.0")
        self.assertEqual(str(v), "5")  # Original version
        v.string = ""
        self.assertEqual(str(v), "0")  # After reset
        v.public.base.string = "4!5.0.1"
        self.assertEqual(str(v), "4!5.0.1")  # Before error
        with self.assertRaises(VersionError):
            v.public.base.string = "9!x"
        self.assertEqual(str(v), "4!5.0.1")  # After error


class TestPatch(unittest.TestCase):
    def test_example_0(self: Self) -> None:
        x: Qual = Qual("a1")
        y: Qual = Qual("b2")
        with self.assertRaises(Exception):
            x += y


class TestVersionRelease(unittest.TestCase):

    def test_major_minor_micro_aliases(self: Self) -> None:
        # Test major, minor, and micro aliases for the first three indices
        version: Version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertEqual(version.public.base.release.major, 1)
        self.assertEqual(version.public.base.release.minor, 2)
        self.assertEqual(version.public.base.release.micro, 3)
        self.assertEqual(
            version.public.base.release.patch, 3
        )  # 'patch' is an alias for micro

    def test_release_modify_aliases(self: Self) -> None:
        # Test modifying the release via major, minor, and micro properties
        version: Version = Version()
        version.public.base.release.data = [1, 2, 3]
        version.public.base.release.major = 10
        version.public.base.release.minor = 20
        version.public.base.release.micro = 30
        self.assertEqual(list(version.public.base.release), [10, 20, 30])
        self.assertEqual(version.public.base.release.patch, 30)

    def test_release_with_tailing_zeros_simulation(self: Self) -> None:
        # Test that the release can simulate arbitrary high number of tailing zeros
        version: Version = Version()
        version.public.base.release.data = [1, 2]
        simulated_release = version.public.base.release[:5]
        self.assertEqual(simulated_release, [1, 2, 0, 0, 0])

    def test_release_empty_major(self: Self) -> None:
        # Test that an empty release still has valid major, minor, micro values
        version: Version = Version()
        version.public.base.release.data = []
        self.assertEqual(version.public.base.release.major, 0)
        self.assertEqual(version.public.base.release.minor, 0)
        self.assertEqual(version.public.base.release.micro, 0)
        self.assertEqual(version.public.base.release.patch, 0)


class TestAdditionalVersionRelease(unittest.TestCase):

    def test_release_inequality_with_list(self: Self) -> None:
        # Test inequality of release with a normal list
        version: Version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertFalse(version.public.base.release == [1, 2, 4])

    def test_release_len(self: Self) -> None:
        # Test the length of the release list
        version: Version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertEqual(len(version.public.base.release), 3)

    def test_release_slice_assignment(self: Self) -> None:
        # Test assigning a slice to release
        version: Version = Version()
        version.public.base.release.data = [1, 2, 3, 4, 5]
        version.public.base.release[1:4] = [20, 30, 40]
        self.assertEqual(
            list(version.public.base.release),
            [1, 20, 30, 40, 5],
        )

    def test_release_iterable(self: Self) -> None:
        # Test if release supports iteration
        version: Version = Version()
        version.public.base.release.data = [1, 2, 3]
        result = list(version.public.base.release)
        self.assertEqual(result, [1, 2, 3])

    def test_release_repr(self: Self) -> None:
        # Test the repr of the release property
        version: Version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertEqual(str(version.public.base.release), "1.2.3")

    def test_release_data_property(self: Self) -> None:
        # Test the 'data' property
        version: Version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertEqual(version.public.base.release.data, (1, 2, 3))

    def test_release_data_setter(self: Self) -> None:
        # Test setting the 'data' property directly
        version: Version = Version()
        version.public.base.release.data = [10, 20, 30]
        self.assertEqual(list(version.public.base.release), [10, 20, 30])

    def test_release_contains(self: Self) -> None:
        # Test 'in' keyword with release
        version: Version = Version()
        version.public.base.release.data = [1, 2, 3]
        self.assertIn(2, version.public.base.release)
        self.assertNotIn(4, version.public.base.release)

    def test_release_mul(self: Self) -> None:
        # Test multiplying the release (list behavior)
        version: Version = Version()
        version.public.base.release.data = [1, 2]
        answer: list = list(version.public.base.release * 3)
        solution: list = [1, 2, 1, 2, 1, 2]
        self.assertEqual(answer, solution)

    def test_release_addition(self: Self) -> None:
        # Test adding another list to release
        version: Version = Version()
        version.public.base.release.data = [1, 2, 3]
        answer: list = list(version.public.base.release) + [4, 5]
        solution: list = [1, 2, 3, 4, 5]
        self.assertEqual(answer, solution)


class TestVersionLocal(unittest.TestCase):

    def test_local_len(self: Self) -> None:
        # Test the length of the local list
        version: Version = Version()
        version.local.data = [1, "dev", "build"]
        self.assertEqual(len(version.local), 3)

    def test_local_slice_assignment(self: Self) -> None:
        # Test assigning a slice to the local list
        version: Version = Version()
        version.local.data = [1, "dev", "build"]
        version.local[1:3] = ["alpha", "beta"]
        self.assertEqual(list(version.local), [1, "alpha", "beta"])

    def test_local_contains(self: Self) -> None:
        # Test 'in' keyword with local list
        version: Version = Version()
        version.local.data = [1, "dev", "build"]
        self.assertIn("dev", version.local)
        self.assertNotIn("alpha", version.local)

    def test_local_mul(self: Self) -> None:
        # Test multiplying the local list
        version: Version = Version()
        version.local.data = [1, "dev"]
        answer: list = list(version.local * 3)
        solution: list = [1, "dev", 1, "dev", 1, "dev"]
        self.assertEqual(answer, solution)

    def test_local_addition(self: Self) -> None:
        # Test adding another list to local
        version: Version = Version()
        version.local.data = [1, "dev"]
        answer: list = list(version.local + ["build"])
        solution: list = [1, "dev", "build"]
        self.assertEqual(answer, solution)

    def test_local_inequality_with_list(self: Self) -> None:
        # Test inequality of local with a normal list
        version: Version = Version()
        version.local.data = [1, "dev"]
        self.assertFalse(version.local == [1, "build"])

    def test_local_repr(self: Self) -> None:
        # Test repr of local list
        version: Version = Version()
        version.local.data = [1, "dev", "build"]
        self.assertEqual(str(version.local), "1.dev.build")

    def test_local_data_property(self: Self) -> None:
        # Test that 'data' property correctly reflects local's internal list
        version: Version = Version()
        version.local.data = [1, "dev", "build"]
        self.assertEqual(version.local.data, (1, "dev", "build"))

    def test_local_data_setter(self: Self) -> None:
        # Test that 'data' property can be set directly
        version: Version = Version()
        version.local.data = ["custom", "data"]
        answer: list = list(version.local)
        solution: list = ["custom", "data"]
        self.assertEqual(answer, solution)

    def test_local_iterable(self: Self) -> None:
        # Test if local supports iteration
        version: Version = Version()
        version.local.string = "1.dev.build"
        result: list = list(version.local)
        self.assertEqual(result, [1, "dev", "build"])


class TestSlicingNoGo(unittest.TestCase):

    def test_slicing_2(self: Self) -> None:
        v: Version = Version("1.2.3.4.5.6.7.8.9.10")
        with self.assertRaises(Exception):
            v.public.base.release[-8:15:5] = 777

    def test_slicing_7(self: Self) -> None:
        v: Version = Version("1.2.3.4.5.6.7.8.9.10")
        del v.public.base.release[-8:15:5]
        self.assertEqual(str(v), "1.2.4.5.6.7.9.10")


class TestDevNoGo(unittest.TestCase):

    def test_initial_none_dev(self: Self) -> None:
        v: Version = Version("1.2.3")
        self.assertEqual(str(v), "1.2.3")
        self.assertFalse(v.public.qual.dev)

    def test_dev_as_none(self: Self) -> None:
        v: Version = Version("1.2.3")
        v.public.qual.dev.string = ""
        self.assertEqual(str(v), "1.2.3")
        self.assertFalse(v.public.qual.dev)


if __name__ == "__main__":
    unittest.main()
