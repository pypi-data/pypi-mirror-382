import time
import threading
from ..notifications import send

signal_exit = threading.Event()

def waitloop_start():
    """
    Infinity loop for waiting for signals or interruptions.
    This should be run only on main thread to correctly receive
    keyboard interruption.
    """
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        send('waitloop-did-finish', {'reason': 'KeyboardInterrupt'})
        signal_exit.set()

def waitloop_is_at_exit():
    """
    Use this function in other threads and other loops to indicate
    when exit from the application is requested.
    """
    return signal_exit.is_set()
