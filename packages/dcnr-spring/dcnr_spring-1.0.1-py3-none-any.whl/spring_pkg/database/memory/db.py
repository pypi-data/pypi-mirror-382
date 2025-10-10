from ..base import Database, DatabaseEntity
from typing import Dict, List, Any, Iterator
from ..base import QueryExpression


class MemoryTable:
    def __init__(self, name: str):
        self.name = name
        self.rows = []

class MemorySchema:
    def __init__(self, name: str):
        self.name = name
        self.tables:Dict[str,MemoryTable] = {}

class MemoryDatabase(Database):
    def __init__(self):
        super().__init__()
        self.autoinc_value = 1
        self.schemas:Dict[str,MemorySchema] = {}

    def get_schema(self, name: str) -> MemorySchema:
        if name not in self.schemas:
            self.schemas[name] = MemorySchema(name)
        return self.schemas[name]

    def get_table(self, name: str) -> MemoryTable:
        if name not in self.tables:
            self.tables[name] = MemoryTable(name)
        return self.tables[name]

    def _insert_align_auto(self, row: dict, automatic_fields: List[str]) -> None:
        for field in automatic_fields:
            if field not in row or row[field] is None:
                row[field] = self.autoinc_value
                self.autoinc_value += 1

    def _insert(self, cls, schema: str, table: str, row: dict) -> None:
        mem_schema = self.get_schema(schema) if schema else self.get_schema("default")
        mem_table = mem_schema.tables.get(table)
        if not mem_table:
            mem_table = MemoryTable(table)
            mem_schema.tables[table] = mem_table
        self._insert_align_auto(row, getattr(cls, '__automatic_fields__', []))
        mem_table.rows.append(row)
        return row


    def _update(self, schema: str, table: str, row: dict, find:Dict[str,Any]) -> None:
        mem_schema = self.get_schema(schema) if schema else self.get_schema("default")
        mem_table = mem_schema.tables.get(table)
        if not mem_table:
            return
        for existing_row in mem_table.rows:
            if all(existing_row.get(k) == v for k, v in find.items()):
                existing_row.update(row)

    def __ordered_rows(self, rows: List[Dict[str, Any]], order: str) -> List[Dict[str, Any]]:
        if not order:
            return rows
        from operator import itemgetter

        def analyze_field(field: str):
            fp = field.split(' ')
            if len(fp) == 1:
                return (fp[0], 'asc')
            elif len(fp) == 2:
                if fp[1].lower() == 'desc':
                    return (fp[0], True)
                else:
                    return (fp[0], False)
            else:
                raise ValueError(f"Invalid order field: {field}")
        order_fields = [analyze_field(field.strip()) for field in order.split(',')]
        def multisort(xs, specs):
            for key, reverse in reversed(specs):
                xs.sort(key=itemgetter(key), reverse=reverse)
            return xs

        return multisort(rows, order_fields)
    
    def _delete(self, cls, schema: str, table: str, expression:QueryExpression=None) -> int:
        """
        Args:
            schema: Schema name
            table: Table name
            expression: QueryExpression representing the criteria to find rows to delete
        Returns:
            Number of rows deleted
        """
        mem_schema = self.get_schema(schema) if schema else self.get_schema("default")
        mem_table = mem_schema.tables.get(table)
        if not mem_table:
            return 0
        
        original_count = len(mem_table.rows)
        mem_table.rows = [row for row in mem_table.rows if not (expression and expression.evaluate(row))]
        deleted_count = original_count - len(mem_table.rows)
        return deleted_count

    def _find(self, cls: type, schema:str, table: str, expression: QueryExpression = None, order:str=None, limit:int=None) -> Iterator[Any]:
        """
        Find rows in the specified schema and table that match the given criteria.
        Returns an iterator for memory efficiency with large datasets.
        
        Args:
            cls: Entity class with __schema__ attribute
            schema: The schema name
            table: The table name
            criteria: Dictionary of key-value pairs to match against
            
        Returns:
            Iterator over instances of the given class
            
        Example:
            # Find all rows where status='active' and count > 10
            for person in db.find(Person, "people", {"status": "active", "count": 10}):
                print(person.name)
        """
        if not issubclass(cls, DatabaseEntity):
            raise ValueError("cls must be a subclass of Database")
              
        mem_schema = self.get_schema(schema) if schema else self.get_schema("default")
        mem_table = mem_schema.tables.get(table)
        
        if not mem_table:
            # Return empty iterator if table doesn't exist
            return iter([])
        
        # Generator function to yield matching instances
        def instance_generator():
            counter = 0
            for row in self.__ordered_rows(mem_table.rows, order):
                if expression and not expression.evaluate(row):
                    continue
                # Convert dictionary to class instance
                instance = cls.from_json(row)
                yield instance

                counter += 1
                if (limit is not None and isinstance(limit,int)
                    and limit > 0 and counter >= limit):
                    break
        
        return instance_generator()