# noqa pylint: skip-file
"""
Semantic versioning utilities for the Fiddler Evals SDK.

This module provides a comprehensive implementation of semantic versioning
(SemVer) specification, including version parsing, comparison, and validation.
It supports the full SemVer 2.0.0 specification including prerelease and
build metadata.

The main class is VersionInfo, which represents a semantic version and provides
methods for comparison, parsing, and string representation.

Copyright (c) 2013, Konstantine Rybnikov
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

  Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

  Neither the name of the {organization} nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import annotations

import collections
import re
from functools import wraps
from typing import Generator, no_type_check

string_types = str, bytes
text_type = str
binary_type = bytes


def cmp(a: int, b: int) -> int:
    """Return negative if a<b, zero if a==b, positive if a>b."""
    return (a > b) - (a < b)


@no_type_check
def comparator(operator: None) -> None:
    """Wrap a VersionInfo binary op method in a type-check."""

    @wraps(operator)
    def wrapper(self, other):
        """Perform type checking before calling the operator.

        :param self: The VersionInfo instance
        :param other: The object to compare with
        :return: The result of the operator function
        :raises TypeError: If other is not a comparable type
        """
        comparable_types = (VersionInfo, dict, tuple, list, text_type, binary_type)
        if not isinstance(other, comparable_types):
            raise TypeError(
                "other type {!r} must be in {!r}".format(type(other), comparable_types)
            )
        return operator(self, other)

    return wrapper


class VersionInfo:
    """
    A semver compatible version class.

    :param int major: version when you make incompatible API changes.
    :param int minor: version when you add functionality in
                      a backwards-compatible manner.
    :param int patch: version when you make backwards-compatible bug fixes.
    :param str prerelease: an optional prerelease string
    :param str build: an optional build string
    """

    __slots__ = ("_major", "_minor", "_patch", "_prerelease", "_build")
    #: Regex for number in a prerelease
    _LAST_NUMBER = re.compile(r"(?:[^\d]*(\d+)[^\d]*)+")
    #: Regex for a semver version
    _REGEX = re.compile(
        r"""
            ^
            (?P<major>0|[1-9]\d*)
            \.
            (?P<minor>0|[1-9]\d*)
            \.
            (?P<patch>0|[1-9]\d*)
            (?:-(?P<prerelease>
                (?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)
                (?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*
            ))?
            (?:\+(?P<build>
                [0-9a-zA-Z-]+
                (?:\.[0-9a-zA-Z-]+)*
            ))?
            $
        """,
        re.VERBOSE,
    )

    def __init__(
        self,
        major: int,
        minor: int = 0,
        patch: int = 0,
        prerelease: str = "",
        build: str = "",
    ) -> None:
        """Initialize a VersionInfo instance.

        :param int major: version when you make incompatible API changes
        :param int minor: version when you add functionality in a backwards-compatible manner
        :param int patch: version when you make backwards-compatible bug fixes
        :param str prerelease: an optional prerelease string
        :param str build: an optional build string
        :raises ValueError: if any version part is negative
        """
        # Build a dictionary of the arguments except prerelease and build
        version_parts = {
            "major": major,
            "minor": minor,
            "patch": patch,
        }

        for name, value in version_parts.items():
            value = int(value)
            version_parts[name] = value
            if value < 0:
                raise ValueError(
                    "{!r} is negative. A version can only be positive.".format(name)
                )

        self._major = version_parts["major"]
        self._minor = version_parts["minor"]
        self._patch = version_parts["patch"]
        self._prerelease = None if prerelease is None else str(prerelease)
        self._build = None if build is None else str(build)

    @property
    def major(self) -> int:
        """The major part of a version (read-only)."""
        return self._major

    @major.setter
    def major(self, value: str) -> None:
        """Prevent modification of the major version.

        :param value: The value being assigned (ignored)
        :raises AttributeError: always raised to prevent modification
        """
        raise AttributeError("attribute 'major' is readonly")

    @property
    def minor(self) -> int:
        """The minor part of a version (read-only)."""
        return self._minor

    @minor.setter
    def minor(self, value: str) -> None:
        """Prevent modification of the minor version.

        :param value: The value being assigned (ignored)
        :raises AttributeError: always raised to prevent modification
        """
        raise AttributeError("attribute 'minor' is readonly")

    @property
    def patch(self) -> int:
        """The patch part of a version (read-only)."""
        return self._patch

    @patch.setter
    def patch(self, value: str) -> None:
        """Prevent modification of the patch version.

        :param value: The value being assigned (ignored)
        :raises AttributeError: always raised to prevent modification
        """
        raise AttributeError("attribute 'patch' is readonly")

    @property
    def prerelease(self) -> str:
        """The prerelease part of a version (read-only)."""
        return self._prerelease

    @prerelease.setter
    def prerelease(self, value: str) -> None:
        """Prevent modification of the prerelease string.

        :param value: The value being assigned (ignored)
        :raises AttributeError: always raised to prevent modification
        """
        raise AttributeError("attribute 'prerelease' is readonly")

    @property
    def build(self) -> str:
        """The build part of a version (read-only)."""
        return self._build

    @build.setter
    def build(self, value: str) -> None:
        """Prevent modification of the build string.

        :param value: The value being assigned (ignored)
        :raises AttributeError: always raised to prevent modification
        """
        raise AttributeError("attribute 'build' is readonly")

    def to_tuple(self) -> tuple[int, int, int, str, str]:
        """
        Convert the VersionInfo object to a tuple.

        .. versionadded:: 2.10.0
           Renamed ``VersionInfo._astuple`` to ``VersionInfo.to_tuple`` to
           make this function available in the public API.

        :return: a tuple with all the parts
        :rtype: tuple

        >>> semver.VersionInfo(5, 3, 1).to_tuple()
        (5, 3, 1, None, None)
        """
        return (self.major, self.minor, self.patch, self.prerelease, self.build)

    def to_dict(self) -> dict:
        """
        Convert the VersionInfo object to an OrderedDict.

        .. versionadded:: 2.10.0
           Renamed ``VersionInfo._asdict`` to ``VersionInfo.to_dict`` to
           make this function available in the public API.

        :return: an OrderedDict with the keys in the order ``major``, ``minor``,
          ``patch``, ``prerelease``, and ``build``.
        :rtype: :class:`collections.OrderedDict`

        >>> semver.VersionInfo(3, 2, 1).to_dict()
        OrderedDict([('major', 3), ('minor', 2), ('patch', 1), \
('prerelease', None), ('build', None)])
        """
        return collections.OrderedDict(
            (
                ("major", self.major),
                ("minor", self.minor),
                ("patch", self.patch),
                ("prerelease", self.prerelease),
                ("build", self.build),
            )
        )

    def __iter__(self) -> Generator[tuple, None, None]:
        """Implement iter(self)."""
        # As long as we support Py2.7, we can't use the "yield from" syntax
        yield from self.to_tuple()  # type: ignore

    @staticmethod
    def _increment_string(string: str) -> str:
        """
        Look for the last sequence of number(s) in a string and increment.

        :param str string: the string to search for.
        :return: the incremented string

        Source:
        http://code.activestate.com/recipes/442460-increment-numbers-in-a-string/#c1
        """
        match = VersionInfo._LAST_NUMBER.search(string)
        if match:
            next_ = str(int(match.group(1)) + 1)
            start, end = match.span(1)
            string = string[: max(end - len(next_), start)] + next_ + string[end:]
        return string

    def compare(self, other) -> int:  # type: ignore
        """
        Compare self with other.

        :param other: the second version (can be string, a dict, tuple/list, or
             a VersionInfo instance)
        :return: The return value is negative if ver1 < ver2,
             zero if ver1 == ver2 and strictly positive if ver1 > ver2
        :rtype: int

        >>> semver.VersionInfo.parse("1.0.0").compare("2.0.0")
        -1
        >>> semver.VersionInfo.parse("2.0.0").compare("1.0.0")
        1
        >>> semver.VersionInfo.parse("2.0.0").compare("2.0.0")
        0
        >>> semver.VersionInfo.parse("2.0.0").compare(dict(major=2, minor=0, patch=0))
        0
        """
        cls = type(self)
        if isinstance(other, string_types):
            other = cls.parse(other)  # type: ignore
        elif isinstance(other, dict):
            other = cls(**other)
        elif isinstance(other, (tuple, list)):
            other = cls(*other)
        elif not isinstance(other, cls):
            raise TypeError(
                "Expected str or {} instance, but got {}".format(
                    cls.__name__, type(other)
                )
            )

        v1 = self.to_tuple()[:3]
        v2 = other.to_tuple()[:3]
        x = cmp(v1, v2)  # type: ignore
        if x:
            return x

        rc1, rc2 = self.prerelease, other.prerelease
        rccmp = _nat_cmp(rc1, rc2)  # type: ignore

        if not rccmp:
            return 0
        if not rc1:
            return 1
        elif not rc2:
            return -1

        return rccmp

    @comparator
    def __eq__(self, other: VersionInfo) -> int:
        """Check if this version equals another version.

        :param other: The version to compare with
        :return: True if versions are equal, False otherwise
        """
        return self.compare(other) == 0

    @comparator
    def __ne__(self, other: VersionInfo) -> bool:
        """Check if this version does not equal another version.

        :param other: The version to compare with
        :return: True if versions are not equal, False otherwise
        """
        return self.compare(other) != 0

    @comparator
    def __lt__(self, other: VersionInfo) -> bool:  # type: ignore
        """Check if this version is less than another version.

        :param other: The version to compare with
        :return: True if this version is less than other, False otherwise
        """
        return self.compare(other) < 0

    @comparator
    def __le__(self, other: VersionInfo) -> bool:  # type: ignore
        """Check if this version is less than or equal to another version.

        :param other: The version to compare with
        :return: True if this version is less than or equal to other, False otherwise
        """
        return self.compare(other) <= 0

    @comparator
    def __gt__(self, other: VersionInfo) -> bool:
        """Check if this version is greater than another version.

        :param other: The version to compare with
        :return: True if this version is greater than other, False otherwise
        """
        return self.compare(other) > 0

    @comparator
    def __ge__(self, other: VersionInfo) -> bool:
        """Check if this version is greater than or equal to another version.

        :param other: The version to compare with
        :return: True if this version is greater than or equal to other, False otherwise
        """
        return self.compare(other) >= 0

    def __getitem__(self, index: slice) -> tuple:
        """Implement __getitem__.

        If the part requested is undefined, or a part of the range requested is undefined, it will throw an index error.
        Negative indices are not supported

        :param index: a positive integer indicating the offset or a :func:`slice` object
        :raises: IndexError, if index is beyond the range or a part is None
        Implement getitem. If the part requested is undefined, or a part of the
        range requested is undefined, it will throw an index error.
        Negative indices are not supported

        :param Union[int, slice] index: a positive integer indicating the
               offset or a :func:`slice` object
        :raises: IndexError, if index is beyond the range or a part is None
        :return: the requested part of the version at position index

        >>> ver = semver.VersionInfo.parse("3.4.5")
        >>> ver[0], ver[1], ver[2]
        (3, 4, 5)
        """
        if isinstance(index, int):
            index = slice(index, index + 1)

        if (
            isinstance(index, slice)
            and (index.start is not None and index.start < 0)
            or (index.stop is not None and index.stop < 0)
        ):
            raise IndexError("Version index cannot be negative")

        part = tuple(
            filter(lambda p: p is not None, self.to_tuple()[index])  # type: ignore
        )

        if len(part) == 1:
            part = part[0]
        elif not part:
            raise IndexError("Version part undefined")
        return part

    def __repr__(self) -> str:
        """Return a string representation of the VersionInfo object.

        :return: a string representation suitable for debugging
        """
        s = ", ".join("{}={!r}".format(key, val) for key, val in self.to_dict().items())
        return "{}({})".format(type(self).__name__, s)

    def __str__(self) -> str:
        """Return a string representation of the version.

        :return: a string in the format "major.minor.patch[-prerelease][+build]"
        """
        version = "%d.%d.%d" % (self.major, self.minor, self.patch)
        if self.prerelease:
            version += "-%s" % self.prerelease
        if self.build:
            version += "+%s" % self.build
        return version

    def __hash__(self) -> int:
        """Return a hash value for the version.

        :return: a hash value based on major, minor, patch, and prerelease
        """
        return hash(self.to_tuple()[:4])

    def match(self, match_expr: str) -> bool:
        """
        Compare self to match a match expression.

        :param str match_expr: operator and version; valid operators are
              <   smaller than
              >   greater than
              >=  greator or equal than
              <=  smaller or equal than
              ==  equal
              !=  not equal
        :return: True if the expression matches the version, otherwise False
        :rtype: bool

        >>> semver.VersionInfo.parse("2.0.0").match(">=1.0.0")
        True
        >>> semver.VersionInfo.parse("1.0.0").match(">1.0.0")
        False
        """
        prefix = match_expr[:2]
        if prefix in (">=", "<=", "==", "!="):
            match_version = match_expr[2:]
        elif prefix and prefix[0] in (">", "<"):
            prefix = prefix[0]
            match_version = match_expr[1:]
        else:
            raise ValueError(
                "match_expr parameter should be in format <op><ver>, "
                "where <op> is one of "
                "['<', '>', '==', '<=', '>=', '!=']. "
                "You provided: %r" % match_expr
            )

        possibilities_dict = {
            ">": (1,),
            "<": (-1,),
            "==": (0,),
            "!=": (-1, 1),
            ">=": (0, 1),
            "<=": (-1, 0),
        }

        possibilities = possibilities_dict[prefix]
        cmp_res = self.compare(match_version)

        return cmp_res in possibilities

    @classmethod
    def parse(cls, version: str) -> VersionInfo:
        """
        Parse version string to a VersionInfo instance.

        :param version: version string
        :return: a :class:`VersionInfo` instance
        :raises: :class:`ValueError`
        :rtype: :class:`VersionInfo`

        .. versionchanged:: 2.11.0
           Changed method from static to classmethod to
           allow subclasses.

        >>> semver.VersionInfo.parse('3.4.5-pre.2+build.4')
        VersionInfo(major=3, minor=4, patch=5, \
prerelease='pre.2', build='build.4')
        """
        if isinstance(version, binary_type):
            version = version.decode(encoding="utf-8", errors="strict")
        match = cls._REGEX.match(version)
        if match is None:
            raise ValueError("%s is not valid SemVer string" % version)

        version_parts = match.groupdict()

        version_parts["major"] = int(version_parts["major"])
        version_parts["minor"] = int(version_parts["minor"])
        version_parts["patch"] = int(version_parts["patch"])

        return cls(**version_parts)  # type: ignore

    @classmethod
    def isvalid(cls, version: str) -> bool:
        """
        Check if the string is a valid semver version.

        .. versionadded:: 2.9.1

        :param str version: the version string to check
        :return: True if the version string is a valid semver version, False
                 otherwise.
        :rtype: bool
        """
        try:
            cls.parse(version)
            return True
        except ValueError:
            return False


def _nat_cmp(a: int, b: int) -> int:
    """Compare two prerelease strings using natural ordering.

    This function implements natural comparison for prerelease strings,
    where numeric parts are compared as numbers and non-numeric parts
    are compared as strings.

    :param a: first prerelease string to compare
    :param b: second prerelease string to compare
    :return: negative if a < b, zero if a == b, positive if a > b
    """

    def convert(text: str) -> int:
        """Convert text to int if it's numeric, otherwise return as string.

        :param text: the text to convert
        :return: integer if text is numeric, otherwise the original string
        """
        return int(text) if re.match("^[0-9]+$", text) else text  # type: ignore

    def split_key(key: str) -> list:
        """Split a key by dots and convert numeric parts.

        :param key: the key string to split
        :return: list of converted parts
        """
        return [convert(c) for c in key.split(".")]

    def cmp_prerelease_tag(a: int, b: int) -> int:
        """Compare two prerelease tag parts.

        :param a: first tag part to compare
        :param b: second tag part to compare
        :return: negative if a < b, zero if a == b, positive if a > b
        """
        if isinstance(a, int) and isinstance(b, int):
            return cmp(a, b)
        elif isinstance(a, int):
            return -1
        elif isinstance(b, int):
            return 1
        else:
            return cmp(a, b)

    a, b = a or "", b or ""  # type: ignore
    a_parts, b_parts = split_key(a), split_key(b)  # type: ignore
    for sub_a, sub_b in zip(a_parts, b_parts):
        cmp_result = cmp_prerelease_tag(sub_a, sub_b)
        if cmp_result != 0:
            return cmp_result
    else:
        return cmp(len(a), len(b))  # type: ignore
