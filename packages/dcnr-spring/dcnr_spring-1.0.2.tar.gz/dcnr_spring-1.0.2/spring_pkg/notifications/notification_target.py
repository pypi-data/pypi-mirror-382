from dataclasses import dataclass


@dataclass
class NotificationTarget:
    target: callable
    userdata: any
    id: int