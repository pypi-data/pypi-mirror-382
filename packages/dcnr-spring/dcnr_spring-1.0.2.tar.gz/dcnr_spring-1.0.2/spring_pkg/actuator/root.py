import json
from datetime import datetime
from typing import Any, Dict, List, Callable

STATUS_OK = 'UP'
STATUS_FAIL = 'DOWN'
STATUS_UNKNOWN = 'NA'

_glob_pages = {}


def is_ok(page_name:str):
    """Checks if the given actuator component is in OK status."""
    if page_name in _glob_pages:
        func = (_glob_pages.get(page_name) or {})
        resp = func()
        return resp.get('status', 'NA') == STATUS_OK
    return True

def register_actuator_component(page_name:str, callback:Callable[[],Dict[str,Any]]):
    """Registers a new actuator component with the given name and 
    callback function. The callback function should return a dictionary with 
    the status of the component.


    Example of return value from callback function:

    {
        'status': 'UP'
    }

    
    Another example containing also details about the component:

    {
        'status': 'UP',
        'details': {
            'total': 1234567890,
            'free': 987654321,
            'exists': True,
            'path': '/opt/app/.'
        }
    }


    """
    _glob_pages[page_name] = callback

def on_actuator_root():
    return on_actuator_endpoint('')

def get_actuator_components():
    return _glob_pages.keys()

def get_component_response(page_name:str):
    callback = _glob_pages.get(page_name)
    if callback is not None:
        resp = callback()
    else:
        resp = None

    if resp is None:
        resp = {
            'status': 'NA'
        }
    return resp

def on_actuator_endpoint(path:str):
    resp = {}
    if path is None or path == '':
        resp = {
            'status': 'UP',
            'groups': [
                'liveness',
                'readiness'
            ],
            'components': {k:v() for k,v in _glob_pages.items()}
        }
    elif path in _glob_pages:
        resp = _glob_pages[path]()
    else:
        resp = {}

    return resp
