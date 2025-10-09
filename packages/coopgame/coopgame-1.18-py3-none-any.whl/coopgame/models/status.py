import time


class Status:

    def __init__(self,
                 name,
                 applied_time: float = None,
                 clear_time: float = None):
        self.name = name
        self.applied_time = applied_time if applied_time else time.clock()
        self.clear_time = clear_time


