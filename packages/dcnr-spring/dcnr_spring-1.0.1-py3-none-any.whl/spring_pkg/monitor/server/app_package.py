from ...database import dbfield, dbtable, DatabaseEntity

@dbtable(schema='ppcm', table='app_package')
class AppPackage(DatabaseEntity):
    id: int = dbfield(dtype='serial8', primary=True)
    application_name: str = dbfield(dtype='text', nullable=False)
    create_d: str = dbfield(dtype='timestamp', default='now()', nullable=False)
    pkg_name: str = dbfield(dtype='text', nullable=False)
    version: str = ""
    # version: str = dbfield(dtype='text', nullable=False)