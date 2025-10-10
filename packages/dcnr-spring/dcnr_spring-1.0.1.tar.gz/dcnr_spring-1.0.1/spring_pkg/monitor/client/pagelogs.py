import logging

loglevelnames = [
    (logging.CRITICAL, 'CRITICAL'),
    (logging.ERROR, 'ERROR'),
    (logging.WARNING, 'WARNING'),
    (logging.INFO, 'INFO'),
    (logging.DEBUG, 'DEBUG'),
    (logging.NOTSET, 'NOTSET')
]

logger = logging.getLogger(__name__)


def log_level_from_string(value):
    for ln in loglevelnames:
        if value.upper()==ln[1]:
            return ln[0]
    return logging.WARN

def loglevel_name_from_value(value):
    for ln in loglevelnames:
        if value > ln[0]:
            return f'>{ln[1]}'
        if value == ln[0]:
            return ln[1]
    return 'NOTSET'


def write_path_dict(d, path, value):
    currd = d
    for p in path:
        if 'children' in currd:
            if p not in currd['children']:
                currd['children'][p] = {
                    'children': {}
                }
            currd = currd['children'][p]
    currd['logger'] = value


def get_logger_list():
    loggers = {
        'logger': {
            'name': '[root]',
            'level': loglevel_name_from_value(logging.getLogger().level)
        },
        'children': {}
    }
    try:
        for name, lgr in logging.root.manager.loggerDict.items():
            write_path_dict(loggers, name.split('.'), {
                'name': name,
                'level': loglevel_name_from_value(lgr.level)
            })
    except Exception:
        logger.exception('get_logger_list')
    return loggers


