import re
import keyword
import inspect

from enum import Enum
from pydantic import BaseModel
from datetime import date, datetime
from surrealdb import Geometry, RecordID
from dataclasses import dataclass, field
# from pydantic_core import PydanticUndefined
from typing import get_origin, get_args, Literal, Union, Any, Any, Optional, Generic, TypeVar

from .field import Field
from .utils import flatten_type
from .tokenizer import Text, Tokenizer, FrenchTokenizer


@dataclass(frozen=True)
class Link:
    _in: type[Any]
    _out: type[Any]
    symetric: bool = False


H = TypeVar('H')



# This file is bloated, should be re-writen


class Reference(Generic[H]):
    """
    Type annotation for defining foreign key references to other tables.

    Reference fields create relationships between tables in SurrealDB by storing
    RecordIDs that point to records in other tables. This is similar to foreign
    keys in traditional databases but leverages SurrealDB's graph capabilities.

    Type Parameters:
        H: The Node or Edge class that this field references

    Example:
        >>> from tapestry import Node, Reference
        >>>
        >>> class Person(Node):
        ...     name: str
        ...     email: str
        ...
        >>> class Article(Node):
        ...     title: str
        ...     author: Reference[Person]  # References a Person record
        ...     editor: Reference[Person] | None  # Optional reference
        ...
        >>> # When creating an article
        >>> person = await Person(name="John Doe", email="john@example.com").create(db)
        >>> article = Article(
        ...     title="Introduction to SurrealDB",
        ...     author=person  # Can assign the Person instance directly
        ... )
        >>> await article.create(db)
        >>>
        >>> # The author field will store the Person's RecordID
        >>> print(article.author)  # RecordID(table='person', id='...')

    Notes:
        - Reference fields store RecordIDs, not the full referenced object
        - Can reference any Node or Edge subclass
        - Supports optional references with Union[Reference[T], None]
        - When querying, references can be traversed using graph operators
        - Unlike Edge tables, References are unidirectional and don't create separate relation tables

    See Also:
        - Edge: For bidirectional relationships with properties
        - Node: Base class for tables that can be referenced
    """
    pass


