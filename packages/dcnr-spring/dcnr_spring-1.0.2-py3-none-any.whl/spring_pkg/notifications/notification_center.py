import threading
from .notification_data import NotificationData


class NotificationCenter:
    lock: threading.Lock = threading.Lock()
    notifications: dict[str,NotificationData] = {}
    id: int = 1

