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
import hy
import logging
import typing as tp
from functools import partial
from inspect import get_annotations
from hy.model_patterns import Expression, Symbol
from hy.models import Object

logger = logging.getLogger(__name__)

T = tp.TypeVar('T')
S = tp.TypeVar('S')

def parse_dsl(
        data: str, parser: Expression, cls: type[T], /, positional: bool=False
) -> T:
    form = list(hy.read_many(data))
    qform = [qquote(s) if is_toplevel(cls, s) else s for s in form]
    eform = [s for s in hy.eval(qform) if s is not None]
    if positional:
        return parse_struct_pos(cls, parser.parse(eform))
    else:
        args = parse_attrs_as_dict(cls, parser.parse(eform))
        return cls(**args)

def qquote(expr: Expression) -> Expression:
    return Expression([Symbol('quasiquote'), expr])

def is_toplevel(cls: type, expr: Expression) -> bool:
    name = str(expr[0])
    fields = {f.name for f in dtc.fields(cls)}
    return name in fields

def parse_attr_name(attr: Symbol | str) -> str:
    return hy.mangle(str(attr))  # type: ignore[no-any-return]

def get_attr_type(cls: type, attr: str) -> type:
    name = parse_attr_name(attr)
    return get_annotations(cls)[name]  # type: ignore[no-any-return]

def parse_attr_value(attr_type: type[T], attr_value: tp.Any) -> tp.Any:

    attr_sub_type = getattr(attr_type, '__args__', [None])[0]

    logger.debug('parsing value, type={}, sub-type={}, value={}'.format(
        attr_type, attr_sub_type, attr_value
    ))

    result: tp.Any
    match attr_value:
        case Expression():
            result = [
                parse_attr_value(attr_sub_type, item) for item in attr_value
            ]
        case Symbol():
            result = str(attr_value)
        case Object():
            result = hy.eval(attr_value)
        case [Symbol(), *_]:
            result = tuple(
                parse_attr_value(attr_sub_type, item) for item in attr_value
            )
        case _:
            result = attr_value

    return result

def parse_attrs_as_dict(cls: type[T], args: list[tp.Any]) -> dict[str, tp.Any]:
    items = (v for v in args if v is not None)
    to_type = partial(get_attr_type, cls)
    return {
        parse_attr_name(key): parse_attr_value(to_type(key), value)
        for key, value in items
    }

def parse_struct_kw(cls: type[T], args: list[tp.Any]) -> tuple[str, T]:
    kw = parse_attrs_as_dict(cls, args[1:])
    return (args[0], cls(**kw))

def parse_struct_kw_named(cls: type[T], args: list[tp.Any]) -> T:
    name = str(args[0])
    kw = parse_attrs_as_dict(cls, args[1:])
    return cls(name, **kw)  # type: ignore

def parse_struct_pos(cls: type[T], args: list[tp.Any]) -> T:
    fields = (f.name for f in dtc.fields(cls))  # type: ignore
    items = ((get_attr_type(cls, n), v) for n, v in zip(fields, args))
    values: list[tp.Any] = [parse_attr_value(t, v) for t, v in items]
    return cls(*values)

# vim: sw=4:et:ai
