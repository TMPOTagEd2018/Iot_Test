from threading import Timer
from time import sleep
import random

from . import Monitor


class HeartbeatMonitor(Monitor):
    level = 0
    timer: Timer

    def __init__(self, shared_key, sensitivity=1):
        super().__init__()

        self.init(shared_key)

        self.timer = Timer(3, self.handler)
        self.timer.start()
        self.sensitivity = sensitivity

    def init(self, shared_key):
        random.seed(int(shared_key, 16))
        self.rng = random.getstate()

    def input(self, value):
        if value == -1:
            # sensor failure! do nothing, for now
            return

        random.setstate(self.rng)
        check = random.getrandbits(32)
        if check != int(value):
            return

        self.rng = random.getstate()

        self.threats.on_next(0)
        self.level = 0
        self.reset()

    def handler(self):
        while True:
            self.threats.on_next(self.level * self.sensitivity)
            self.level = min(self.level + 1, 3)
            sleep(10)

    def reset(self):
        self.level = 0
