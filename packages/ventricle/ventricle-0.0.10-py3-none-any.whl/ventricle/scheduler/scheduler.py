from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler:

    def __init__(self):
        self._scheduler = BackgroundScheduler()

    def start(self):
        self._scheduler.start()