import numpy as np

from . import Monitor, sigmoid


class AccelMonitor(Monitor):
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
        # the sensor reports degrees/s

        # observe the last 10 values and check if the box is moving quickly

        buffer = np.array(buffer)
        buffer[abs(buffer) < 0.1] = 0

        m = np.max(buffer * 10) * np.sum(buffer * 10)

        fac = sigmoid(m / 10 - 0.1)

        self.level = m * fac + self.level * (1 - fac)

        self.threats.on_next(self.level * self.sensitivity)
