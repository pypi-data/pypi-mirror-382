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
Queue with limited number of items.

Adding new items to the queue removes the oldest one when the queue is
full.
"""

import asyncio
from collections import deque

class NQueue[T]:
    """
    Queue with limited number of items.

    Adding an item to a full queue drops oldest queue item.
    """
    def __init__(self, max_size: int) -> None:
        """
        Create queue with its size specified.

        :param max_size: Size of the queue.
        """
        self.max_size = max_size
        self._data = deque[T]([], maxlen=max_size)
        self._task: asyncio.Future[T] | None = None

    def put(self, item: T) -> None:
        """
        Add an item to the queue.

        :param item: Item to add to the queue.
        """
        self._data.append(item)
        task = self._task
        if task is not None and not task.done() and self._data:
            task.set_result(self._data.popleft())

    async def get(self) -> T:
        """
        Get the oldest item from the queue.

        Wait if queue is empty.
        """
        if self._task is not None:
            raise TypeError('A consumer already registered for the queue')

        if self._data:
            result = self._data.popleft()
        else:
            loop = asyncio.get_running_loop()
            self._task = loop.create_future()
            result = await self._task
            self._task = None

        return result

    def full(self) -> bool:
        """
        Return true if queue is full.
        """
        return len(self._data) == self._data.maxlen

    def __len__(self) -> int:
        """
        Return current size of the queue.
        """
        return len(self._data)

# vim: sw=4:et:ai
