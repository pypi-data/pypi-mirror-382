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
N23 scheduler to run asynchronous tasks processing data and executing
actions.

There are three types of tasks

- data task executed at regular time intervals; data received by the task
  is transformed by a pipeline function, and then by a sink asynchronous
  coroutine
- event-driven data tasks; data is received as it arrives, and is processed
  like above
- action tasks executed at regular time intervals; no data is received

The data tasks execution is split between 3 stages

- receive data with an asynchronous coroutine
- transform data with a pipeline function, which is a regular Python
  callable
- send data to a sink, which is an asynchronous coroutine

Different kinds of Python functions can be actions or receive data. These
are coroutines, asynchronous generators, awaitables, and regular Python
functions. They are always used as an asynchronous coroutine, i.e.
a regular function is run with `asyncio.to_thread`.

Design Notes
============
1. Task execution is separated from processing of a data of the task. This
   allows enqueue the data if processing happens to be too slow

   - the oldest data is lost when the queue is full
   - in the future, let's block a task when its data queue is full with
     a task policy

2. Tasks scheduled at regular intervals have timeout equal to 75% of time
   interval to receive data. At the next edge of the interval, non-pending
   tasks are rescheduled, and pending tasks are awaited

   - in the future the regular tasks timeout property needs to be
     configurable
   - in the future, allow to cancel tasks instead of waiting for them with
     a task policy

3. `atimer <https://wrobell.dcmod.org/atimer/>`_ library is used for
   scheduler timer. This allows expiration at regular intervals and
   reporting of timer overruns.

4. The data tasks execution is split between 3 stages to emphasize the
   rule, that data should not be received or sent during data
   transformation.

5. The functions receiving data shall not block the scheduler, therefore
   regular Python functions are turned into coroutines with
   `asyncio.to_thread` function.
