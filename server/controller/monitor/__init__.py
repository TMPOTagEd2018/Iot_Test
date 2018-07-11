from rx.core import Disposable
from rx.subjects import Subject

class Monitor:
    def __init__(self):
        self.data: Subject = Subject()
        self.threats: Subject = Subject()
    
    def dispose(self):
        if self.query is not None:
            self.query.dispose()