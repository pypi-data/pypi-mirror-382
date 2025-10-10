from .connection import Connection
from .service import set_db_status
from .config import get_configuration, get_connection_string, DB_CONFIG_ENV_VARs


def get_connection(creds:dict=None) -> Connection:
    '''
    The creds should contain dictionary with keys like PDB_HOST, PDB_PORT, PDB_NAME, ...
    or keys like 'host', 'port', 'database', ....
    '''
    if creds is None:
        creds = get_configuration()
    elif isinstance(creds,dict):
        if 'PDB_HOST' in creds:
            cschema = creds.get(DB_CONFIG_ENV_VARs.get('schema'))
            creds = {
                'port': '5432'
            }.update({
                var: creds.get(DB_CONFIG_ENV_VARs.get(var)) 
                for var in ['host', 'port', 'name', 'user', 'password']
            })
            if cschema is not None:
                creds['options'] = '-c search_path=' + cschema                
    else:
        raise TypeError('The method get_connection requires dict object of credentials.')
    try:
        connstr = get_connection_string(creds)
        conn = Connection(connstr)
        if conn.encoding != 'UTF8':
            conn.set_client_encoding('UTF8')
        set_db_status('UP')
        return conn
    except Exception:
        set_db_status('DOWN')
        raise

