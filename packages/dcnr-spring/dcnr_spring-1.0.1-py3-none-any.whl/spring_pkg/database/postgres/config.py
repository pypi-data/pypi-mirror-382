import os


DB_CONFIG_ENV_VARs = {
    'name': 'PDB_NAME',
    'user': 'PDB_USER',
    'password': 'PDB_PWD',
    'host': 'PDB_HOST',
    'port': 'PDB_PORT',
    'schema': 'PDB_SCHEMA'
}

def _get_dummy_configuration(schema=None):
    creds = {
        "host": os.environ.get(DB_CONFIG_ENV_VARs['host'], 'localhost'),
        "port": os.environ.get(DB_CONFIG_ENV_VARs['port'], "5432"),
        "database": os.environ.get(DB_CONFIG_ENV_VARs['name'], 'postgres'),
        "user": os.environ.get(DB_CONFIG_ENV_VARs['user'], 'postgres'),
        "password": os.environ.get(DB_CONFIG_ENV_VARs['password'], 'postgres')
    }
    return creds

get_configuration = _get_dummy_configuration
get_configuration.__doc__ = """
    Get the current database configuration from environment variables.
    Returns a dictionary with keys: host, port, database, user, password.
    """

def set_configuration_envs(**kwargs):
    """
    Set the environment variables for database configuration.
    Only sets variables for keys provided in kwargs and not None.
    """
    for key in DB_CONFIG_ENV_VARs.keys():
        if key in kwargs and kwargs[key] is not None:
            DB_CONFIG_ENV_VARs[key] = str(kwargs[key])

def get_configuration_envs() -> dict:
    """
    Get the current database configuration from environment variables.
    """
    return dict(DB_CONFIG_ENV_VARs)

def set_configuration_provider(func:callable):
    global get_configuration
    try:
        test = func()
    except Exception:
        test = None
    finally:
        pass
    if not isinstance(test, dict):
        raise ValueError("The configuration provider function must return a dictionary.")
    get_configuration = func

def get_connection_string(creds:dict):
    '''
    The creds should contain dictionary with keys like PDB_HOST, PDB_PORT, PDB_NAME, ...
    or keys like 'host', 'port', 'database', ....
    '''
    if creds is None:
        creds = get_configuration()
    elif isinstance(creds,dict):
        if 'PDB_HOST' in creds:
            cschema = creds.get(DB_CONFIG_ENV_VARs['schema'])
            creds = {
                "host": creds.get(DB_CONFIG_ENV_VARs['host'], 'localhost'),
                "port": creds.get(DB_CONFIG_ENV_VARs['port'], '5432'),
                "database": creds.get(DB_CONFIG_ENV_VARs['name'], 'postgres'),
                "user": creds.get(DB_CONFIG_ENV_VARs['user'], 'postgres'),
                "password": creds.get(DB_CONFIG_ENV_VARs['password'], 'postgres')
            }
            if cschema is not None:
                creds['options'] = '-c search_path=' + cschema                
    else:
        raise TypeError('The method get_connection_string requires dict object of credentials.')
    parts = []
    for key in ['host','port','database','user','password','options']:
        if key in creds and creds[key] is not None:
            parts.append(f"{key}={creds[key]}")
    return ' '.join(parts)

