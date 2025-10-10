from functools import wraps
from time import sleep
from threading import Lock

__all__ = ['message_counter', 'get_count', 'wait_for_empty']

_mq_count = {
    'lock': Lock(),
    'count': 0
}


def message_counter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with _mq_count['lock']:
            _mq_count['count'] += 1
        try:
            return func(*args, **kwargs)
        finally:
            with _mq_count['lock']:
                _mq_count['count'] -= 1
                if _mq_count['count']<0:
                    _mq_count['count'] = 0
    return wrapper

def get_count():
    global _mq_count
    with _mq_count['lock']:
        return _mq_count['count']
    
def wait_for_empty(timeout=60):
    tc = 0
    sleep(5)
    while get_count()>0 and tc<timeout:
        tc += 1
        sleep(1)