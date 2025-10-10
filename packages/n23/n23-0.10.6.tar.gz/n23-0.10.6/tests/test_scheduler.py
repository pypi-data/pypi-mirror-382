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
The n23 scheduler unit tests.
"""

import asyncio
import functools
import logging
import time
import typing as tp
from collections import Counter
from collections.abc import AsyncIterator, Awaitable

from n23.fn import identity
from n23.scheduler import create_task_function, run_task_ed, Scheduler, \
    TaskHandle, TaskResult, logger as s_logger
from n23.queue import NQueue

import pytest
from unittest import mock

logger = logging.getLogger()

@pytest.mark.asyncio
async def test_task_read_awaitable() -> None:
    """
    Test reading data with an awaitable.
    """
    class Reader(Awaitable[str]):
        def __await__(self) -> tp.Generator[None, None, str]:
            yield from ()
            return 'value'

    cf = create_task_function(Reader())
    assert await cf() == 'value'

@pytest.mark.asyncio
async def test_task_read_func() -> None:
    """
    Test reading data with a function.
    """
    cf = create_task_function(lambda: 'value')
    assert await cf() == 'value'

@pytest.mark.asyncio
async def test_task_read_coroutine() -> None:
    """
    Test reading data with a coroutine.
    """
    async def reader() -> str:
        return 'value'

    cf = create_task_function(reader)
    assert await cf() == 'value'

@pytest.mark.asyncio
async def test_task_read_coroutine_partial() -> None:
    """
    Test reading data with coroutine enclosed with partial.
    """
    async def reader(v: str) -> str:
        return 'value ' + v

    cf = create_task_function(functools.partial(reader, 'test'))
    assert await cf() == 'value test'

@pytest.mark.asyncio
async def test_task_read_async_generator() -> None:
    """
    Test reading data with a asynchronous generator.
    """
    async def reader() -> AsyncIterator[str]:
        while True:
            yield 'value'

    cf = create_task_function(reader)
    assert await cf() == 'value'

@pytest.mark.timeout(1)
@pytest.mark.asyncio
async def test_task_ed_read() -> None:
    """
    Test reading data with event-driven task.
    """
    async def reader() -> AsyncIterator[str]:
        for i in range(3):
            await asyncio.sleep(0.001)
            yield 'value'

    th = TaskHandle[str]('pressure')
    queue = NQueue[TaskResult[str]](5)
    task = run_task_ed(th, create_task_function(reader), queue)

    try:
        await task
    except StopAsyncIteration as ex:
        logger.info('ignoring: {}'.format(ex))

    result = queue._data
    assert [v.name for v in result] == ['pressure'] * 3
    assert [v.value for v in result] == ['value'] * 3

def test_scheduler_adding_regular_task() -> None:
    """
    Test adding regular task with pipeline and sink to scheduler.
    """
    async def source() -> int: return 1
    async def sink(v: TaskResult[int]) -> None: pass

    scheduler = Scheduler()
    handle = scheduler.add(1, 'pressure', source, identity, sink)
    assert not scheduler._e_tasks
    assert not scheduler._a_tasks

    task = scheduler._r_tasks[0]
    assert task.interval == 1
    assert task.handle == handle
    assert task.source == source
    assert task.pipeline == identity
    assert task.sink == sink

def test_scheduler_adding_ed_task() -> None:
    """
    Test adding event-driven task with pipeline and sink to scheduler.
    """
    async def source() -> int: return 1
    async def sink(v: TaskResult[int]) -> None: pass

    scheduler = Scheduler()
    handle = scheduler.add('pressure', source, identity, sink)
    assert not scheduler._r_tasks
    assert not scheduler._a_tasks

    task = scheduler._e_tasks[0]
    assert task.handle == handle
    assert task.source == source
    assert task.pipeline == identity
    assert task.sink == sink

def test_scheduler_adding_action_task() -> None:
    """
    Test adding action task with pipeline and sink to scheduler.
    """
    async def action() -> None: pass

    scheduler = Scheduler()
    handle = scheduler.add(1, 'pressure', action)
    assert not scheduler._r_tasks
    assert not scheduler._e_tasks

    task = scheduler._a_tasks[0]
    assert task.interval == 1
    assert task.action == action
    assert task.handle == handle

@pytest.mark.timeout(5)
@pytest.mark.asyncio
async def test_scheduler_reader_regular() -> None:
    """
    Test scheduler reading data with a coroutine.
    """
    async def reader() -> int:
        return 2

    sink = mock.AsyncMock(side_effect=[None, ValueError('stop')])

    start = time.time()
    scheduler = Scheduler()
    scheduler.add(0.1, 'pressure', reader, identity, sink)
    with pytest.raises(ValueError, match=r'^stop$'):
        await scheduler

    assert scheduler.ctx.tick == 1
    assert scheduler.ctx.time > start

    # data is consumed by the sink
    assert len(scheduler._r_tasks[0].queue._data) == 0

@pytest.mark.asyncio
async def test_scheduler_reader_error() -> None:
    """
    Test scheduler not swallowing error thrown by data reader.
    """
    async def reader() -> tp.NoReturn:
        raise ValueError('test test test')

    sink = mock.AsyncMock()

    scheduler = Scheduler()
    scheduler.add(0.1, 'pressure', reader, identity, sink)
    with pytest.raises(ExceptionGroup, match=r'^Task execution failed') as ctx:
        await scheduler
    assert ctx.group_contains(ValueError, match=r'^test test test$')

@pytest.mark.timeout(1)
@pytest.mark.asyncio
async def test_scheduler_reader_timeout() -> None:
    """
    Test scheduler logging information on data read timeout.
    """
    with mock.patch.object(asyncio, 'wait') as mock_wait:
        task = mock.MagicMock()
        task.get_name.return_value = 'pressure'

        stopper = mock.MagicMock()
        stopper.exception.return_value = ValueError('stop')
        mock_wait.side_effect = [
            [{}, {task}],
            [{stopper}, {}],
        ]

        scheduler = Scheduler()
        scheduler.add(
            0.1, 'pressure', mock.MagicMock(),  identity, mock.MagicMock()
        )
        p_logger = mock.patch.object(s_logger, 'info')
        with p_logger as f, \
                pytest.raises(ExceptionGroup, match=r'^Task execution failed') as ctx:
            await scheduler._run_tasks()

        assert ctx.group_contains(ValueError, match=r'^stop$')

        # the timeout was logged and task got cancelled
        c1 = f.call_args_list[1]
        assert c1 == mock.call('pending tasks: n=1, tasks(5)=pressure')

@pytest.mark.timeout(1)
@pytest.mark.asyncio
async def test_scheduler_pipeline_null() -> None:
    """
    Test scheduler skipping sink on pipeline returing null.
    """
    async def reader() -> AsyncIterator[int]:
        yield 1
        yield 1
        raise ValueError('stop')

    counter = Counter[int]()
    def pl(v: TaskResult[int]) -> TaskHandle[int] | None:
        counter[v.value] += 1
        return None

    sink = mock.AsyncMock()

    scheduler = Scheduler()
    scheduler.add(0.1, 'pressure', reader, pl, sink)
    assert len(scheduler._r_tasks) == 1

    with pytest.raises(ExceptionGroup, match=r'^Task execution failed') as ctx:
        await scheduler
    assert ctx.group_contains(ValueError, match=r'^stop$')

    assert counter[1] == 2  # pipeline called twice
    assert sink.call_count == 0  # but sink is not called at all

@pytest.mark.timeout(1)
@pytest.mark.asyncio
async def test_scheduler_sink_error() -> None:
    """
    Test scheduler not swallowing error thrown by sink.
    """
    async def reader() -> int:
        return 1

    sink = mock.AsyncMock()
    sink.side_effect = [ValueError('test test test')]

    scheduler = Scheduler()
    scheduler.add(0.1, 'pressure', reader, identity, sink)
    assert len(scheduler._r_tasks) == 1

    with pytest.raises(ValueError, match=r'^test test test$'):
        await scheduler

    sink.assert_called_once()

@pytest.mark.timeout(3)
@pytest.mark.asyncio
async def test_scheduler_cancel() -> None:
    """
    Test cancelling scheduler.
    """
    async def reader() -> int:
        return 1

    async def reader_event() -> int:
        await asyncio.sleep(0.25)
        return 1

    async def cancel(task: asyncio.Future[None]) -> None:
        await asyncio.sleep(1)
        task.cancel('done')

    sink = mock.AsyncMock()
    sink_event = mock.AsyncMock()

    scheduler = Scheduler()
    scheduler.add(0.2, 'pressure', reader, identity, sink)
    scheduler.add('gps', reader_event, identity, sink_event)

    task = asyncio.ensure_future(scheduler)
    with pytest.raises(asyncio.CancelledError, match=r'^done$'):
        await asyncio.gather(cancel(task), task)

    # sleep a while and check if all tasks are cancelled
    await asyncio.sleep(1)

    # expected 5, but give it a bit of flexibility
    assert 4 <= sink.call_count <= 6

    # expected 4, but give it a bit of flexibility
    assert 3 <= sink_event.call_count <= 6

    assert len(asyncio.all_tasks()) == 1

# vim: sw=4:et:ai
