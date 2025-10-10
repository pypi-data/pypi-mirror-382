import datetime
from typing import Optional
import threading


class PodHubInfo:
    def __init__(self, exp_req=None, exp_sec=None):
        self.last_received:Optional[datetime.datetime] = None
        self.last_asked:Optional[datetime.datetime] = None
        self.last_lock = threading.Lock()
        self.data:Optional[dict] = None
        self.expiration_sec = exp_sec or 86400
        self.expiration_request = exp_req or 300

    def set_data(self, data):
        with self.last_lock:
            self.data = data
            self.last_received = datetime.datetime.now()
        return self

    def get_data(self):
        with self.last_lock:
            return self.data

    def should_ask_data(self):
        curr_time = datetime.datetime.now()
        with self.last_lock:
            if self.last_received is None:
                if self.last_asked is None:
                    return True
                diff:datetime.timedelta = (curr_time - self.last_asked)
                if diff.total_seconds() > self.expiration_request:
                    self.last_asked = curr_time
                    return True
                else:
                    return False
            else:
                diff:datetime.timedelta = (curr_time - self.last_received)
                if diff.total_seconds() > self.expiration_sec:
                    return True
                return False