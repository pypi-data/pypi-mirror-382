import requests
import datetime
import time
import os
import threading, logging
import socket
from ...subprocess import is_subprocess
from ...coding import LockedValue
from .methods import get_instance_status
from .main_api import resolve_api_data

_podhub_sync_thread = LockedValue[threading.Thread](None)
_podhub_session = LockedValue[requests.Session](None)
_podhub_url = LockedValue[str](None)
_podhub_outgoing_data = LockedValue[list](None)
_podhub_start = LockedValue[str](datetime.datetime.now().isoformat())
_podhub_appname = LockedValue[str](socket.gethostname())
_podhub_stop_requested = LockedValue[bool](False)

logger = logging.getLogger(__name__)


def set_application_name(name:str):
    _podhub_appname.set(name)

def set_server_url(url:str):
    _podhub_url.set(url)
    _podhub_session.set(None)

def _get_session():
    with _podhub_session.lock:
        if _podhub_session.value is None:
            _podhub_session.value = requests.Session()
    return _podhub_session.get()

def _pod_hub_enhance_info(_data, cmd):
    try:
        value = resolve_api_data(cmd)
        if value:
            _data[cmd] = value
    except Exception:
        logger.exception(f'Exception in getting {cmd} data...')

def _pod_hub_send_signal():
    try:
        session = _get_session()
        _data = {
            'application': _podhub_appname.get(),
            'instance': socket.gethostname(),
            'instance-status': get_instance_status(),
            'start-time': _podhub_start.get(),
        }
        with _podhub_outgoing_data.lock:
            for cmd in _podhub_outgoing_data.value or []:
                _pod_hub_enhance_info(_data, cmd)
            _podhub_outgoing_data.value = []
        r = session.post(_podhub_url.get(), json=_data)
        if r.text in ['codepoints', 'pip']:
            with _podhub_outgoing_data.lock:
                _podhub_outgoing_data.value.append(r.text)
        if r.text == 'OK':
            logger.debug('Signal sent and received.')
    except Exception:
        logger.exception('Sending signal EXC')

def start_pod_hub():
    def _pod_hub_loop():
        seconds = 0
        while _podhub_stop_requested.get() == False:
            time.sleep(1)
            if seconds%30 == 0:
                _pod_hub_send_signal()
            seconds = (seconds+1)%60
        _podhub_stop_requested.set(False)

    if is_subprocess():
        logger.warning('Subprocess mode detected, pod_hub will not be started.')
        return
    
    with _podhub_sync_thread.lock:
        if _podhub_sync_thread.value is None:
            _podhub_sync_thread.value = threading.Thread(target=_pod_hub_loop)
            _podhub_sync_thread.value.start()
            logger.warning('starting the pod_hub loop')
        else:
            logger.warning(f'pod_hub already started')

def stop_pod_hub():
    _podhub_stop_requested.set(True)