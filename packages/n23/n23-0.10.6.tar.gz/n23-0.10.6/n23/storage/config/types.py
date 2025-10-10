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

import dataclasses as dtc

@dtc.dataclass(frozen=True)
class Storage:
    version: str
    role: str
    extensions: tuple[str, ...]=tuple()

@dtc.dataclass(frozen=True)
class Column:
    name: str
    type: str
    nullable: bool

@dtc.dataclass(frozen=True)
class Entity:
    name: str
    partition_by: str | None=None
    columns: list[Column]=dtc.field(default_factory=list)
    chunk: str='1day'

@dtc.dataclass(frozen=True)
class Config:
    storage: Storage
    entities: list[Entity]
    sql: str=''

# vim: sw=4:et:ai
