from typing import Any, TypeVar, Iterator, Dict, Optional, List


# -------------------------------------------------------------------
# Base declaring method *signatures* so IDEs/type checkers see them
# -------------------------------------------------------------------
class DatabaseEntityBase:
    __ordered_fields__: List[str] = []
    __field_meta__: Dict[str, Any] = {}
    __field_defaults__: Dict[str, Any] = {}
    __field_aliases__: Dict[str, str] = {}
    __schema__: str = "default"
    __tablename__: str = ""
    __automatic_fields__: List[str] = []
    __primary_fields__: List[str] = []
    __database__: Optional[Any] = None  # type: ignore[var-annotated]

    def to_json(self) -> Dict[str, Any]:
        """
        Convert all annotated fields to a dictionary with column names as keys.
        Uses aliases if defined via dbfield(alias=...).
        """
        cls = self.__class__
        meta = {n: getattr(self, n) for n in cls.__ordered_fields__}
        as_columns = {
            (cls.__field_meta__[n].alias if n in cls.__field_meta__ and cls.__field_meta__[n].alias else n): v
            for n, v in meta.items()
        }
        return as_columns

    @classmethod
    def convert_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert input dictionary keys using alias metadata.
        
        Args:
            data: Input dictionary with keys as column names (possibly using aliases)
            
        Returns:
            Dictionary with keys converted to field names as per alias metadata.
            Example: If alias "text_content" maps to field "text", then
                     {"record_id": 1, "text_content": "Hello"} becomes {"id": 1, "text": "Hello"}
        """
        mapped_data = {
            (cls.__field_aliases__.get(k, k)): v
            for k, v in data.items()
        }
        return mapped_data

    # @classmethod
    # def from_json(cls, data: dict[str, Any]) -> Any: ...
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Any:
        # Map data keys using alias metadata
        alias_for: Dict[str, str] = {}
        for n, fs in cls.__field_meta__.items():
            if fs.alias:
                alias_for[fs.alias] = n
        mapped_data = {
            (alias_for.get(k, k)): v
            for k, v in data.items()
        }
        return cls(**mapped_data)

    @classmethod
    def set_database(cls, db: Any) -> None:
        cls.__database__ = db
