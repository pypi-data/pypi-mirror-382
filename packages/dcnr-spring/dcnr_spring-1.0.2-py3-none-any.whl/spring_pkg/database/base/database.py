from .db_entity_base import DatabaseEntityBase
from typing import Dict, Any, Iterator, List, Generator
from .database_root import DatabaseRoot
from .query_result import QueryResult
from .query_expression import QueryExpression, Q, AndExpression


class Database(DatabaseRoot):
    """
    Database object for ORM operations.

    Connection is estabilished in subclass specific way. 
    For database in memory, teher is not need to connect to other server.
    For PostgreSQL it is necessary to provide connection parameters.

    Database provides basic methods for CRUD operations.
    - insert
    - update
    - delete
    - find

    The operations are enabled by correct using of 
    dbtable and dbfield decorators in data entity classes.

    """
    def __init__(self):
        # Initialize database connection here
        pass

    def _delete(self, cls, schema: str, table: str, expression:QueryExpression=None) -> int:
        """
        Args:
            schema: Schema name
            table: Table name
            expression: QueryExpression representing the criteria to find rows to delete
        Returns:
            Number of rows deleted
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def _insert(self, cls, schema: str, table: str, row: dict) -> None:
        """
        Args:
            schema: Schema name
            table: Table name
            row: Dictionary representing the row to insert
                keys are names of columns in physical database

        """
        raise NotImplementedError("Subclasses should implement this method.")
    
    def _update(self, schema: str, table: str, row: dict, find:Dict[str,Any]) -> None:
        """
        Args:
            schema: Schema name
            table: Table name
            row: Dictionary representing the row to update
                keys are names of columns in physical database
            find: Dictionary representing the criteria to find rows to update
                keys are names of columns in physical database
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def _find(self, cls: type, schema:str, table: str, expression: QueryExpression=None, order:str=None, limit:int=None) -> QueryResult:
        """
        Args:
            criteria: Dictionary of key-value pairs to match against
                   keys are names of columns in physical database
        Returns:
             Returns an iterator of instances of the given entity class"""
        raise NotImplementedError("Subclasses should implement this method.")

    def _copy_automatic_field_values(self, source: Dict[str, Any], target: Any) -> None:
        cls = target.__class__
        automatic_fields = cls.__automatic_fields__ if hasattr(cls, '__automatic_fields__') else []
        aliases = cls.__field_aliases__ if hasattr(cls, '__field_aliases__') else {}
        for field in automatic_fields:
            if field in source:
                column = aliases.get(field, field)
                setattr(target, field, source[column])

    def create(self, cls) -> Any:
        if not issubclass(cls, DatabaseEntityBase):
            raise TypeError("cls must be a subclass of DatabaseEntityBase")
        instance = cls()
        setattr(instance, '__database__', self)
        return instance

    def insert(self, entity:DatabaseEntityBase) -> None:
        schema = entity.__schema__
        table = entity.__tablename__
        cls_ = entity.__class__
        row = self._insert(entity.__class__, schema, table, entity.to_json())
        self._copy_automatic_field_values(row, entity)
        setattr(entity, '__database__', self)


    def update(self, entity:DatabaseEntityBase, find:Dict[str,Any]) -> None:
        schema = entity.__schema__
        table = entity.__tablename__
        self._update(schema, table, entity.to_json(), find=entity.convert_fields(find))
        setattr(entity, '__database__', self)

    def _convert_args_to_expressions(self, cls, expressions:QueryExpression, where: Any) -> QueryExpression:
        all_expressions = list(expressions)
        
        if where:
            all_expressions.append(Q(**where))

        # Combine all expressions with AND
        if len(all_expressions) == 1:
            combined_expression = all_expressions[0]
        elif len(all_expressions) > 1:
            combined_expression = all_expressions[0]
            for expr in all_expressions[1:]:
                combined_expression = AndExpression(combined_expression, expr)
        else:
            combined_expression = None

        if combined_expression:
            combined_expression.map_names(getattr(cls, '__field_aliases__', {}))

        return combined_expression

    def delete(self, cls: type, *expressions:QueryExpression, **where: Any) -> int:
        """
        Delete rows in the specified schema and table that match the given criteria.
        
        Args:
            cls: Entity class with __schema__ attribute
            *expressions: Query expressions like F('age') > 3
            **where: Keyword arguments for filtering

        Returns:
            Number of rows deleted
        """
        combined_expression = self._convert_args_to_expressions(cls, expressions, where)
        
        return self._delete(cls, getattr(cls, '__schema__', None), getattr(cls, '__tablename__', ''), expression=combined_expression)


    def find(self, cls: type, *expressions:QueryExpression, **where: Any) -> QueryResult:
        """
        Override base find method to properly extract schema from entity class.
        
        Args:
            cls: Entity class with __schema__ attribute
            *expressions: Query expressions like F('age') > 3
            **where: Keyword arguments for filtering

        Examples:
            # Using expressions
            db.find(Person, F('age') > 3, F('name') != None)

            # Using keyword arguments
            db.find(Person, department="Engineering", active=True)
            
            # Mixed usage
            db.find(Person, field('age') > 18, department="Engineering")
            
        Returns:
            List of instances of the given class
        """
        combined_expression = self._convert_args_to_expressions(cls, expressions, where)

        return QueryResult(self, cls, combined_expression)


