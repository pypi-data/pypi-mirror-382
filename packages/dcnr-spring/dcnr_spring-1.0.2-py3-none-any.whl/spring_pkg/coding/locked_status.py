import threading
from typing import Generic, TypeVar

T = TypeVar('T')

class LockedValue(Generic[T]):
    """
    generic thread-safe value. It is useful for scalar values like bool, int, str, etc.
    but collections like list, dict, set are not thread-safe even 
    if wrapped in this class.

    However the reference to the collection is thread-safe.

    Example:
    ```python
        status = LockedValue[bool](False)
        status.set(True)
        print(status.get())  # True
    ```
    """
    def __init__(self, initial: T):
        self.value = initial
        self.lock = threading.Lock()

    def set(self, value: T):
        with self.lock:
            self.value = value

    def get(self) -> T:
        with self.lock:
            return self.value