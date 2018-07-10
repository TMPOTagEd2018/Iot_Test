from rx import Observable
from rx.core import Disposable

import sqlite3
import time

import numpy as np
from datetime import datetime as dt

import colorama as cr
cr.init(autoreset=True)

class ThreatProcessor:
    prev_score: float = 0

    def __init__(self, threats, sensitivity):
        self.threats = threats
        self.sensitivity = sensitivity
        self.query = self.threats.buffer_with_count(sensitivity, sensitivity - 1)
        self.subscription = self.query.subscribe(self.on_threat)

    def on_threat(self, buffer: [int]):
        if -1 in buffer:
            prev_score = 0
            buffer = [0]

        threat_score = (np.sum(buffer) + np.max(buffer)) / (np.std(buffer) + 1) / self.sensitivity * 2

        if int(threat_score) == int(self.prev_score):
            return

        with sqlite3.connect("data.db") as conn: # type: sqlite3.Connection
            conn.execute(f"INSERT INTO threats VALUES (?, ?, ?, ?, ?)", (int(time.time()), None, None, int(self.prev_score), int(threat_score)))

        self.prev_score = threat_score