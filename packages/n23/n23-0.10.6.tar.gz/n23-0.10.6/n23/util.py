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

import logging
import os.path
import typing as tp
from collections.abc import Iterator
from datetime import datetime, timezone
from contextlib import contextmanager
from importlib import resources

logger = logging.getLogger(__name__)

T = tp.TypeVar('T')

def to_datetime(ts: float) -> datetime:
    """
    Convert Unix epoch to datetime object in UTC timezone.

    :param ts: Unix epoch.
    """
    return datetime.fromtimestamp(ts, tz=timezone.utc)

@contextmanager
def read_file(fn: str, ext: str) -> Iterator[str]:
    """
    Read content of a file or a module.

    :param fn: File or resource path.
    """
    if not os.path.exists(fn):
        pkg, name = fn.rsplit('.', 1)
        fn = resources.files(pkg).joinpath(f'{name}.{ext}')  # type: ignore

    logger.info(f'reading file: {fn}')
    with open(fn) as f:
        yield f.read(65 * 1024)  # TODO: make it configurable

# vim: sw=4:et:ai
