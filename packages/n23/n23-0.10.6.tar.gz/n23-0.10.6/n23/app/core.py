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
Helper functions to start applications based on N23 framework.
"""

import asyncio
import logging
import signal
import sys
import typing as tp
import uvloop
from collections.abc import Coroutine
from unittest import mock

logger = logging.getLogger(__name__)

T = tp.TypeVar('T')
S = tp.TypeVar('S')
V = tp.TypeVar('V')

def run(coro: Coroutine[T, S, V]) -> V:
    """
    Run application based on N23 framework.

    The function provides the following benefits

    - uvloop based asyncio loop
    - TERM and INT signal handlers are installed to allow graceful shutdown
      of application components
    """
    uvloop.install()
    logger.info('uvloop installed')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    with mock.patch.object(asyncio.events, 'new_event_loop') as mock_new_loop:
        mock_new_loop.return_value = loop

        # shutdown gracefully on SIGTERM and SIGINT
        loop.add_signal_handler(signal.SIGTERM, sys.exit)
        loop.add_signal_handler(signal.SIGINT, sys.exit)

        return asyncio.run(coro)

# vim: sw=4:et:ai
