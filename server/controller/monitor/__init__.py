from rx.subjects import Subject, BehaviorSubject


class Monitor:
    def __init__(self):
        self.data: Subject = Subject()
        self.threats: BehaviorSubject = BehaviorSubject(0)

    def dispose(self):
        if self.query is not None:
            self.query.dispose()
