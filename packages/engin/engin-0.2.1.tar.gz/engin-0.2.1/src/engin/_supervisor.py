import inspect
import logging
import typing
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum
from types import TracebackType
from typing import TypeAlias

import anyio
from anyio import get_cancelled_exc_class
from typing_extensions import assert_never

if typing.TYPE_CHECKING:
    from anyio.abc import TaskGroup

LOG = logging.getLogger("engin")

AsyncFunction: TypeAlias = Callable[[], Awaitable[None]]


class OnException(Enum):
    SHUTDOWN = 0
    """
    Cancel all other supervised tasks and shutdown the Engin.
    """

    RETRY = 1
    """
    Retry the task.
    """

    IGNORE = 2
    """
    The task will be not be retried and the engin will not be stopped, other tasks will
    continue to run.
    """


@dataclass(kw_only=True, slots=True, eq=False)
class _SupervisorTask:
    """
    Attributes:
        - factory: a coroutine function that can create the task.
        - on_exception: determines the behaviour when the task raises an exception.
        - complete: will be set to true if task stops for any reason except cancellation.
        - last_exception: the last exception raised by the task.
    """

    factory: AsyncFunction
    on_exception: OnException
    complete: bool = False
    last_exception: Exception | None = None
    shutdown_hook: AsyncFunction | None = None

    async def __call__(self) -> None:
        # loop to allow for restarting erroring tasks
        while True:
            try:
                await self.factory()
                self.complete = True
                return
            except get_cancelled_exc_class() as err:
                LOG.debug(f"supervised task '{self.name}' was cancelled", exc_info=err)
                raise
            except Exception as err:
                self.last_exception = err
                if self.on_exception == OnException.IGNORE:
                    LOG.warning(
                        f"supervisor task '{self.name}' raised {type(err).__name__} "
                        "which will be ignored",
                        exc_info=err,
                    )
                    self.complete = True
                    return
                if self.on_exception == OnException.RETRY:
                    LOG.warning(
                        f"supervisor task '{self.name}' raised {type(err).__name__} "
                        "which will be retried",
                        exc_info=err,
                    )
                    continue
                if self.on_exception == OnException.SHUTDOWN:
                    LOG.error(
                        f"supervisor task '{self.name}' raised {type(err).__name__}, "
                        "starting shutdown",
                        exc_info=err,
                    )
                    self.complete = True
                    raise get_cancelled_exc_class() from None
                assert_never(self.on_exception)

    @property
    def name(self) -> str:
        factory = self.factory
        if inspect.ismethod(factory):
            return f"{factory.__self__.__class__.__name__}.{factory.__func__.__name__}"
        if inspect.isclass(factory):
            return type(factory).__name__
        if inspect.isfunction(factory):
            return factory.__name__
        return str(factory)


class Supervisor:
    def __init__(self) -> None:
        self._tasks: list[_SupervisorTask] = []
        self._task_group: TaskGroup | None = None

    def supervise(
        self,
        func: AsyncFunction,
        *,
        on_exception: OnException = OnException.SHUTDOWN,
        shutdown_hook: AsyncFunction | None = None,
    ) -> None:
        self._tasks.append(
            _SupervisorTask(
                factory=func, on_exception=on_exception, shutdown_hook=shutdown_hook
            )
        )

    @property
    def empty(self) -> bool:
        return not self._tasks

    async def __aenter__(self) -> None:
        if not self._tasks:
            return

        self._task_group = await anyio.create_task_group().__aenter__()

        for task in self._tasks:
            LOG.info(f"supervising task: {task.name}")
            self._task_group.start_soon(task, name=task.name)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        if self._task_group:
            for task in self._tasks:
                if task.shutdown_hook is not None:
                    LOG.debug(f"supervised task shutdown hook: {task.name}")
                    await task.shutdown_hook()
            if not self._task_group.cancel_scope.cancel_called:
                self._task_group.cancel_scope.cancel()
            await self._task_group.__aexit__(exc_type, exc_value, traceback)