"""

from __future__ import annotations

import asyncio
import enum
import inspect
import logging
import time
import typing as tp
from collections.abc import Awaitable, Coroutine, AsyncGenerator, \
    AsyncIterator, Generator, Iterable
from dataclasses import dataclass
from itertools import islice

from .fn import concat, partial
from .timer import Timer
from .queue import NQueue

logger = logging.getLogger(__name__)

type TaskCoroutine[T] = Coroutine[None, None, T]
type TaskCoroutineFunction[T] = tp.Callable[[], TaskCoroutine[T]]
type SourceFunction[T] = Awaitable[T] \
    | tp.Callable[
        [],
        T \
        | TaskCoroutine[T] \
        | AsyncGenerator[T] \
        | AsyncIterator[T]
]
type PipelineFunction[T, S] = tp.Callable[['TaskResult[T]'], S | None]
type SinkFunction[T] = tp.Callable[[T], Awaitable[tp.Any]]
type ActionFunction = SourceFunction[tp.Any | None]
type DataTask = 'RegularTask[tp.Any, tp.Any]' | 'EventDrivenTask[tp.Any, tp.Any]'

@dataclass(frozen=True, slots=True)
class TaskHandle[T]:
    """
    Scheduler task handle.
    """
    name: str

@dataclass(frozen=True, slots=True)
class TaskResult[T]:
    """
    Result of task execution.
    """
    time: float
    name: str
    value: T

class TimeoutPolicy(enum.Enum):
    """
    Timeout policies for N23 scheduler tasks.
    """
    CONTINUE = enum.auto()

class BufferPolicy(enum.Enum):
    """
    Buffer policies for N23 scheduler tasks.
    """
    DROP_OLD = enum.auto()

@dataclass(frozen=True, slots=True)
class TaskPolicy:
    """
    N23 scheduler task policy.

    :var on_timeout: What to do on scheduler task timeout.
    :var on_buffer_full: What to do when scheduler task buffer is full.
    :var buffer_limit: N23 scheduler task buffer limit.
    """
    on_timeout: TimeoutPolicy=TimeoutPolicy.CONTINUE
    on_buffer_full: BufferPolicy=BufferPolicy.DROP_OLD
    buffer_limit: int=1000

DEFAULT_TASK_POLICY = TaskPolicy()

@dataclass(frozen=False, slots=True)
class Context:
    """
    N23 scheduler context.

    :var tick: Timer cycle tick.
    :var time: Time at the start of timer cycle.
    """
    tick: int
    time: float

@dataclass(frozen=True, slots=True)
class Task[T]:
    handle: TaskHandle[T]

@dataclass(frozen=True, slots=True)
class RegularTask[T, S](Task[T]):
    interval: float
    source: SourceFunction[T]
    pipeline: PipelineFunction[T, S]
    sink: SinkFunction[S]
    queue: NQueue[TaskResult[T]]

@dataclass(frozen=True, slots=True)
class EventDrivenTask[T, S](Task[T]):
    source: SourceFunction[T]
    pipeline: PipelineFunction[T, S]
    sink: SinkFunction[S]
    queue: NQueue[TaskResult[T]]

@dataclass(frozen=True, slots=True)
class ActionTask(Task[tp.Any]):
    interval: float
    action: ActionFunction

class Scheduler(Awaitable[None]):
    """
    N23 scheduler to run asynchronous tasks processing data and executing
    actions.

    :var ctx: Scheduler context.
    :var timeout: Asynchronous task timeout.
    """
    def __init__(self, *, timeout: float | None=None):
        self.timeout = timeout

        self._r_tasks: list[RegularTask[tp.Any, tp.Any]] = []
        self._e_tasks: list[EventDrivenTask[tp.Any, tp.Any]] = []
        self._a_tasks: list[ActionTask] = []

        self.ctx = Context(-1, time.time())

    @tp.overload
    def add(
        self, interval: float, name: str, action: ActionFunction
    ) -> TaskHandle[tp.Any | None]: ...

    @tp.overload
    def add[T, S](
        self,
        name: str,
        source: SourceFunction[T],
        pipeline: PipelineFunction[T, S],
        sink: SinkFunction[S],
        *,
        policy: TaskPolicy=DEFAULT_TASK_POLICY,
    ) -> TaskHandle[T]: ...

    @tp.overload
    def add[T, S](
        self,
        interval: float,
        name: str,
        source: SourceFunction[T],
        pipeline: PipelineFunction[T, S],
        sink: SinkFunction[S],
        *,
        policy: TaskPolicy=DEFAULT_TASK_POLICY,
    ) -> TaskHandle[T]: ...

    def add(self, ni: float | str, *args, **kwargs) -> TaskHandle[tp.Any]:  # type: ignore[misc, no-untyped-def]
        """
        Add an asynchronous task to the scheduler.

        Three forms of the method are supported::

        `add(interval, name, action)`
            Add task to execute an asynchronous action.

        `add(interval, name, source, pipeline, sink)`
            Add data task to receive and process data at regular time
            intervals.

        `add(name, source, pipeline, sink)`
            Add data, event-driven task to receive and process data as it
            arrives.


        A data source function or an action can be

        - a coroutine
        - an asynchronous generator
        - an awaitable
        - a regular Python functions

        Data from `source` is buffered in a queue. Pipeline and sink are
        executed whenever there is data in the buffer. Data is lost when
        the queue is full.

        Pipeline and sink receive object of class :py:class:`n23.TaskResult`
        as its first parameter. Use `functools.partial` to set default
        parameters if the functions have more parameters.

        If `interval` is specified, then asynchronous task is run at
        regular intervals with a timer, thus obtaining equally spaced time
        series. Otherwise, task receives data as it arrives and unevenly
        spaced time series is generated.

        :param interval: Run task at regular time intervals (not defined
            for an event-driven task).
        :param name: Name (identifier) of the task. Unique for each task.
        :param source: Coroutine or function to receive source data
            (alternatively an action, see below).
        :param action: Coroutine or function to execute as an action.
        :param pipeline: Function to process source data (not defined for
            an action).
        :param sink: Coroutine to store or forward data (not defined for
            an action).
        :param policy: Task policy.

        .. seealso::

           - :py:class:`n23.TaskResult`
           - :py:class:`n23.TaskHandle`
        """
        num_args = len(args)
        logger.debug('add task: name or interval={}, num args={}'.format(
            ni, num_args
        ))

        match (ni, num_args):
            case (str(), int()):
                handle = self._add_e_task(ni, *args, **kwargs)
            case (float() | int(), 2):
                handle = self._add_action(ni, *args, **kwargs)
            case (float() | int(), int()):
                handle = self._add_r_task(ni, *args, **kwargs)
            case _:
                raise NotImplementedError('Method not implemented')
        return handle

    def _add_r_task[T, S](  # noqa: PLR0913
            self,
            interval: float,
            name: str,
            source: SourceFunction[T],
            pipeline: PipelineFunction[T, S],
            sink: SinkFunction[S],
            *,
            policy: TaskPolicy=DEFAULT_TASK_POLICY,
    ) -> TaskHandle[T]:
        """
        Submit task to execute at regular time intervals.
        """
        handle = TaskHandle[T](name)
        queue = NQueue[TaskResult[T]](max_size=policy.buffer_limit)
        task = RegularTask[T, S](
            handle, interval, source, pipeline, sink, queue
        )
        self._r_tasks.append(task)
        return handle

    def _add_e_task[T, S](
            self,
            name: str,
            source: SourceFunction[T],
            pipeline: PipelineFunction[T, S],
            sink: SinkFunction[S],
            *,
            policy: TaskPolicy=DEFAULT_TASK_POLICY,
    ) -> TaskHandle[T]:
        """
        Submit event-driven task to receive data as it arrives.
        """
        handle = TaskHandle[T](name)
        queue = NQueue[TaskResult[T]](max_size=policy.buffer_limit)
        task = EventDrivenTask[T, S](handle, source, pipeline, sink, queue)
        self._e_tasks.append(task)
        return handle

    def _add_action(
            self,
            interval: float,
            name: str,
            action: ActionFunction,
    ) -> TaskHandle[tp.Any]:
        """
        Submit action task to execute it at regular time intervals.

        :param interval: Run task at regular time intervals if specified.
        :param name: Name (identifier) of the task.
        :param action: Coroutine or function to execute as an action task.
        """
        handle = TaskHandle[tp.Any](name)
        task = ActionTask(handle, interval, action)
        self._a_tasks.append(task)
        return handle

    def __await__(self) -> Generator[tp.Any]:
        """
        Start scheduler and run tasks of the scheduler.
        """
        # always run the loop with regular and action tasks to generate
        # scheduler tick (even when there are no tasks)
        reg_task = asyncio.ensure_future(self._run_tasks())
        tasks: list[Awaitable[None]] = [reg_task]

        # add event-driven tasks
        tasks.extend(
            run_task_ed(t.handle, create_task_function(t.source), t.queue)
            for t in self._e_tasks
        )

        # add task data processors using pipelines and sinks
        items: Iterable[DataTask] = concat(self._r_tasks, self._e_tasks)
        tasks.extend(
            task_process_data(t.queue, t.pipeline, t.sink) for t in items
        )
        yield from asyncio.gather(*tasks).__await__()

    async def _run_tasks(self) -> None:
        """
        Run N23 scheduler tasks executed at regular time intervals.
        """
        task_cf: tp.Callable[[RegularTask[tp.Any, tp.Any]], TaskCoroutineFunction[None]] = \
            lambda t: partial(
                run_task_regular,
                t.handle, create_task_function(t.source), t.queue
            )
        tasks = [(t.interval, t.handle, task_cf(t)) for t in self._r_tasks]
        tasks.extend(
            (t.interval, t.handle, create_task_function(t.action))
            for t in self._a_tasks
        )

        intervals = set(i for i, *_ in tasks)
        if len(intervals) > 1:
            # TODO: add support for multiplies of the main interval
            raise ValueError('Single interval is supported only')
        elif not intervals:
            interval = 1.0
        else:
            interval = intervals.pop()
        assert not intervals

        timer = Timer(interval)
        timeout = interval * 0.75 if self.timeout is None else self.timeout

        ctx = self.ctx
        wait_tasks = partial(
            asyncio.wait,
            timeout=timeout,
            return_when=asyncio.FIRST_EXCEPTION
        )
        create_task = asyncio.create_task
        exclude = set[str]()
        pending = set[asyncio.Task[tp.Any]]()
        try:
            timer.start()
            while True:
                await timer
                ctx.time = time.time()
                ctx.tick = timer._tick  # noqa: SLF001

                current_tasks = [
                    create_task(cf(), name=h.name) for _, h, cf in tasks
                    if h.name not in exclude
                ]
                current_tasks.extend(pending)
                if current_tasks:
                    done, pending = await wait_tasks(current_tasks)

                    # crash software on error
                    errors = [e for t in done if (e := t.exception())]
                    if errors:
                        raise ExceptionGroup('Task execution failed', errors)

                    exclude = {t.get_name() for t in pending}
                    if exclude:
                        logger.info('pending tasks: n={}, tasks(5)={}'.format(
                            len(exclude), ', '.join(islice(exclude, 5))
                        ))
        finally:
            timer.close()

#
# functions to create task coroutines, execute tasks, and process task data
# for N23 scheduler
#

def create_task_function[T](
        func: SourceFunction[T] | ActionFunction
) -> TaskCoroutineFunction[tp.Any]:
    """
    Create asynchronous coroutine function to execute a task of N23
    scheduler.

    A data source function or an action can be

    - a coroutine
    - an asynchronous generator
    - an awaitable
    - a regular Python functions

    :param func: Data source function or an action.
    """

    task_cf: TaskCoroutineFunction[tp.Any]
    if inspect.isawaitable(func):
        task_cf = lambda: func  # type: ignore[assignment, return-value]
        logger.info('{} is awaitable'.format(func))
    elif inspect.iscoroutinefunction(func):
        task_cf = func
        logger.info('{} is coroutine function'.format(func))
    elif inspect.isasyncgenfunction(func):
        task_cf = func().__anext__
        logger.info('{} is asynchronous generator'.format(func))
    else:
        task_cf = partial(asyncio.to_thread, func)
        logger.info('{} is function, run in a thread' .format(func))

    return task_cf

async def run_task_regular[T](
        handle: TaskHandle[T],
        task_cf: TaskCoroutineFunction[T],
        queue: NQueue[TaskResult[T]],
) -> None:
    """
    Execute task and put result of the task into the buffer queue.

    :param handle: N23 scheduler task handle.
    :param task_cf: Task coroutine function.
    :param queue: N23 scheduler task buffer queue.
    """
    value = await task_cf()
    result = TaskResult(time.time(), handle.name, value)

    if __debug__ and queue.full():
        logger.debug('queue to drop task results: task={}'.format(
            handle.name
        ))
    queue.put(result)

async def run_task_ed[T](
        handle: TaskHandle[T],
        task_cf: TaskCoroutineFunction[T],
        queue: NQueue[TaskResult[T]],
) -> None:
    """
    Execute N23 scheduler event-driven task and process its data as it
    arrives.

    :param handle: N23 scheduler task handle.
    :param task_cf: Task coroutine function.
    :param queue: N23 scheduler task buffer queue.
    """
    while True:
        await run_task_regular(handle, task_cf, queue)

async def task_process_data[T, S](
        queue: NQueue[TaskResult[T]],
        pipeline: PipelineFunction[T, S],
        sink: SinkFunction[S],
) -> None:
    while True:
        value = await queue.get()
        if (result := pipeline(value)) is not None:
            await sink(result)

__all__ = ['Scheduler', 'TaskHandle', 'TaskResult']

# vim: sw=4:et:ai
