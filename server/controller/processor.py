from rx import Observable
from rx.core import Disposable

import sqlite3
import time

import numpy as np

import colorama as cr
cr.init(autoreset=True)


class ThreatProcessor:
    prev_score: float = 0

    def __init__(self, threats: Observable, sensitivity):
        self.threats = threats
        self.sensitivity = sensitivity
        self.query = self.threats.combine_latest(lambda *data: data)
        self.subscription: Disposable = self.query.subscribe(self.on_threat)

    def on_threat(self, buffer: [int]):
        if -1 in buffer:
            self.prev_score = 0
            buffer = [0]

        threat_score = (np.sum(buffer) + np.max(buffer)) / \
            (np.std(buffer) + 1) / self.sensitivity * 2
        # threat_score += ((threat_score - self.prev_score) * .25) * 0.1

        # if abs(threat_score - self.prev_score) < 0.1:
        #    return

        with sqlite3.connect("data.db") as conn:  # type: sqlite3.Connection
            t = round(time.time(), 3)
            ps = round(self.prev_score, 1)
            ts = round(threat_score, 1)
            conn.execute(f"INSERT INTO threats VALUES ({t}, NULL, NULL, {ps}, {ts})")

        self.prev_score = threat_score
