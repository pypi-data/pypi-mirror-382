from __future__ import annotations

from typing import Any, Optional, Dict, Tuple, get_type_hints, List
try:
    from typing import dataclass_transform  # py311+
except ImportError:
    from typing_extensions import dataclass_transform  # py310

from .dbfield import dbfield, DatabaseFieldSpec


# -------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------
def _snake(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i and (not name[i-1].isupper()):
            out.append("_")
        out.append(ch.lower())
    return "".join(out)

def _get_db_type_from_annotation(annotation) -> str:
    """Convert type annotation to database type string."""
    if annotation is int:
        return 'int'
    elif annotation is str:
        return 'varchar'
    elif annotation is float:
        return 'float'
    elif annotation is bool:
        return 'boolean'
    else:
        return 'varchar'  # Default fallback
    
# -------------------------------------------------------------------
# Decorator (works with and without arguments)
#   @model
#   @model(schema="rise", table="requests")
# -------------------------------------------------------------------
@dataclass_transform(field_specifiers=(dbfield,))
def dbtable(_cls: type | None = None, /, *, schema: Optional[str] = None,
          table: Optional[str] = None, repr: bool = True):
    """
    decorator for database entity classes.

    - Sets __schema__ and __tablename__ (from args or sensible defaults).
    - Builds a typed __init__ from annotations + defaults/field().
    - Injects runtime implementations of 'save' and 'find'.
    """

    def wrap(cls: type) -> type:
        # ---------- Check direct inheritance from DatabaseEntity ----------
        if 'DatabaseEntity' not in [c.__name__ for c in cls.__bases__]:
            raise TypeError(f"Class {cls.__name__} must directly inherit from DatabaseEntity. "
                        f"Current bases: {[base.__name__ for base in cls.__bases__]}")
        
        # ---------- names & defaults ----------
        hints = get_type_hints(cls, include_extras=False)

        # Get annotations ONLY from the current class (not inherited)
        current_class_annotations = getattr(cls, '__annotations__', {})

        # Get fields with DatabaseFieldSpec objects (dbfield() calls)
        dbfield_names = [name for name, value in vars(cls).items() 
                        if isinstance(value, DatabaseFieldSpec) and not name.startswith('_')]


        # capture declared order of annotated attributes
        # ordered = [n for n in cls.__dict__ if n in hints]
        # ordered = list(hints.keys())
        # Filter to only include fields defined in the current class
        # ordered = [name for name in current_class_annotations.keys() 
        #         if not name.startswith('_')]  # Exclude private/special variables

        # Start with annotated fields, then add dbfield-only fields
        ordered = []
        
        # Add annotated fields first (maintains annotation order)
        for name in current_class_annotations.keys():
            if not name.startswith('_'):
                ordered.append(name)
        
        # Add dbfield-only fields (fields with dbfield() but no annotation)
        for name in dbfield_names:
            if name not in ordered:  # Don't duplicate
                ordered.append(name)

        print(f'\n=========== {cls.__name__} =================')
        print(f"Current class annotations: {current_class_annotations}")
        print(f"All hints (including inherited): {hints}")
        print(f"Ordered (current class only): {ordered}")
        print(f"vars(cls): {vars(cls)}")

        # collect defaults (from class dict or DatabaseFieldSpec)
        defaults: Dict[str, Tuple[bool, Any]] = {}
        field_meta: Dict[str, DatabaseFieldSpec] = {}
        field_auto: List[str] = []
        for name, value in vars(cls).items():
            if isinstance(value, DatabaseFieldSpec):
                if value.dtype in ('serial4', 'serial8', 'bigserial'):
                    field_auto.append(name)
                    value.default = None
                defaults[name] = (True, value.default)
                field_meta[name] = value
            # elif value in ordered:
            #     # a non-DatabaseFieldSpec class attribute with a type annotation
            #     dbs = DatabaseFieldSpec()
            #     dbs.alias = name
            #     dbs.dtype = type(value).__name__
            #     dbs.nullable = True
            #     dbs.default = value
            #     field_meta[name] = dbs
            #     defaults[name] = (True, value)
            else:
                defaults[name] = (False, value)

        # Process annotation-only fields that don't have DatabaseFieldSpec
        for field_name in ordered:
            if field_name.startswith('__'):
                continue
            if field_name not in field_meta:  # Not already processed
                # Create DatabaseFieldSpec for annotation-only field
                dbs = DatabaseFieldSpec()
                dbs.alias = field_name
                
                # Get type from annotations
                field_type = current_class_annotations.get(field_name) or hints[field_name]
                dbs.dtype = _get_db_type_from_annotation(field_type)
                dbs.nullable = True
                dbs.default = None
                
                # Check if there's a default value in class dict
                if field_name in cls.__dict__:
                    default_value = cls.__dict__[field_name]
                    dbs.default = default_value
                    defaults[field_name] = (True, default_value)
                else:
                    defaults[field_name] = (True, None)  # No default, required field
                
                field_meta[field_name] = dbs

        setattr(cls, '__field_meta__', field_meta)
        setattr(cls, '__field_defaults__', defaults)
        setattr(cls, '__ordered_fields__', ordered)
        setattr(cls, '__automatic_fields__', field_auto)
        setattr(cls, '__primary_fields__', [n for n, fs in field_meta.items() if fs.primary])  # type: ignore[attr-defined]
        cls.__field_aliases__ = {n: fs.alias for n, fs in field_meta.items() if fs.alias}  # type: ignore[attr-defined]

        # ---------- schema & table ----------
        if schema is not None:
            setattr(cls, "__schema__", schema)
        else:
            # leave as-is if already present; else None
            setattr(cls, "__schema__", getattr(cls, "__schema__", None))

        if table is not None:
            setattr(cls, "__tablename__", table)
        else:
            # leave as-is or derive snake_case name
            setattr(cls, "__tablename__", getattr(cls, "__tablename__", _snake(cls.__name__)))

        # ---------- __init__ with proper signature for tooling ----------
        def __init__(self, **kwargs: Any) -> None:
            for n in self.__ordered_fields__:
                if n in kwargs:
                    val = kwargs[n]
                else:
                    has_default, dv = defaults.get(n, (False, ...))
                    if has_default:
                        val = dv
                    else:
                        if dv is ...:
                            raise TypeError(f"Missing required argument: {n!r}")
                        val = dv
                setattr(self, n, val)

        __init__.__name__ = "__init__"
        __init__.__qualname__ = f"{cls.__name__}.__init__"
        cls.__init__ = __init__  # type: ignore[assignment]

        # ---------- nice repr ----------
        if repr:
            def __repr__(self) -> str:
                pairs = ", ".join(f"{n}={getattr(self, n)!r}" for n in ordered)
                return f"{cls.__name__}({pairs})"
            cls.__repr__ = __repr__  # type: ignore[assignment]

        return cls

    # Support both @model and @model(...)
    return wrap if _cls is None else wrap(_cls)

