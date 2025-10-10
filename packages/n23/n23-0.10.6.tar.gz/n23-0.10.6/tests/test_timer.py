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
Tests for timer with timer tick.
"""

import time
from n23.timer import Timer

import pytest

@pytest.mark.asyncio
async def test_timer_tick_and_expirations() -> None:
    """
    Test timer initialization, expiration and tick count.
    """
    timer = Timer(0.1)
    timer.start()
    num_exp = await timer

    assert 1 == num_exp
    assert 0 == timer._tick

@pytest.mark.asyncio
async def test_timer_tick_and_expirations_over() -> None:
    """
    Test timer initialization, expiration and tick count.
    """
    timer = Timer(0.1)
    timer.start()

    num_exp = await timer
    num_exp = await timer
    num_exp = await timer

    time.sleep(0.2)
    num_exp = await timer

    assert 2 == num_exp

    # due to two expirations
    assert 4 == timer._tick

# vim: sw=4:et:ai
