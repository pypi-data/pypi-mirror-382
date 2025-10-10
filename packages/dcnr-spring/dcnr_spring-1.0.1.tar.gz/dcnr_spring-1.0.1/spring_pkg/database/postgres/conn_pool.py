# db_pool.py
import os
import atexit
from psycopg_pool import ConnectionPool
from .config import get_configuration, get_connection_string
from ...coding import LockedValue


pool = LockedValue[ConnectionPool](None)

# Typical DSN; you can also pass individual params
def get_safe_pool(credentials:dict=None):
    with pool.lock:
        if pool.get() is not None:
            return pool.get()
        DSN = get_connection_string(credentials or get_configuration())

        pool_value = ConnectionPool(
            conninfo=DSN,
            min_size=1,              # keep at least 1 warm connection
            max_size=10,             # cap total connections
            max_idle=300,            # seconds; recycle if idle too long
            max_lifetime=3600,       # seconds; recycle old connections
            timeout=30,              # wait up to 30s for a connection
            # Configure newly-opened connections (e.g., session settings)
            configure=lambda conn: conn.execute("set application_name to 'my-app'"),
            # Reset is called before returning a conn to pool (default rolls back)
            # reset=None,
            kwargs={                 # passed to psycopg.connect(...)
                "autocommit": False, # usually prefer explicit transactions
                # TCP keepalives (optional but good for long-lived conns)
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 3,
            },
        )

        # Optional: explicit open at startup (otherwise first checkout opens lazily)
        pool_value.open()
        atexit.register(pool_value.close)
        pool.set(pool_value)

    return pool.get()

def get_shared_connection(creds:dict=None):
    """
    Acquire a pooled connection as a context manager.
    Usage:
        with get_shared_connection() as conn:
            ...
    """
    return get_safe_pool(creds=creds).connection()
