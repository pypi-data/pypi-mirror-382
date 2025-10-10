from typing import Any, Optional

# -------------------------------------------------------------------
# Field helper: carry defaults + optional DB column alias
# -------------------------------------------------------------------
class DatabaseFieldSpec:
    __slots__ = ("default", "alias", "dtype", "primary", "nullable")
    def __init__(self, default: Any = ..., *, alias: Optional[str] = None, dtype: Optional[str] = None, primary: Optional[bool] = False, nullable: Optional[bool] = False) -> None:
        self.default = default
        self.alias = alias
        self.dtype = dtype
        self.primary = primary
        self.nullable = nullable

def dbfield(default: Any = ..., *, alias: Optional[str] = None, dtype: Optional[str] = None, primary: Optional[bool] = False, nullable: Optional[bool] = False) -> DatabaseFieldSpec:
    """
    Create definition for a database-mapped field.
    """
    return DatabaseFieldSpec(default, alias=alias, dtype=dtype, primary=primary, nullable=nullable)