@dataclass(frozen=True)
class Table:
    name: str
    base_class: type
    model_class: type
    fields: tuple[Field[Any], ...]
    name_to_type: dict[str, type] = field(default_factory=dict)
    relation: Optional[Link] = None
    index: dict[str, str] = field(default_factory=dict)
    tokenizers: tuple[Tokenizer, ...] = ()

    def __post_init__(self):
        indices = {}
        tokenizers = []
        for field in self.fields:
            if field.field_type:
                for tp in tuple(flatten_type(field.field_type, base_type=Text)):
                    if inspect.isclass(tp) and issubclass(tp, Text):
                        tokenizer = (get_args(tp) or (FrenchTokenizer, ))[0]
                        tokenizers.append(tokenizer)
                        indices[field.name] = tokenizer.name

                for tp in tuple(flatten_type(field.field_type, base_type=Reference)):
                    origin = get_origin(tp)
                    if origin is Reference or (tp is Reference and not origin):
                        args =  get_args(tp)
                        if not args or not issubclass(args[0], self.base_class):
                            raise TypeError("References must point to a Node class")

        object.__setattr__(self, "index", indices)
        object.__setattr__(self, "tokenizers", tuple(tokenizers))
        object.__setattr__(self, "name_to_type", {f.name: f.field_type for f in self.fields})

    # -------------------- helpers to map python type -> surreal type ----------

    @staticmethod
    def _quote_ident(name: str) -> str:
        if keyword.iskeyword(name) or not name.isidentifier():
            return f'"{name}"'
        return name


    @staticmethod
    def _enum_to_literal_union(tp: type[Enum]) -> str:
        # parts = []
        # for m in tp:
        #     v = m.value
        #     if isinstance(v, str):
        #         parts.append(f'"{v}"')
        #     else:
        #         parts.append(f'"{m.name}"')
        # return " | ".join(parts)
        return " | ".join(f'"{m.name}"' for m in tp)


    @staticmethod
    def _literal_to_union(tp: Any) -> str:
        # Literal[...] -> produce Surreal literal union
        args = get_args(tp)
        parts = []
        for a in args:
            if a is None:
                parts.append("NONE")
            elif isinstance(a, str):
                parts.append(f'"{a}"')
            elif isinstance(a, bool):
                parts.append("true" if a else "false")
            else:
                parts.append(str(a))
        return " | ".join(parts)


    def _pytype_to_surreal(self, field_name: str, tp: Any, _skip_serializer_check: bool = False) -> str:
        """Map Python typing annotation tp -> Surreal type expression string."""

        origin = get_origin(tp) or getattr(tp, "__origin__", None)
        args = get_args(tp) or getattr(tp, "__args__", ())

        # Check for Pydantic model subclass first (before checking custom types)
        if inspect.isclass(tp) and issubclass(tp, self.base_class):
            return f"record<{tp.__name__.lower()}>"


        # Check for Pydantic model subclass first (before checking custom types)
        if inspect.isclass(tp) and issubclass(tp, Reference):
            print(tp.__annotations__)
            assert False
            # should I really make a REFERENCE here ?
            # return f"record<{tp.__name__.lower()}> REFERENCE"
            return f"record<{tp.__name__.lower()}> REFERENCE"


        if inspect.isclass(tp) and issubclass(tp, Text):
            return "string"

        # Check for field serializers on the parent class (skip if recursing from serializer)
        if not _skip_serializer_check and inspect.isclass(self.model_class) and issubclass(self.model_class, BaseModel):
            # Look for field_serializer method (format: serialize__{field_name})
            serializer_name = f"serialize__{field_name}"
            if hasattr(self.model_class, serializer_name):
                serializer_method = getattr(self.model_class, serializer_name)
                if callable(serializer_method):
                    sig = inspect.signature(serializer_method)
                    if sig.return_annotation != inspect.Signature.empty:
                        # Skip serializer check on recursive call to avoid infinite loop
                        return self._pytype_to_surreal(field_name, sig.return_annotation, _skip_serializer_check=True)

        # Check if the type itself is a Pydantic BaseModel with a model_serializer
        if not _skip_serializer_check and inspect.isclass(tp) and issubclass(tp, BaseModel) and not issubclass(tp, self.base_class):
            # Look for model_serializer method
            for name in dir(tp):
                if not name.startswith('_'):
                    attr = getattr(tp, name)
                    if callable(attr) and hasattr(attr, '__func__'):
                        # Check if this method has a model_serializer decorator
                        # by checking if it has the right signature (self) -> ReturnType
                        try:
                            sig = inspect.signature(attr)
                            # model_serializer methods typically have (self) -> ReturnType signature
                            params = list(sig.parameters.values())
                            if (len(params) == 1 and
                                params[0].name == 'self' and
                                sig.return_annotation != inspect.Signature.empty):
                                # This looks like a model_serializer, use its return type
                                # Skip serializer check on recursive call to avoid infinite loop
                                return self._pytype_to_surreal(field_name, sig.return_annotation, _skip_serializer_check=True)
                        except (ValueError, TypeError):
                            continue

        if hasattr(tp, '__get_pydantic_core_schema__'):
            # Try to infer the underlying type from the core schema
            try:
                # Get the core schema (Pydantic v2)
                from pydantic import GetCoreSchemaHandler

                # Create a simple handler that returns the schema for basic types
                class SimpleHandler:
                    def __call__(self, source_type):
                        # Return a simple any schema for unknown types
                        from pydantic_core import core_schema
                        return core_schema.any_schema()

                    def generate_schema(self, source_type):
                        from pydantic_core import core_schema
                        return core_schema.any_schema()

                    @property
                    def handler(self):
                        return self

                handler = SimpleHandler()

                # Try to get schema
                schema = tp.__get_pydantic_core_schema__(source_type=tp, handler=handler)

                # Analyze the schema to determine the underlying type
                return self._analyze_core_schema(schema)
            except Exception:
                pass

            # # Fallback: Check if it's a known SurrealDB type
            # # Check by class name or direct type comparison
            # if tp is Geometry or (hasattr(tp, '__name__') and 'Geometry' in tp.__name__):
            #     return 'geometry<any>'

            # if tp is RecordID or (hasattr(tp, '__name__') and 'RecordID' in tp.__name__):
            #     # Try to extract table name from type arguments if available
            #     if hasattr(tp, '__args__') and tp.__args__:
            #         table_name = tp.__args__[0]
            #         if isinstance(table_name, str):
            #             return f'record<{table_name}>'
            #     return 'record<any>'

            # For other custom types, try to get the python type if available
            if hasattr(tp, '__origin__'):
                return self._pytype_to_surreal(field_name, tp.__origin__)


            # Default fallback for custom Pydantic types
            return 'any'

        # Optional / Union[..., None]
        if origin is Union or origin is getattr(__import__("types"), "UnionType", None):
            # if Optional[...] (Union with None)
            if any(a is type(None) for a in args):
                non_none = tuple(a for a in args if a is not type(None))
                match non_none:
                    case ():
                        return "NONE"
                    case (s, ):
                        inner = self._pytype_to_surreal(field_name, s, _skip_serializer_check=True)
                        # Don't wrap 'any' in option<> since 'any' already includes None
                        if inner == "any":
                            return "any"
                        return f"option<{inner}>"
                    case many:
                        others = " | ".join(self._pytype_to_surreal(field_name, some, _skip_serializer_check=True) for some in many)
                        # Don't wrap 'any' in option<> since 'any' already includes None
                        if others == "any":
                            return "any"
                        return f"option<{others}>"
            # generic union -> join pieces
            union_parts = [self._pytype_to_surreal(field_name, a, _skip_serializer_check=True) for a in args]
            # Deduplicate and simplify
            unique_parts = []
            seen = set()
            for part in union_parts:
                if part not in seen:
                    seen.add(part)
                    unique_parts.append(part)
            # If 'any' is in the union, just return 'any'
            if 'any' in unique_parts:
                return 'any'
            # If only one type after deduplication, return it directly
            if len(unique_parts) == 1:
                return unique_parts[0]
            return " | ".join(unique_parts)

        # Literal
        if origin is Literal:
            return self._literal_to_union(tp)

        # List / list[...] -> array<...>
        if origin is list:
            inner = args[0] if args else Any
            return f"array<{self._pytype_to_surreal(field_name, inner, _skip_serializer_check=True)}>"

        # Set / set[...] -> set<...>
        if origin is set:
            inner = args[0] if args else Any
            return f"set<{self._pytype_to_surreal(field_name, inner, _skip_serializer_check=True)}>"



        # Enum classes
        if inspect.isclass(tp) and issubclass(tp, Enum):
            return self._enum_to_literal_union(tp)

        # SurrealDB-specific types (check without needing __get_pydantic_core_schema__)
        if tp is Geometry:
            return 'geometry<any>'
        if tp is RecordID:
            return 'record<any>'

        # primitives
        if tp is str:
            return "string"
        if tp in (int, float):
            return "number"
        if tp is bool:
            return "bool"
        if tp in (date, datetime):
            return "datetime"

        # fallback
        return "any"

    @classmethod
    def _analyze_core_schema(cls, schema) -> str:
        """Analyze a Pydantic core schema object to determine the Surreal type."""

        if schema is None:
            return 'any'

        # Handle dict-based schemas
        if isinstance(schema, dict):
            schema_type = schema.get('type')

            # Check for function validators with wrapped schemas
            if schema_type in ('function-after', 'function-before', 'function-wrap', 'with-info'):
                # Look for the wrapped/inner schema
                if 'schema' in schema:
                    return cls._analyze_core_schema(schema['schema'])
                elif 'inner' in schema:
                    return cls._analyze_core_schema(schema['inner'])

            # Basic type mappings
            if schema_type == 'str':
                return 'string'
            elif schema_type == 'int':
                return 'number'
            elif schema_type == 'float':
                return 'number'
            elif schema_type == 'bool':
                return 'bool'
            elif schema_type == 'datetime':
                return 'datetime'
            elif schema_type == 'date':
                return 'datetime'
            elif schema_type == 'bytes':
                return 'bytes'
            elif schema_type == 'list':
                items_schema = schema.get('items_schema')
                if items_schema:
                    inner = cls._analyze_core_schema(items_schema)
                    return f'array<{inner}>'
                return 'array<any>'
            elif schema_type == 'dict':
                return 'object'
            elif schema_type == 'set':
                items_schema = schema.get('items_schema')
                if items_schema:
                    inner = cls._analyze_core_schema(items_schema)
                    return f'array<{inner}>'
                return 'array<any>'
            elif schema_type == 'tuple':
                return 'array<any>'
            elif schema_type in ('union', 'chain'):
                key = "choices" if schema_type == "union" else "steps"
                match sorted({cls._analyze_core_schema(step) for step in schema.get(key, [])}):
                    case []:
                        return "any"
                    case [one]:
                        return one
                    case many:
                        # filter any, otherwise it does not makes any sense
                        return ' | '.join(m for m in many if m != "any")

            elif schema_type == 'nullable':
                inner = schema.get('schema')
                if inner:
                    return f'option<{cls._analyze_core_schema(inner)}>'
                return 'option<any>'
            elif schema_type == 'none':
                return 'NONE'
            elif schema_type == 'literal':
                expected = schema.get('expected', [])
                if expected:
                    value = expected[0]
                    if value is None:
                        return 'NONE'
                    elif isinstance(value, str):
                        return f'"{value}"'
                    elif isinstance(value, bool):
                        return 'true' if value else 'false'
                    else:
                        return str(value)
            elif schema_type == 'any':
                return 'any'

        # Handle core_schema objects with attributes
        if hasattr(schema, '__dict__'):
            attrs = schema.__dict__
            if 'type' in attrs:
                # Reconstruct as dict and recurse
                return cls._analyze_core_schema(attrs)

        return 'any'

    # -------------------- schema generation ---------------------------------

    @staticmethod
    def target_name(tp):
        if inspect.isclass(tp) and issubclass(tp, BaseModel):
            return tp.__name__.lower()
        # fallback: use type __name__ or str(tp)
        return getattr(tp, "__name__", str(tp)).lower()


    def generate_table_sql(self) -> str:
        stmts = []
        if self.relation:
            in_tbl = self._pytype_to_surreal("_in", self.relation._in)
            out_tbl = self._pytype_to_surreal("_out", self.relation._out)
            in_tbl = re.sub(r'record<([^>]+)>', r'\1',  in_tbl)
            out_tbl = re.sub(r'record<([^>]+)>', r'\1',  out_tbl)
            stmts.append(f"DEFINE TABLE IF NOT EXISTS {self.name} TYPE RELATION IN {in_tbl} OUT {out_tbl};")
            if self.relation.symetric:
                stmts.append(f"DEFINE FIELD key ON TABLE {self.name} VALUE <string>array::sort([in, out]);")
                stmts.append(f"DEFINE INDEX only_one_link ON TABLE {self.name} FIELDS key UNIQUE;")
        else:
            stmts.append(f"DEFINE TABLE IF NOT EXISTS {self.name} SCHEMAFULL;")
        for ft in self.fields:
            if ft.name == "id": # only define if not None
                continue
            if ft.name == "is_stub_":
                continue
            surreal_t = self._pytype_to_surreal(ft.name, ft.field_type)
            stmts.append(f"DEFINE FIELD {self._quote_ident(ft.name)} ON {self.name} TYPE {surreal_t};")

        define_index = [
            f"DEFINE INDEX {field}_search ON TABLE {self.name} FIELDS {field} SEARCH ANALYZER {analyzer} BM25 HIGHLIGHTS;"
            for field, analyzer in self.index.items()
        ]
        return "\n".join(stmts) + "\n" + "\n".join(define_index)
