__doc__ = """
Database interface for PostgreSQL database.
It offers two modes:
- native
- ORM-based

# Native mode

```python

import dcnr_spring.database.postgres as pgdb

with pgdb.get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")

```
The assumption is, that configuration for connection is in the 
environment variables:
- PDB_HOST
- PDB_PORT
- PDB_NAME
- PDB_USER
- PDB_PWD
- PDB_SCHEMA

If you have configuration in different variables, set them before 
establishing of connection by this:

```python

import dcnr_spring.database.postgres as pgdb

pgdb.set_configuration_envs(host="DATABASE_HOST", 
                 port="DATABASE_PORT", name="DATABASE_NAME", 
                 user="DATABASE_USER", password="DATABASE_SECRET",
                 schema="DATABASE_DEFAULT_SCHEMA")
```

This will have effect that during get_connection() method
the connection data are fetched from environment variables `DATABASE_HOST`, etc.

# ORM based solution

```python

from spring_pkg.database.postgres import PostgresDatabase
from spring_pkg.database.base import dbtable, dbfield
from spring_pkg.database.base import DatabaseEntity

@dbtable(schema="test_schema", table="records")
class Record(DatabaseEntity):
    id: int = dbfield(alias="record_id")
    text: str = dbfield(alias="text_content")
    status: str = dbfield(default="active")
    count: int = dbfield(default=0)

    
rec = Record(id=1, text="Hello World", status="published", count=42)
print(rec.to_dict(["id", "text"]))

# Using the database
db = PostgresDatabase()
db.insert(rec)

# find all records with status published
for r in db.find(Record, status="published"):
    print(r.id, r.text, r.status, r.count)

```


"""


__all__ = ['get_configuration', 'set_configuration_provider', 'get_connection_string',
           'set_configuration_envs', 'get_configuration_envs',
           'get_shared_connection', 'get_connection',
           'PostgresDatabase']

from .config import (get_configuration, 
                     set_configuration_envs, 
                     get_configuration_envs, 
                     set_configuration_provider, 
                     get_connection_string)
from .conn_pool import get_shared_connection
from .main_api import get_connection
from .postgres_db import PostgresDatabase