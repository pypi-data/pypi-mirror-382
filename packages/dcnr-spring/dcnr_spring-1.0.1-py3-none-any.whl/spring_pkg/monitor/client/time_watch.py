import threading
import datetime
from operator import itemgetter

_data_lock = threading.Lock()
_data = {}


def codepoint_log(path:str, msg=None, timestamp=None):
    with _data_lock:
        if isinstance(timestamp,datetime.datetime):
            timestamp = timestamp.isoformat()
        else:
            timestamp = datetime.datetime.now().isoformat()
        _data[path] = (timestamp, msg)


def _cp_write_path_dict(d, path, value):
    currd = d
    for p in path:
        if 'children' in currd:
            if p not in currd['children']:
                currd['children'][p] = {
                    'children': {}
                }
            currd = currd['children'][p]
    currd['code_point'] = value


def codepoints_get_tree():
    code_points = {
        'code_point': {
            'name': '[root]',
            'time': None,
            'msg': None
        },
        'children': {}
    }

    with _data_lock:
        for key, val in _data.items():
            _cp_write_path_dict(code_points, key.split('.'), {
                'name': key,
                'time': val[0],
                'msg': val[1]
            })

    return code_points

def codepoints_get_list():
    p = []
    with _data_lock:
        for key, val in _data.items():
            p.append({
                'name': key,
                'time': val[0],
                'msg': val[1]
            })

    return sorted(p, key=itemgetter('time'), reverse=True)
