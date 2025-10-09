import asyncio
from ._task_queue import TaskQueue
from ._worker import Worker


class HeadWorker(Worker):
    """
        Coordinating Worker Thread. Owns the managing event loop.
    """

    def __init__(self, queue: TaskQueue) -> None:
        super().__init__(queue)

    async def _run_async(self):
        await self.queue.start()
        await asyncio.Event().wait()
