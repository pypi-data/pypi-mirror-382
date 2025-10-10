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

from ...dsl import parse_dsl
from .schema import PARSER
from .types import Config
from ...util import read_file

def read_db_config(fn: str) -> Config:
    """
    Read database configuration file.

    :param fn: File or resource path.
    """
    with read_file(fn, 'cfg') as data:
        return parse_dsl(data, PARSER, Config)

# vim: sw=4:et:ai
