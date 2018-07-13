from threading import Timer

from . import Monitor


class HeartbeatMonitor(Monitor):
    level = 0
    timer: Timer

    def __init__(self, sensitivity=1):
        super().__init__()
        self.timer = Timer(3, self.handler)
        self.sensitivity = sensitivity

    def input(self, value):
        self.threats.on_next(0)
        self.reset()

    def handler(self):
        self.level = min(self.level + 1, 3)
        self.threats.on_next(self.level * self.sensitivity)
        self.reset()

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(3, self.handler)
        self.timer.start()
