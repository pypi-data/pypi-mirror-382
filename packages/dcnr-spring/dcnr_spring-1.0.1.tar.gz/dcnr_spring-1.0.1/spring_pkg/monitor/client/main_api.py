from .pagelogs import get_logger_list
from .livedata import livedata_page
from .pip_pkgs import get_pip_packages
from .time_watch import codepoints_get_tree


_methods = [
    {
        'title': 'Python Loggers',
        'api': 'loggers',
        'description': 'Python loggers and logging levels.',
        'func': get_logger_list
    },
    {
        'title': 'Python Packages',
        'api': 'pip',
        'description': 'Installed python packages.',
        'func': get_pip_packages
    },
    {
        'title': 'Live messages',
        'api': 'livedata',
        'description': 'Recent messages from service.',
        'func': livedata_page
    },
    {
        'title': 'Codepoints',
        'api': 'codepoints',
        'description': 'Codepoints with timestamps.',
        'func': codepoints_get_tree
    }
]

def on_main(path):
    if path is None or path in ['', 'index']:
        return _methods

    for m in _methods:
        if m['api'] == path and 'func' in m:
            return m['func']()

    return 'Unknown resource', 400

def register_api(title:str, api:str, description:str, func:callable):
    _methods.append({
        'title': title,
        'api': api,
        'description': description,
        'func': func
    })

def resolve_api_data(api:str):
    for m in _methods:
        if m['api'] == api and 'func' in m:
            return m['func']()
    return None
