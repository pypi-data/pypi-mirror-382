from typing import Dict, Any, Iterator, List, Optional

class DatabaseRoot:
    """
    Root class for ORM database object.
    """
    def __init__(self):
        pass

    def _find(self, cls: type, schema:str, table: str, criteria: Dict[str, Any], __order:str=None, __limit:int=None) -> Iterator[Any]:
        """
        Args:
            criteria: Dictionary of key-value pairs to match against
                   keys are names of columns in physical database
        Returns:
             Returns an iterator of instances of the given entity class"""
        raise NotImplementedError("Subclasses should implement this method.")