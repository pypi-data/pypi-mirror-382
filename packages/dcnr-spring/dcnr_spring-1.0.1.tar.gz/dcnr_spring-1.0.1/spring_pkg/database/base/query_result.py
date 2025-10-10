from typing import Dict, Any, Iterator, List, Optional
from .database_root import DatabaseRoot
from .query_expression import QueryExpression, AndExpression


class QueryResult:
    """
    A chainable query result that supports ordering and limiting.
    """
    
    def __init__(self, database: DatabaseRoot, cls: type, expression: QueryExpression = None):
        self._database = database
        self._cls = cls
        self.expression = expression
        self._order_fields: Optional[Dict[str, str]] = None
        self._limit_count: Optional[int] = None

    def where(self, *expressions: QueryExpression) -> 'QueryResult':
        """Add additional WHERE conditions"""
        if not expressions:
            return self
        
        # Combine new expressions
        new_expression = expressions[0]
        for expr in expressions[1:]:
            new_expression = AndExpression(new_expression, expr)
        
        # Combine with existing expression
        if self.expression:
            combined = AndExpression(self.expression, new_expression)
        else:
            combined = new_expression
        
        return QueryResult(self.database, self.cls, combined)
    
    def order(self, **fields: str) -> 'QueryResult':
        """
        Add ordering to the query.
        
        Args:
            **fields: Field names as keys, 'asc' or 'desc' as values
            
        Example:
            query.order(name='asc', age='desc')
            
        Returns:
            New QueryResult with ordering applied
        """           
        # Validate ordering values
        for field, direction in fields.items():
            if direction.lower() not in ('asc', 'desc'):
                raise ValueError(f"Invalid order direction '{direction}' for field '{field}'. Must be 'asc' or 'desc'.")
        
        # Create a new QueryResult with the ordering
        new_query = QueryResult(self._database, self._cls, self.expression)
        new_query._order_fields = fields.copy()
        new_query._limit_count = self._limit_count  # Preserve existing limit
        return new_query
    
    def limit(self, count: int) -> 'QueryResult':
        """
        Add a limit to the query.
        
        Args:
            count: Maximum number of results to return
            
        Returns:
            New QueryResult with limit applied
        """
        if count <= 0:
            raise ValueError("Limit count must be positive")
            
        # Create a new QueryResult with the limit
        new_query = QueryResult(self._database, self._cls, self.expression)
        new_query._order_fields = self._order_fields.copy() if self._order_fields else None
        new_query._limit_count = count
        return new_query
    
    def _build_order_string(self) -> Optional[str]:
        """
        Convert order fields dict to database order string format.
        
        Returns:
            Order string like "name asc, age desc" or None
        """
        if not self._order_fields:
            return None
            
        order_parts = []
        for field, direction in self._order_fields.items():
            order_parts.append(f"{field} {direction.lower()}")
        
        return ", ".join(order_parts)
    
    def __iter__(self) -> Iterator[Any]:
        """
        Execute the query and return an iterator of results.
        """
        order_string = self._build_order_string()
        
        results = self._database._find(
            cls=self._cls,
            schema=getattr(self._cls, '__schema__', 'public'),
            table=getattr(self._cls, '__tablename__', ''),
            expression=self.expression,
            order=order_string,
            limit=self._limit_count
        )
        
        for result in results:
            setattr(result, '__database__', self._database)
            yield result
    
    def __len__(self) -> int:
        """
        Get the count of results (executes the query).
        """
        length = 0
        for _ in self:
            length += 1
        return length
    
    def __bool__(self) -> bool:
        """
        Check if there are any results.
        """
        try:
            next(iter(self))
            return True
        except StopIteration:
            return False
    
    def first(self) -> Optional[Any]:
        """
        Get the first result or None if no results.
        """
        try:
            return next(iter(self))
        except StopIteration:
            return None
    
    def all(self) -> List[Any]:
        """
        Get all results as a list.
        """
        return [a for a in self]
    
    def __repr__(self) -> str:
        order_info = f", order={self._order_fields}" if self._order_fields else ""
        limit_info = f", limit={self._limit_count}" if self._limit_count else ""
        return f"QueryResult(cls={self._cls.__name__}, criteria={self.expression}{order_info}{limit_info})"
