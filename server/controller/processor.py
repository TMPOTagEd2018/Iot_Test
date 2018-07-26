from rx import Observable
from rx.core import Disposable

import sqlite3
import time

import threading

import numpy as np
from monitor import sigmoid


class ThreatProcessor:
    prev_score: float = 0

    def __init__(self, threats: [Observable], conn: sqlite3.Connection, sensitivity: float):
        self.db_lock = threading.Lock()
        self.threats = threats
        self.conn = conn
        self.sensitivity = sensitivity
        self.query = Observable.combine_latest(threats, lambda *data: data)
        self.subscription: Disposable = self.query.subscribe(self.on_threat)

    def on_threat(self, buffer: [int]):
        if -1 in buffer:
            self.prev_score = 0
            buffer = [0]

        std = np.std(buffer)
        b_max = np.max(buffer)

        threat_score = (np.sum(buffer) + b_max) / \
            (sigmoid(std / (b_max + 1)) * std + 1)
        fac = sigmoid((threat_score - self.prev_score) * 2.7)
        threat_score = threat_score * fac + self.prev_score * (1 - fac)

        t = round(time.time(), 3)
        ps = round(self.prev_score, 1)
        ts = round(threat_score, 1)

        self.prev_score = threat_score

        # prevent massive db overload from minute numerical jitter
        if ps == ts:
            return

        self.conn.execute(f"INSERT INTO threats VALUES ({t}, NULL, NULL, {ps}, {ts})")

        if self.db_lock.acquire(blocking=False):
            try:
                self.conn.commit()
            finally:
                self.db_lock.release()
