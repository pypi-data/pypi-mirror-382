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

import typing as tp

from ..dsl import parse_dsl
from ..util import read_file
from .config_schema import PARSER
from .types import ApplicationConfig, ApplicationConfigError

def read_app_config(fn: str) -> ApplicationConfig:
    """
    Read N23 application configuration file.

    :param fn: File or resource path.
    """
    with read_file(fn, 'cfg') as data:
        return parse_dsl(data, PARSER, ApplicationConfig, positional=True)

def app_config_value(
        config: ApplicationConfig, section: str, name: str, default: tp.Any=None
) -> tp.Any:
    """
    Get configuration value for N23 application.

    :param config: N23 application configuration.
    :param section: Section name of the configuration.
    :param name: Configuration item value.
    :param default: Default value of configuration item.
    """
    no_value = object()
    items = (
        c.value for s in config.section for c in s.items
        if (s.name, c.name) == (section, name)
    )
    value = next(items, no_value)
    if default is None and value is no_value:
        raise ApplicationConfigError(
            'Configuration value not found, section={}, name={}'
            .format(section, name)
        )
    elif default is not None and value is no_value:
        value = default

    return value

def app_config_value_optional(
        config: ApplicationConfig, section: str, name: str
) -> tp.Any | None:
    """
    Get configuration value for N23 application or null value.

    :param config: N23 application configuration.
    :param section: Section name of the configuration.
    :param name: Configuration item value.
    """
    items = (
        c.value for s in config.section for c in s.items
        if (s.name, c.name) == (section, name)
    )
    return next(items, None)

# vim: sw=4:et:ai
