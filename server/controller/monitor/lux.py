import numpy as np

from . import Monitor, sigmoid


class LuxMonitor(Monitor):
    def __init__(self, sensitivity=1):
        super().__init__()

        self.sensitivity = sensitivity

        self.query = self.data \
            .map(int) \
            .buffer_with_count(10, 5) \
            .subscribe(self.handler)

        self.level = 0

    def input(self, value):
        self.data.on_next(value)

    def handler(self, buffer: [int]):
        buffer = np.array(buffer, dtype=np.float)

        self.level = np.sum(buffer[buffer > 127]) / 255 / 10

        self.threats.on_next(self.level * self.sensitivity)
