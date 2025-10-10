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

from n23.util import to_datetime

import pytest

DATETIME_DATA = (
    (1654038062, '2022-05-31 23:01:02+00:00'),
    (1667260873, '2022-11-01 00:01:13+00:00'),
)

@pytest.mark.parametrize('ts, expected', DATETIME_DATA)
def test_datetime_conv(ts: float, expected: str) -> None:
    """
    Test Unix epoch to datetime conversion.
    """
    dt = to_datetime(ts)
    assert dt.isoformat(sep=' ') == expected

# vim: sw=4:et:ai
