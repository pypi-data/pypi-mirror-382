import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from .conn_pool import get_shared_connection
from ..base import Database, QueryExpression
from .sql import get_sql_params, stringify_dict


class PostgresDatabase(Database):
    def __init__(self):
        super().__init__()
        self.shared_cursor = None

    @contextmanager
    def transaction(self):
        """
        Provides ability to do commit only after closing transaction block.

        Usage:
        with db.transaction():
            db.insert(...)
            db.update(...)
            ...

        """
        if self.shared_cursor is not None:
            raise RuntimeError('Nested transaction is not supported.')
        
        with get_shared_connection() as conn:
            with conn.cursor(row_factory=dict_row) as curs:
                try:
                    self.shared_cursor = curs
                    yield
                    conn.commit()
                except Exception as x:
                    conn.rollback()
                    raise x
                finally:
                    self.shared_cursor = None


    def _insert(self, cls, schema: str, table: str, row: dict) -> None:
        if self.shared_cursor:
            self.insert_update(self.shared_cursor, schema, table, row)
        else:
            with get_shared_connection() as conn:
                with conn.cursor(row_factory=dict_row) as curs:
                    self.insert_update(curs, schema, table, row)
                    conn.commit()


    def _update(self, schema: str, table: str, row: dict, find):
        if self.shared_cursor:
            self.insert_update(self.shared_cursor, schema, table, row, find)
        else:
            with get_shared_connection() as conn:
                with conn.cursor(row_factory=dict_row) as curs:
                    self.insert_update(curs, schema, table, row, find)
                    conn.commit()
    
    def _find(self, cls, schema:str, table:str, expression:QueryExpression, order = None, limit = None):
        with get_shared_connection() as conn:
            with conn.cursor(row_factory=dict_row) as curs:
                query = f'SELECT * FROM {schema}.{table}'
                params = []
                if expression is not None:
                    where_clauses, params = expression.to_sql()
                    query += ' WHERE ' + where_clauses
                if order:
                    query += ' ORDER BY ' + order
                if limit is not None and limit > 0:
                    query += ' LIMIT %s'
                    params.append(limit)
                curs.execute(query, params)
                rows = curs.fetchall()
                for row in rows:
                    yield cls.from_json(dict(row))

    def _delete(self, cls, schema:str, table:str, expression = None):
        with get_shared_connection() as conn:
            with conn.cursor(row_factory=dict_row) as curs:
                query = f'DELETE FROM {schema}.{table}'
                params = []
                if expression is not None:
                    where_clauses, params = expression.to_sql()
                    query += ' WHERE ' + where_clauses
                curs.execute(query, params)
                conn.commit()
                return curs.rowcount

    def insert_update(self, curs:psycopg.Cursor, schema_name:str, table_name:str, data:dict, find=None):
        """Inserts or updates entity in DB.

        This function does only one of these operations, depending on value of find parameter.
        """
        result = {}
        if data is None:
            raise RuntimeError('Request data has to be in JSON format.')

        data = {key:stringify_dict(value) for key,value in data.items()}

        # We are going to create values for parametrized statement 
        # for safe SQL operation on database
        # We need the same order of columns, co we create array with triplets
        # where first item in column name, second is placeholder, third 
        # is column value.
        # All column values are in this case TEXT.
        query, params = get_sql_params(schema_name, table_name, data, find)
        try:
            curs.execute(query,params)
            result = curs.fetchone()
        except Exception as x:
            result = {
                '_status': 'ERROR',
                '_error': str(x)
            }

        return result


    def update_or_insert(self, curs:psycopg.Cursor, schema_name:str, table_name:str, data:dict, find=None):
        """Updates or inserts entity in DB.

        This function first tries to update given entity according find parameter.
        If not found, then it inserts new entity.
        This method does no commit. The commit to DB has to be done outside of this function.
        """
        result = {}
        if data is None:
            raise RuntimeError('Request data has to be in JSON format.')

        data = {key:stringify_dict(value) for key,value in data.items()}

        # We are going to create values for parametrized statement 
        # for safe SQL operation on database
        # We need the same order of columns, co we create array with triplets
        # where first item in column name, second is placeholder, third 
        # is column value.
        # All column values are in this case TEXT.
        query, params = get_sql_params(schema_name, table_name, data, find)
        try:
            curs.execute(query,params)
            if curs.rowcount == 0 and find is not None:
                data.update(find)
                query,params = get_sql_params(schema_name, table_name, data, None)
                curs.execute(query, params)
            result = curs.fetchone()
        except Exception as x:
            curs.connection.rollback()
            raise RuntimeError('update_or_insert failed') from x

        return result
