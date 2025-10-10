import psycopg
from psycopg.rows import dict_row
from .sql import get_sql_params, stringify_dict


class Connection():
    def __init__(self, connection:psycopg.Connection, **kwargs):
        super().__init__(**kwargs)
        self.connection = connection

    def insert(self, schema_name:str, table_name:str, data:dict):
        with self.connection.cursor(row_factory=dict_row) as curs:
            return self.insert_update(curs, schema_name, table_name, data, find=None)
        
    def update(self, schema_name:str, table_name:str, data:dict, find:dict):
        with self.connection.cursor(row_factory=dict_row) as curs:
            return self.insert_update(curs, schema_name, table_name, data, find=find)

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
            self.commit()
        except Exception as x:
            result = {
                '_status': 'ERROR',
                '_error': str(x)
            }
            self.rollback()

        return result


    def update_or_insert(self, schema_name:str, table_name:str, data:dict, find=None):
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
        with self.cursor(row_factory=dict_row) as curs:
            try:
                curs.execute(query,params)
                if curs.rowcount == 0 and find is not None:
                    data.update(find)
                    query,params = get_sql_params(schema_name, table_name, data, None)
                    curs.execute(query, params)
                self.commit()
                result = curs.fetchone()
            except Exception as x:
                self.rollback()
                raise RuntimeError('update_or_insert failed') from x

        return result
