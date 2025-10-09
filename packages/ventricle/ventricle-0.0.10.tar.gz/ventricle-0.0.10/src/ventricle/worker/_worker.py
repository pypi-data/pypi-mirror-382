import asyncio
import threading
from ._task_queue import TaskQueue


class Worker(threading.Thread):

    def __init__(self, queue: TaskQueue):
        """
        The Worker Object.
        :param queue: The queue to get the tasks from.
        """
        super().__init__()
        self.queue = queue

    def run(self):
        asyncio.run(self._run_async())

    async def _run_async(self):
        while True:
            task = await self.queue.get()
            try:
                await task.func(*task.args, **task.kwargs)
            except Exception as e:
                print(e) # todo replace with logging

