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
from inspect import signature
from itertools import chain, islice
from functools import partial

T = tp.TypeVar('T')
S = tp.TypeVar('S')

concat = chain
flatten = chain.from_iterable

def identity(v: T) -> T:
    """
    Identity function.
    """
    return v

def head(it: Iterable[T]) -> T:
    """
    Get head (first) item of an iterable.
    """
    return next(islice(it, 0, 1))

def tail(it: Iterable[T]) -> Iterable[T]:
    """
    Get tail (all items, but the first) of an iterable.
    """
    return islice(it, 1, None)

def compose(*funcs):  # type: ignore
    """
    Compose functions.
    """
    first = head(funcs)
    rest = tail(funcs)

    first_has_param = bool(signature(first).parameters)

    def wrapper_0():  # type: ignore
        result = first()
        for f in rest:
            result = f(result)
        return result

    def wrapper_1(v):  # type: ignore
        result = first(v)
        for f in rest:
            result = f(result)
        return result

    return wrapper_1 if first_has_param else wrapper_0

__all__ = [
    'compose', 'concat', 'flatten', 'head', 'identity', 'partial', 'tail',
]

# vim: sw=4:et:ai
