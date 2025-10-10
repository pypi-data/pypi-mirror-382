from ...actuator import register_actuator_component
import os

__all__ = [
    'set_db_status',
    'get_db_status'
]

PINGHOUND_DB_SERVICE_NAME = os.getenv('PINGHOUND_DB_SERVICE_NAME', 'db')

DB_STATUS = {
    'status': 'UP',
    'details': {
        'database': 'PostgreSQL',
        'validationQuery': 'SELECT 1',
    }
}

def get_db_status():
    return DB_STATUS

def set_db_status(status:str, details:dict=None):
    DB_STATUS['status'] = status
    if details is not None:
        DB_STATUS['details'] = details

register_actuator_component(PINGHOUND_DB_SERVICE_NAME, get_db_status)
