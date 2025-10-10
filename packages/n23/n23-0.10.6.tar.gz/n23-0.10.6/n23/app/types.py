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

import dataclasses as dtc
import typing as tp
from collections.abc import Awaitable
from contextlib import AbstractAsyncContextManager

from ..scheduler import Scheduler

Process: tp.TypeAlias = Awaitable[tp.Any]

@dtc.dataclass(frozen=True)
class ApplicationRunContext:
    """
    N23 application run context.

    NOTE: Process manager should return null or an awaitable.

    :var setup: Function to setup/start application to be run via N23
        framework.
    :var scheduler: N23 scheduler.
    :var process_managers: Context managers, which create processes.
    :var processes: List of processes.
    """
    setup: tp.Callable[[], Awaitable[tp.Any]]
    scheduler: Scheduler
    process_managers: list[AbstractAsyncContextManager[Process]]
    processes: list[Process]

@dtc.dataclass(frozen=True)
class ApplicationConfigItem:
    name: str
    value: object

@dtc.dataclass(frozen=True)
class ApplicationConfigSection:
    name: str
    items: list[ApplicationConfigItem]

@dtc.dataclass(frozen=True)
class ApplicationConfig:
    section: list[ApplicationConfigSection]

class ApplicationConfigError(Exception):
    """
    N23 application configuration error.
    """

# vim: sw=4:et:ai
