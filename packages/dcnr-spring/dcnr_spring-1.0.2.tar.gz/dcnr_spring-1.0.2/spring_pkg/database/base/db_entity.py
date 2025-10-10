from typing import Any, TypeVar, Iterator
from .db_entity_base import DatabaseEntityBase
from .database import Database

class DatabaseEntity(DatabaseEntityBase):
    """Optional: inherit to make IDEs show save/find even before decoration."""

    def insert(self, db:Database=None) -> Any:
        db = DatabaseEntity.safe_database(self, db)
        return db.insert(self)

    def update(self, db:Database=None, **where: Any) -> None:
        db = DatabaseEntity.safe_database(self, db)
        db.update(self, find=where)

    def save(self, db:Database=None) -> Any:
        db = DatabaseEntity.safe_database(self, db)
        if not self.__primary_fields__:
            return db.insert(self)
        find_criteria = {field: getattr(self, field) for field in self.__primary_fields__}
        if any(v is None for v in find_criteria.values()):
            return db.insert(self)
        else:
            db.update(self, find=find_criteria)

    @staticmethod
    def safe_database(obj, db) -> Any:
        if db is None:
            db = getattr(obj, '__database__', None)
            if db is None:
                raise ValueError("No database instance associated with this entity. Provide 'db' argument or set '__database__' attribute.")
        return db

    @classmethod
    def find(cls, db:Database=None, **where: Any) -> Iterator[Any]:
        db = DatabaseEntity.safe_database(cls, db)
        return db.find(cls, **where)
