#
# n23 - data acquisition and processing framework
#
# Copyright (C) 2013-2025 by Artur Wroblewski <wrobell@riseup.net>
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
Utility functions to manage sinks for N23 scheduler.
"""

from .storage import storage_from_uri, Storage

def sink_from_uri(uri: str) -> Storage:
    """
    Create N23 scheduler sink using URI.

    :param uri: Sink URI.
    """
    return storage_from_uri(uri)

# vim: sw=4:et:ai
