from ._pool import WorkerPool

def create_worker_app(concurrency:int) -> WorkerPool:
    return WorkerPool(concurrency=concurrency)