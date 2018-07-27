from rx import Observable
from rx.core import Disposable

import numpy as np
from monitor import sigmoid


class ThreatProcessor:
    prev_score: float = 0
    prev_score_write: float = 0

    def __init__(self, threats: [Observable], callback=None):
        self.threats = threats
        self.on_threat = callback
        self.query = Observable.combine_latest(threats, lambda *data: data)
        self.subscription: Disposable = self.query.subscribe(self.process)
        self.on_threat = None

    def update(self):
        self.subscription.dispose()
        self.query = Observable.combine_latest(self.threats, lambda *data: data)
        self.subscription: Disposable = self.query.subscribe(self.process)

    def process(self, buffer: [int]):
        if -1 in buffer:
            self.prev_score = 0
            buffer = [0]

        buffer = np.array(buffer)
        bsum = np.sum(buffer)

        # threat_score = (np.average(b_s) + np.max(b_s)) * 5

        fac = sigmoid((bsum - self.prev_score) * 10)
        fac = max(fac, 2e-4)
        threat_score = bsum * fac + self.prev_score * (1 - fac)

        print(*buffer, threat_score, self.prev_score, fac, sep=",")

        # prevent massive db overload from minute numerical jitter
        if round(self.prev_score_write, 1) != round(threat_score, 1) and self.on_threat is not None:
            self.on_threat(threat_score)
            self.prev_score_write = threat_score

        self.prev_score = threat_score
