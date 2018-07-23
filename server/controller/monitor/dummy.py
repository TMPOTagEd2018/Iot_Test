from rx import Observable, Observer
from rx.core import ObservableBase
from rx.subjects import Subject
from rx.linq.observable import window

from datetime import datetime
from threading import Timer
from time import sleep

import numpy as np

from . import Monitor


class DummyMonitor(Monitor):
    timer: Timer

    def __init__(self):
        super().__init__()
        self.timer = Timer(1, self.handler)
        self.timer.start()

    def handler(self):
        while True:
            self.threats.on_next(1)
            sleep(1)
