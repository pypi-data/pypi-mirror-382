import threading
from ...notifications import send


STATUS_UNKNOWN = 'UNKNOWN'
STATUS_PRIMARY = 'PRIMARY'
STATUS_SECONDARY = 'SECONDARY'

NOTIFICATION_NAME = 'did_become_primary_instance'

g_status = STATUS_UNKNOWN
g_status_lock = threading.Lock()


def _set_status(new_status):
    global g_status

    with g_status_lock:
        if g_status in [STATUS_UNKNOWN, STATUS_SECONDARY] \
            and new_status == STATUS_PRIMARY:
                g_status = new_status
                send(NOTIFICATION_NAME, { 'status': STATUS_PRIMARY })

        if g_status != new_status:
            g_status = new_status


def get_instance_status():
    """Returns current status of instance priority.

    Returned value is one of STATUS_UNKNOWN, STATUS_PRIMARY, STATUS_SECONDARY.
    """
    s = None
    with g_status_lock:
        s = g_status
    return s

def set_instance_status(status:str):
    return _set_status(status)
