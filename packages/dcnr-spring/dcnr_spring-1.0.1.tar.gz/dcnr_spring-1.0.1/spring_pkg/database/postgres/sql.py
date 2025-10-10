import json


"""
Parameter:
  single_body : dictionary where keys are names of columns, values are values for given columns
  columns: optional list of allowed columns. Keys in dictionary, not present in columns list will be ignored.
"""
def stringify_dict(value):
    if isinstance(value,dict) or isinstance(value,list):
        return json.dumps(value, indent=2)
    else:
        return value

def get_sql_params(schema_name, table_name, data, find):
    column_list = []
    values_list = []
    params = []
    for key,val in data.items():
        params.append(val)
        column_list.append(key)
        values_list.append('%s')

    if find is not None and isinstance(find,dict):
        # This is update of existing item
        find_list = []
        for findkey,findvalue in find.items():
            params.append(findvalue)
            find_list.append(f'{findkey}=%s')
        query = f"""UPDATE {schema_name}.{table_name}
            SET ({','.join(column_list)}) = ROW({','.join(values_list)})
            WHERE {' AND '.join(find_list)} RETURNING *;"""
    else:
        # This is creation of the new item.
        query = f"""INSERT INTO {schema_name}.{table_name}({','.join(column_list)})
        VALUES({','.join(values_list)}) RETURNING *;"""

    return query, params
