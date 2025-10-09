import asyncio
from asyncio import Queue, AbstractEventLoop
from typing import Optional
from threading import Event

from ._task import Task


class TaskQueue:
    """
    An asyncio.Queue confined to a single (owning) event loop, but usable
    from *any* loop or thread via cross-loop marshaling.
    """

    def __init__(self) -> None:
        self._loop: Optional[AbstractEventLoop] = None
        self._q: Optional[Queue[Task]] = None
        self._started = Event()
        self._stopped = Event()

    async def start(self) -> None:
        """
        Initialize the queue inside the running (owning) loop.
        Must be awaited from the target loop/thread that will own the queue.
        """
        self._loop = asyncio.get_running_loop()
        self._q = asyncio.Queue()
        self._started.set() # unlock the queue

    # ----------------------------
    # Async API usable from ANY loop
    # ----------------------------

    async def put(self, item: Task) -> None:
        """
        Works when called from the owning loop OR any other event loop.
        If called from a foreign loop, the operation is marshaled to the owning loop.
        """
        self._started.wait() # secure that the queue is started
        assert self._loop is not None and self._q is not None
        # Foreign loop: marshal to owning loop and await the cross-loop future.
        fut = asyncio.run_coroutine_threadsafe(self._q.put(item), self._loop)
        await asyncio.wrap_future(fut)

    async def get(self) -> Task:
        """
        Works when called from the owning loop OR any other event loop.
        If called from a foreign loop, the operation is marshaled to the owning loop.
        """
        self._started.wait() # secure that the queue is started
        assert self._loop is not None and self._q is not None
        fut = asyncio.run_coroutine_threadsafe(self._q.get(), self._loop)
        return await asyncio.wrap_future(fut)