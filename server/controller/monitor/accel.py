import numpy as np

from . import Monitor, sigmoid


class AccelMonitor(Monitor):
    def __init__(self, sensitivity=1):
        super().__init__()

        self.sensitivity = sensitivity

        self.query = self.data \
            .map(int) \
            .buffer_with_count(30, 5) \
            .subscribe(self.handler)

        self.level = 0

    def input(self, value):
        self.data.on_next(value)

    def handler(self, buffer: [int]):
        # the sensor reports degrees/s

        # observe the last 10 values and check if the box is moving quickly

        buffer = np.array(buffer, dtype=np.float)
        buffer = abs(buffer)

        # anything less than 1 m/s2 is ignored
        # anything greater than 1 m/s2

        m = np.max(buffer) * (np.std(buffer) + 1)

        self.level = sigmoid(m) * 2 - 1

        self.threats.on_next(self.level * self.sensitivity)
