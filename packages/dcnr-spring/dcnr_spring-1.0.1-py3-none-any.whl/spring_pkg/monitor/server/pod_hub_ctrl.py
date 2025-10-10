import threading, datetime
import time
from multiprocessing import SimpleQueue
from .pod_hub_data import ph_put, ai_get_app, PodHubApplication

proc_queue = SimpleQueue()
proc_lock = threading.Lock()
proc_thread = None

def _pod_hub_process():
    while True:
        if proc_queue.empty():
            time.sleep(5)
            continue
        cmd, args = proc_queue.get()
        if cmd == 'pod-hub-info':
            ph_put(args)

def receive_pod_hub_info(body:dict) -> str:
    """

    Usage

    ```python
    from flask import Flas, request

    app = Flask(__name__)

    def _receive_pod_hub_info():
        req = request.get_json()
        return receive_pod_hub_info(req)

    app.add_url_rule('/pod-hub', '/pod-hub', _receive_pod_hub_info, methods=['POST'])
    ```

    """
    try:
        for key in ['application', 'instance', 'instance-status', 'start-time']:
            if key not in body:
                return f'Missing key {key}'
        body['received'] = datetime.datetime.now()
        proc_queue.put(('pod-hub-info', body))
        app:PodHubApplication = ai_get_app(body['application'])
        if app.pip.should_ask_data() and 'pip' not in body:
            return 'pip'
        elif app.codepoints.should_ask_data():
            return 'codepoints'
        return 'OK'
    except Exception as x:
        return str(x)

def register_endpoints():
    """
    Usage: ontime initialization during the start of service

    register_endpoints()
    """
    global proc_thread

    with proc_lock:
        if proc_thread is None:
            proc_thread = threading.Thread(target=_pod_hub_process)
            proc_thread.start()
