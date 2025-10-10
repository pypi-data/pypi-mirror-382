from contextlib import contextmanager



class DatabaseCursor:
    def __init__(self):
        pass

    def execute(self, sql, params=None):
        pass

    def fetchone(self):
        return None

    def fetchall(self):
        return []

    def close(self):
        pass

    def rowcount(self):
        return 0

class DatabaseConnection:
    def __init__(self, **kwargs):
        self.data = kwargs

    def cursor(self, row_factory=None):
        return self
    
    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

@contextmanager
def connection():
    # open connection
    conn = DatabaseConnection()
    try:
        yield conn
        # commit
        conn.commit()
    except Exception as ex:
        # rollback
        conn.rollback()
        raise ex
    finally:
        # close connection
        conn.close()

