import threading


class SafeCounter:
    def __init__(self):
        self._count = 0
        self._count_lock = threading.Lock()

    def increment(self):
        with self._count_lock:
            self._count += 1

    def decrement(self):
        with self._count_lock:
            self._count -= 1

    def count(self):
        return self._count

