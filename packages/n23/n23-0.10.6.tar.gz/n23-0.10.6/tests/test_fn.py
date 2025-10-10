#
# n23 - data acquisition and processing framework
#
# Copyright (C) 2013-2024 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Collection of functions to support functional programming in Python.
"""

import typing as tp
from collections.abc import Iterable

from n23.fn import head, tail, compose

import pytest

T = tp.TypeVar('T')

@pytest.mark.parametrize(
    "values, expected",
    [[[1, 2, 3], 1],
     [range(2, 5), 2]]
)
def test_head(values: Iterable[T], expected: T) -> None:
    """
    Test getting head item of an iterable.
    """
    assert head(values) == expected

@pytest.mark.parametrize(
    "values, expected",
    [[[1, 2, 3], [2, 3]],
     [range(2, 5), [3, 4]]]
)
def test_tail(values: Iterable[T], expected: list[T]) -> None:
    """
    Test getting head item of an iterable.
    """
    assert list(tail(values)) == expected

def test_compose_0() -> None:
    """
    Test function composition when the first function has no arguments.
    """
    result = compose(lambda: 1, lambda v: v * 3)()  # type: ignore
    assert result == 3

def test_compose() -> None:
    """
    Test function composition.
    """
    result = compose(lambda v: v + 1, lambda v: v * 3, lambda v: v - 1)(2)  # type: ignore
    assert result == 8

# vim: sw=4:et:ai
