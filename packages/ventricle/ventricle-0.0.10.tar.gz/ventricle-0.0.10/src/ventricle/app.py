from typing import Optional

import uvicorn

from .rest import create_rest_app
from .scheduler import create_schedular_app
from .worker import create_worker_app


class Ventricle:

    def __init__(self,
                 title: str = "Ventricle",
                 rest_root_path: str = "",
                 worker_concurrency: int = 16,
                 redis_url: Optional[str] = None,
                 amqp_url: Optional[str] = None
                 ):
        """
        The ventricle app.
        :param title: The title of the application.
        :param rest_root_path: The base path of the REST API.
        :param worker_concurrency: The number of worker processes to run in parallel.
        :param redis_url: The redis url to connect to. Some services may not work if not provided.
        :param amqp_url: The amqp url to connect to. Some services may not work if not provided.
        """
        self.rest = create_rest_app(title=title, root_path=rest_root_path)
        self.scheduler = create_schedular_app()

        assert worker_concurrency > 0, "Worker concurrency must be greater than 0."
        self.worker = create_worker_app(worker_concurrency)

        # todo validate the urls
        self.REDIS_URL = redis_url
        self.AMQP_URL = amqp_url

    def start(self, rest: bool = True, schedular: bool = True, worker: bool = True, host: str = "0.0.0.0",
              port: int = 8000) -> None:
        """
        Start the Ventricle app.
        :param rest: If the REST server should be started.
        :param schedular: If the scheduler should be started.
        :param worker: If the worker should be started.
        :param host: The host to connect to.
        :param port: The port to connect to.
        :return: None
        """
        if schedular:
            self.scheduler.start()

        if worker:
            self.worker.start()

        if rest:
            uvicorn.run(
                self.rest,
                host=host,
                port=port
            )
