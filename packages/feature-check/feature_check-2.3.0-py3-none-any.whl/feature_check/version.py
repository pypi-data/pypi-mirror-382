# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""Version string parsing for the feature-check Python library."""

from __future__ import annotations

from typing import NamedTuple


class VersionComponent(NamedTuple):
    """Represent a single version component: a numerical part and a freeform string one."""

    num: int | None
    rest: str

    def __str__(self) -> str:
        """Provide a string representation of the version component."""
        return (str(self.num) if self.num is not None else "") + self.rest

    def cmp(self, other: object) -> int:  # noqa: C901,PLR0911,PLR0912
        """Compare two components, return None if they are equal."""
        if not isinstance(other, VersionComponent):
            raise NotImplementedError(repr(other))

        if self.num is not None:
            if other.num is not None:
                if self.num < other.num:
                    return -1
                if self.num > other.num:
                    return 1

                if self.rest is not None:
                    if other.rest is not None:
                        if self.rest < other.rest:
                            return -1
                        if self.rest > other.rest:
                            return 1
                        return 0

                    return 1

                if other.rest is not None:
                    return -1

                return 0

            return 1

        if other.num is not None:
            return -1

        if self.rest is not None:
            if other.rest is not None:
                if self.rest < other.rest:
                    return -1
                if self.rest > other.rest:
                    return 1
                return 0

            return -1

        return 0

    def __lt__(self, other: object) -> bool:
        """Check whether this version component is less than the other one."""
        return self.cmp(other) < 0

    def __le__(self, other: object) -> bool:
        """Check whether this version component is less than or equal to the other one."""
        return self.cmp(other) <= 0

    def __eq__(self, other: object) -> bool:
        """Check whether this version component is equal to the other one."""
        return self.cmp(other) == 0

    def __ne__(self, other: object) -> bool:
        """Check whether this version component is not equal to the other one."""
        return self.cmp(other) != 0

    def __ge__(self, other: object) -> bool:
        """Check whether this version component is greater than or equal to the other one."""
        return self.cmp(other) >= 0

    def __gt__(self, other: object) -> bool:
        """Check whether this version component is greater than the other one."""
        return self.cmp(other) > 0

    def __hash__(self) -> int:
        """Return an integer key for hashable collections."""
        return hash((self.num, self.rest))


class Version(NamedTuple):
    """A version string: many components, possibly other attributes."""

    value: str
    components: list[VersionComponent]


def _version_compare_split_empty(
    spl_a: list[VersionComponent],
    spl_b: list[VersionComponent],
) -> int | None:
    """Check if any of the split version numbers is empty."""
    if not spl_a:
        if not spl_b:
            return 0
        if spl_b[0].num is None:
            return 1
        return -1
    if not spl_b:
        if spl_a[0].num is None:
            return -1
        return 1

    return None


def _version_compare_split(spl_a: list[VersionComponent], spl_b: list[VersionComponent]) -> int:
    """Compare two version numbers already split into component lists.

    Returns -1, 0, or 1 for the first version being less than, equal to,
    or greater than the second one.
    """
    res = _version_compare_split_empty(spl_a, spl_b)
    if res is not None:
        return res

    (comp_a, comp_b) = (spl_a.pop(0), spl_b.pop(0))
    res = comp_a.cmp(comp_b)
    if res != 0:
        return res

    return _version_compare_split(spl_a, spl_b)


def version_compare(ver_a: Version, ver_b: Version) -> int:
    """Compare two version strings.

    Returns -1, 0, or 1 for the first version being less than, equal to,
    or greater than the second one.
    """
    return _version_compare_split(ver_a.components, ver_b.components)
