from typing import Any, Dict, List
from abc import ABC, abstractmethod

class QueryExpression(ABC):
    """Base class for query expressions"""
    
    @abstractmethod
    def evaluate(self, row: Dict[str, Any]) -> bool:
        """Evaluate the expression against a data row"""
        pass
    
    @abstractmethod
    def to_sql(self) -> tuple[str, List[Any]]:
        """Convert to SQL WHERE clause with parameters"""
        pass

    @abstractmethod
    def map_names(self, aliases: Dict[str, str]) -> None:
        """Map field names using the provided aliases dictionary"""
        pass
    
    def __and__(self, other):
        """Support & operator for AND operations"""
        return AndExpression(self, other)
    
    def __or__(self, other):
        """Support | operator for OR operations"""
        return OrExpression(self, other)

class FieldExpression:
    """Represents a database field that can be used in comparisons"""
    
    def __init__(self, field_name: str):
        self.field_name = field_name
    
    def __eq__(self, other):
        return EqualExpression(self.field_name, other)
    
    def __ne__(self, other):
        return NotEqualExpression(self.field_name, other)
    
    def __lt__(self, other):
        return LessThanExpression(self.field_name, other)
    
    def __le__(self, other):
        return LessEqualExpression(self.field_name, other)
    
    def __gt__(self, other):
        return GreaterThanExpression(self.field_name, other)
    
    def __ge__(self, other):
        return GreaterEqualExpression(self.field_name, other)
    
    def __and__(self, other):
        """Support & operator for AND operations"""
        return AndExpression(self, other)
    
    def __or__(self, other):
        """Support | operator for OR operations"""
        return OrExpression(self, other)
    
    def map_names(self, aliases: Dict[str, str]) -> None:
        if self.field_name in aliases:
            self.field_name = aliases[self.field_name]

class EqualExpression(QueryExpression):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        return row.get(self.field) == self.value
    
    def to_sql(self) -> tuple[str, List[Any]]:
        if self.value is None:
            return f"{self.field} IS NULL", []
        return f"{self.field} = %s", [self.value]
    
    def map_names(self, aliases: Dict[str, str]) -> None:
        if self.field in aliases:
            self.field = aliases[self.field]

class NotEqualExpression(QueryExpression):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        return row.get(self.field) != self.value
    
    def to_sql(self) -> tuple[str, List[Any]]:
        if self.value is None:
            return f"{self.field} IS NOT NULL", []
        return f"{self.field} != %s", [self.value]

    def map_names(self, aliases: Dict[str, str]) -> None:
        if self.field in aliases:
            self.field = aliases[self.field]


class GreaterThanExpression(QueryExpression):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        field_value = row.get(self.field)
        return field_value is not None and field_value > self.value
    
    def to_sql(self) -> tuple[str, List[Any]]:
        return f"{self.field} > %s", [self.value]

    def map_names(self, aliases: Dict[str, str]) -> None:
        if self.field in aliases:
            self.field = aliases[self.field]

class GreaterEqualExpression(QueryExpression):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        field_value = row.get(self.field)
        return field_value is not None and field_value >= self.value
    
    def to_sql(self) -> tuple[str, List[Any]]:
        return f"{self.field} >= %s", [self.value]

    def map_names(self, aliases: Dict[str, str]) -> None:
        if self.field in aliases:
            self.field = aliases[self.field]

class LessThanExpression(QueryExpression):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        field_value = row.get(self.field)
        return field_value is not None and field_value < self.value
    
    def to_sql(self) -> tuple[str, List[Any]]:
        return f"{self.field} < %s", [self.value]

    def map_names(self, aliases: Dict[str, str]) -> None:
        if self.field in aliases:
            self.field = aliases[self.field]

class LessEqualExpression(QueryExpression):
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        field_value = row.get(self.field)
        return field_value is not None and field_value <= self.value
    
    def to_sql(self) -> tuple[str, List[Any]]:
        return f"{self.field} <= %s", [self.value]

    def map_names(self, aliases: Dict[str, str]) -> None:
        if self.field in aliases:
            self.field = aliases[self.field]

class AndExpression(QueryExpression):
    def __init__(self, left: QueryExpression, right: QueryExpression):
        self.left = left
        self.right = right
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        return self.left.evaluate(row) and self.right.evaluate(row)
    
    def to_sql(self) -> tuple[str, List[Any]]:
        left_sql, left_params = self.left.to_sql()
        right_sql, right_params = self.right.to_sql()
        return f"({left_sql}) AND ({right_sql})", left_params + right_params

    def map_names(self, aliases: Dict[str, str]) -> None:
        self.left.map_names(aliases)
        self.right.map_names(aliases)

class OrExpression(QueryExpression):
    def __init__(self, left: QueryExpression, right: QueryExpression):
        self.left = left
        self.right = right
    
    def evaluate(self, row: Dict[str, Any]) -> bool:
        return self.left.evaluate(row) or self.right.evaluate(row)
    
    def to_sql(self) -> tuple[str, List[Any]]:
        left_sql, left_params = self.left.to_sql()
        right_sql, right_params = self.right.to_sql()
        return f"({left_sql}) OR ({right_sql})", left_params + right_params

    def map_names(self, aliases: Dict[str, str]) -> None:
        self.left.map_names(aliases)
        self.right.map_names(aliases)

# Helper functions to create field expressions
def F(name: str) -> FieldExpression:
    """Create a field expression for queries"""
    return FieldExpression(name)

# Convenience functions
def Q(**kwargs) -> QueryExpression:
    """Create query expressions from keyword arguments"""
    expressions = []
    for field_name, value in kwargs.items():
        expressions.append(EqualExpression(field_name, value))
    
    if len(expressions) == 1:
        return expressions[0]
    
    # Combine with AND
    result = expressions[0]
    for expr in expressions[1:]:
        result = AndExpression(result, expr)
    
    return result