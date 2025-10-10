import os, sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import spring_pkg as spring

from spring_pkg.database import DatabaseEntity, dbfield, dbtable, Database


@dbtable(schema="rise", table="requests")
class Request(DatabaseEntity):
    id: int = dbfield(dtype="serial8")  # auto-incrementing PK
    # DB column is "client_text", but Python name is "text"
    text: str = dbfield(alias="client_text")
    status: str = "new"


database = Database()

r = Request(text="hello")
r.save(database)
