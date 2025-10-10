import logging
import threading
import datetime
from typing import List, Optional
from .podhub_data import PodHubData
from .podhub_app import PodHubApplication

ph_data_lock = threading.Lock()
ph_data:List[PodHubData] = []

ai_data_lock = threading.Lock()
ai_data:dict = {}

logger = logging.getLogger(__name__)


def _ph_get_unique(data):
    with ph_data_lock:
        for d in ph_data:
            if d.application == data['application'] and d.instance == data['instance']:
                d.instance_status = data['instance-status']
                d.received = data['received']
                return d
        d = PodHubData(application=data['application'],
                    instance=data['instance'],
                    instance_status=data['instance-status'],
                    start_time=data['start-time'],
                    received=data['received'])
        ph_data.insert(0, d)
        return d

def _ph_remove_old():
    global ph_data
    last_time = datetime.datetime.now() - datetime.timedelta(seconds=65)
    with ph_data_lock:
        new_ph = []
        for a in ph_data:
            if a.received > last_time:
                new_ph.append(a)
        ph_data = new_ph

"""
app_package:
  id: serial8 NOTNULL PRIMARY
  create_d: timestamp NOTNULL DEFAULT:CURRENT_TIMESTAMP INDEX
  application_name: text INDEX
  pkg_name: text
  version: text

app_package_changes:
  id: serial8 NOTNULL PRIMARY
  application_name: text INDEX
  create_d: timestamp NOTNULL DEFAULT:CURRENT_TIMESTAMP INDEX
  pkg_name: text
  old_version: text
  new_version: text
"""

def ai_check_pkg_changes(app:PodHubApplication, raw_list:dict):
    latest = {a['name']:a['version'] for a in raw_list.values()}
    app.check_current_pkgs(latest)
    changes = app.get_pkgs_differences(latest)
    app.save_pkg_differences(changes)


def ph_put(data:dict):
    try:
        _ph_get_unique(data)
        _ph_remove_old()
        if 'pip' in data:
            app:PodHubApplication = ai_get_app(data['application'])
            app.pip.set_data(data['pip'])
            ai_check_pkg_changes(app, data['pip'])
        if 'codepoints' in data:
            app:PodHubApplication = ai_get_app(data['application'])
            app.codepoints.set_data(data['codepoints'])
    except Exception:
        logger.exception('ph_put')

def ai_get_app(app_name:str) -> PodHubApplication:
    with ai_data_lock:
        if app_name not in ai_data:
            ai_data[app_name] = PodHubApplication(application=app_name)
        return ai_data[app_name]

def get_app_instances(app:str) -> List[str]:
    """
    Returns list of existing instances in Kubernetes cluster for given application
    """
    inst:List[str] = []
    with ph_data_lock:
        for p in ph_data:
            if p.application == app and p.instance not in inst:
                inst.append(p.instance)
    return list(inst)


def get_live_services():
    data = []
    with ph_data_lock:
        for p in ph_data:
            data.append({
                'application': p.application,
                'instance': p.instance,
                'instance_status': p.instance_status,
                'start_time': p.start_time
            })

    data = sorted(data, key=lambda a: a['application'])
    return data

def _get_safe_list(arg):
    if not isinstance(arg,list):
        return []
    return [a for a in arg if a is not None and len(a)>0]

def _enum_codepoints(arr, data, name, level=0):
    if 'code_point' in data:
        cp = data['code_point']
        arr.append({
            'level': level,
            'name': name,
            'time': cp.get('time'),
            'msg': cp.get('msg')
        })
    else:
        arr.append({
            'level': level,
            'name': name,
            'time': '',
            'msg': ''
        })
    if 'children' in data:
        for key, value in data['children'].items():
            _enum_codepoints(arr, value, key, level+1)

def _enum_codepoints_flat(arr, data):
    if 'code_point' in data:
        cp = data['code_point']
        time_str = cp.get('time') or 'T'
        arr.append({
            'name': cp.get('name'),
            'time': time_str,
            'timeh': time_str.split('T'),
            'msg': cp.get('msg')
        })
    if 'children' in data:
        for _, value in data['children'].items():
            _enum_codepoints_flat(arr, value)


def get_app_pips(app_name:str):
    data = {
        "app_name": app_name,
        "instances": get_app_instances(app_name),
        "packages": []
    }

    app = ai_get_app(app_name)
    data_pip = app.pip.get_data()
    if data_pip is not None:
        new_pips = []
        for name, old_pip in data_pip.items():
            new_pips.append({
                'name': name,
                'version': old_pip['version'],
                'depending': _get_safe_list(old_pip.get('requires')),
                'required_by': _get_safe_list(old_pip.get('required-by'))
            })
        data['packages'] = new_pips

    data['changes'] = app.get_changes()

    data_cp = app.codepoints.get_data()
    if data_cp is not None:
        new_cp = []
        _enum_codepoints(new_cp, data_cp, 0)
        data['codepoints'] = new_cp

        flat_cp = []
        _enum_codepoints_flat(flat_cp, data_cp)
        flat_cp = sorted(flat_cp, key=lambda a:a.get('time'), reverse=True)
        data['cpflat'] = flat_cp

    return data