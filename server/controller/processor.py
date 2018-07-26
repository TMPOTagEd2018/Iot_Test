from rx import Observable
from rx.core import Disposable

import sqlite3

import threading

import numpy as np
from monitor import sigmoid


class ThreatProcessor:
    prev_score: float = 0

    def __init__(self, threats: [Observable], callback, sensitivity: float):
        self.db_lock = threading.Lock()
        self.threats = threats
        self.callback = callback
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

        # prevent massive db overload from minute numerical jitter
        if round(self.prev_score, 1) != round(threat_score, 1):
            self.callback(threat_score)
            
        self.prev_score = threat_score
