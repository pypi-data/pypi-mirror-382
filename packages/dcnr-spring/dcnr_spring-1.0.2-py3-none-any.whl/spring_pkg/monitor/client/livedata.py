import datetime
from typing import List
from ...coding import LockedValue


_livedata = LockedValue[dict]({})
_livedata_limits = LockedValue[dict]({})

def livedata_setlimit(tag:str, limit:int):
    with _livedata_limits.lock:
        if tag not in _livedata_limits.value:
            _livedata_limits.value[tag] = []

def livedata_log(tag:str, level:str, message:str, exception:Exception=None):
    with _livedata.lock:
        if tag not in _livedata.value:
            _livedata.value[tag] = []
        entry = {
            'level': level,
            'datetime': datetime.datetime.now(),
            'message': message
        }
        if exception is not None:
            entry['exception'] = str(exception)
        _livedata.value[tag].insert(0, entry)
        limit = _livedata_limits.value.get(tag) or 50
        while len(_livedata.value[tag])>limit:
            _livedata.value[tag].pop()

def livedata_page():
    buff = []
    with _livedata.lock:
        for key,items in _livedata.value.items():
            if len(items)==0:
                continue
            buff.append({
                'logname': key,
                'items': list(items)
            })
    return buff
