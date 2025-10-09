from functools import wraps
from typing import Callable, Awaitable, Any

from ._task import Task
from ._task_queue import TaskQueue
from ._worker import Worker
from ._head import HeadWorker


class WorkerPool:

    def __init__(self, concurrency: int):
        """
        The main worker pool class.
        :param concurrency: The number of concurrency workers.
        """

        # initialize the worker queue
        self._worker_queue = TaskQueue()

        # initialize the worker
        self._head_worker = HeadWorker(self._worker_queue)
        self._workers = [Worker(self._worker_queue) for _ in range(concurrency)]

    def start(self) -> None:
        """
        Start the worker pool.
        :return: None
        """
        self._head_worker.start()
        for worker in self._workers:
            worker.start()

    def join(self) -> None:
        """
        Block until all workers are done.
        :return: None
        """
        self._head_worker.join()
        for worker in self._workers:
            worker.join()

    def task(self, func: Callable[..., Awaitable[Any]]):
        """
        Task decorator.
        :param func: The function to be executed.
        :return: None
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # create the task object and put it in the execution queue
            task = Task(func=func, args=args, kwargs=kwargs)
            await self._worker_queue.put(task)
            return None

        return wrapper
