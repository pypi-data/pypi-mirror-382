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

"""
Timer tracking its own tick.
"""

import atimer
import logging
import typing as tp

logger = logging.getLogger(__name__)

P = tp.ParamSpec('P')

class Timer(atimer.Timer):
    """
    Timer tracking its own tick.
    """
    def __init__(self, interval: float) -> None:
        """
        Create new timer instance.

        .. seealso:: `atimer.Timer`
        .. seealso:: `atimer.Timer.start`
        """
        super().__init__(interval)
        self._tick = -1

    def __await__(self) -> tp.Generator[tp.Any, None, int]:
        """
        Sleep for time specified by timer interval.

        The coroutine returns number of expirations.

        .. seealso:: `atimer.Timer.start`
        """
        # sleep and count number of expirations
        num_exp = yield from super().__await__()

        # use number of expirations to update the timer tick
        self._tick += num_exp

        if num_exp > 1:
            logger.warning(
                'Timer expired more than one time: {}'.format(num_exp)
            )
        return num_exp

# vim: sw=4:et:ai
