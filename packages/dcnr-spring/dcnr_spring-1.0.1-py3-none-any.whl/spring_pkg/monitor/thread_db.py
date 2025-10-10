import threading
from typing import Dict, Any

lck = threading.Semaphore(1)
data = {}

def _get_ident():
    if hasattr(threading, 'get_native_id'):
        return threading.get_native_id()
    else:
        return threading.get_ident()

def _get_thread_ident(t):
    if hasattr(t, 'native_id'):
        return t.native_id
    else:
        return t.ident

def get_thread_record() -> Dict:
    tr = None
    with lck:
        tid = _get_ident()
        data.setdefault(tid, {})
        tr = data[tid]
    return tr

def get_live_threads():
    live = {}
    with lck:
        current_data_keys = list(data.keys())
        for t in threading.enumerate():
            t_ident = _get_thread_ident(t)
            if t_ident in data and 'correlationId' in data[t_ident]:
                live[t_ident] = data[t_ident]
                current_data_keys.remove(t_ident)

        for a in current_data_keys:
            data[a] = {}

    return live

def save_thread_data(key, value):
    data = get_thread_record()
    data[key] = value

def get_thread_data(key, default='') -> Any:
    data = get_thread_record()
    return data.get(key) or default
