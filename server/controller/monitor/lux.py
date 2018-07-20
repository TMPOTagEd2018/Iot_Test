import numpy as np

from . import Monitor


class LuxMonitor(Monitor):
    def __init__(self, sensitivity=1):
        super().__init__()

        self.sensitivity = sensitivity

        self.query = self.data \
            .map(int) \
            .buffer_with_count(10, 5) \
            .subscribe(self.handler)

    def input(self, value):
        self.data.on_next(value)

    def handler(self, buffer: [int]):
        # the sensor reports degrees/s

        # observe the last 10 values and check if contact is over

        m = np.sum(buffer * np.arange(0, 1, 1 / len(buffer))) / len(buffer) / 50

        self.threats.on_next(m * self.sensitivity)
