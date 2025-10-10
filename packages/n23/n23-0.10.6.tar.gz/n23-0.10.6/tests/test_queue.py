#
# n23 - data acquisition and processing framework
#
# Copyright (C) 2013-2023 by Artur Wroblewski <wrobell@riseup.net>
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
# ruff: noqa: SLF001

"""
Unit tests for queue with limited number of items.
"""

import asyncio
from n23.queue import NQueue

import pytest

def test_queue_put() -> None:
    """
    Test adding items to queue.
    """
    queue = NQueue[int](3)
    queue.put(1)
    queue.put(2)
    queue.put(3)
    queue.put(4)

    assert list(queue._data) == [2, 3, 4]

@pytest.mark.timeout(3)
@pytest.mark.asyncio
async def test_queue_get() -> None:
    """
    Test getting items from queue.
    """
    queue = NQueue[int](3)
    async def add() -> bool:
        await asyncio.sleep(0.2)
        queue.put(101)
        return True

    mark_add, result = await asyncio.gather(add(), queue.get())
    assert mark_add is True
    assert result == 101

@pytest.mark.timeout(3)
@pytest.mark.asyncio
async def test_queue_get_twice() -> None:
    """
    Test type error for two consumer of a queue.
    """
    queue = NQueue[int](3)
    with pytest.raises(TypeError):
        await asyncio.gather(queue.get(), queue.get())

@pytest.mark.timeout(3)
@pytest.mark.asyncio
async def test_queue_size() -> None:
    queue = NQueue[int](3)
    queue.put(1)
    queue.put(2)
    assert not queue.full()
    assert len(queue) == 2

    queue.put(3)
    assert queue.full()
    assert len(queue) == 3

    queue.put(4)
    assert len(queue) == 3
    assert list(queue._data) == [2, 3, 4]

# vim: sw=4:et:ai
