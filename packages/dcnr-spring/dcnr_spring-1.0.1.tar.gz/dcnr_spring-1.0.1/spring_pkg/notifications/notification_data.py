from dataclasses import dataclass
from typing import List
from .notification_target import NotificationTarget

@dataclass
class NotificationData:
    clients: List[NotificationTarget]