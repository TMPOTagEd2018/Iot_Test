from rx.subjects import Subject, BehaviorSubject
import numpy as np


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


class Monitor:
    def __init__(self):
        self.data: Subject = Subject()
        self.threats: BehaviorSubject = BehaviorSubject(0)

    def dispose(self):
        if self.query is not None:
            self.query.dispose()
