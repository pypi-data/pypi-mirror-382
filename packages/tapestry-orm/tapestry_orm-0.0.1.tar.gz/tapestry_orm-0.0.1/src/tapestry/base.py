from __future__ import annotations

import inspect

from enum import Enum
from copy import deepcopy
from itertools import chain
from queue import LifoQueue
from pydantic_core.core_schema import ValidationInfo
from pydantic.fields import FieldInfo, ComputedFieldInfo
from surrealdb import AsyncWsSurrealConnection, AsyncHttpSurrealConnection, RecordID
from typing import  Any, ClassVar, Optional, Self, Any, Unpack, Union, Type, get_args
from pydantic import BaseModel, field_validator, model_serializer, field_serializer, Field, ConfigDict, model_validator

from .table import Table, Reference
from .utils import convert_types, replace_type, flatten_type
from .field import Field as CustomField, NestedFieldDescriptor, ComputedFieldDescriptor


# Registry base class -------------------------------------------------------
class Base(BaseModel):
    """
    Base class for creating SurrealDB table models with Pydantic.

    The Base class provides the foundation for defining SurrealDB tables as Python classes
    using Pydantic models. All table models should inherit from this class, which handles
    automatic registration, schema generation, and serialization/deserialization.

    Attributes:
        id (RecordID | None): The SurrealDB record ID. Automatically assigned when records
            are created in the database. Can be None for new records.

    Class Attributes:
        _registry: Tuple of all registered tables in the system
        _tokenizers: Set of tokenizer definitions for full-text search
        _to_create: Queue for chaining object creations
        child_classes: Dictionary mapping table names to their model classes

    Example:
        >>> from tapestry import Base
        >>> from datetime import date
        >>>
        >>> class Person(Base):
        ...     first_name: str
        ...     last_name: str
        ...     date_of_birth: date
        ...
        >>> # Person is automatically registered and can generate SurrealDB schema
        >>> schema = Base.generate_schema()

    Notes:
        - Subclasses are automatically registered upon definition
        - Field types are automatically mapped to SurrealDB types
        - Supports relationships through Reference fields
        - Handles enum serialization automatically
        - Provides full-text search capabilities with Text fields
    """
    id: RecordID | None = Field(exclude=False, default = None)

    model_config = {
        "arbitrary_types_allowed": True,
        "use_enum_values": False, # would be great to have a 'use_enum_names'
        "validate_assignment": True
    }
    _registry: ClassVar[tuple[Table, ...]] = ()
    _tokenizers: ClassVar[set[str]] = set()
    _to_create: ClassVar[LifoQueue[Base]]
    child_classes: ClassVar[dict[str, Type[Base]]] = {}


    @classmethod
    @field_validator('id')
    def validate_record_id(cls, v: Any) -> Optional[RecordID]:
        """
        Validate and convert record ID values.

        Args:
            v: The value to validate (can be None, RecordID, or string)

        Returns:
            Optional[RecordID]: A valid RecordID or None

        Notes:
            Automatically converts string IDs to RecordID instances with the
            appropriate table name.
        """
        if v is None:
            return None
        if isinstance(v, RecordID):
            return v
        # Convert string to RecordID if needed
        return RecordID(cls.__name__.lower(), v)


    @model_serializer(mode="wrap")
    def _serialize(self, serializer, info):
        """
        Custom serializer for handling record references.

        When serializing nested objects, this method ensures that only the record ID
        is serialized for referenced records, not the entire object.

        Args:
            serializer: The default Pydantic serializer
            info: Serialization context information

        Returns:
            Serialized representation of the object or just its ID for references

        Raises:
            Exception: If attempting to reference a record that hasn't been created yet
        """
        if not info.context:
            return serializer(self)
        if info.context.get("root"):
            info.context["root"] = False
            return serializer(self)
        else:
            if self.id is None:
                raise Exception(f"You should create your record before referecing to it : create {self}")
                # self._to_create.put(self)
                # maybe check here in context if we are inserting in db
            return self.id


    @field_validator('*', mode='before')
    @classmethod
    def validate_enums(cls, v: Any, info: ValidationInfo) -> Any:
        """
        Universal validator for enum fields and record references.

        Automatically handles:
        - Converting enum names (strings) to enum instances
        - Validating enum values
        - Processing RecordID references

        Args:
            v: The value to validate
            info: Validation context with field information

        Returns:
            The validated/converted value
        """
        constructor = cls._table.name_to_type.get(info.field_name)
        if inspect.isclass(constructor) and issubclass(constructor, Enum):
            if isinstance(v, constructor):
                return v
            name = constructor[v]
            return name
        # if isinstance(v, RecordID) and not info.field_name == "id":
        #     try:
        #         constructor = cls.child_classes[v.table_name]
        #     except KeyError:
        #         return v
        #     values = {key: None for key in constructor.model_fields}
        #     values["id"] = v
        #     stub = constructor.model_construct(**values)
        #     # def _frozen_setattr(self, name, value):
        #     #        raise AttributeError(f"Instance {type(self).__name__} is frozen; cannot set {name!r}")
        #     # stub.__setattr__ = MethodType(_frozen_setattr, stub)
        #     print("stub : ", stub, constructor)
        #     return stub
        return v


    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]):
        discarded = kwargs.pop("discarded", False)
        # Create unique queue for each subclass
        # this queue will be used to chain several object creations
        cls._to_create = LifoQueue()
        cls._discarded = discarded
        return super().__init_subclass__(**kwargs)


    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        relation = kwargs.pop("relation", None)
        super().__pydantic_init_subclass__(**kwargs)

        if cls._discarded:
            return

        model_fields: dict[str, FieldInfo | ComputedFieldInfo] = deepcopy(cls.model_fields)
        model_fields.update(cls.model_computed_fields)
        fields: list[CustomField[Any]] = []
        for field_name, field_info in model_fields.items():
            field_type = field_info.annotation if isinstance(field_info, FieldInfo) else field_info.return_type
            if isinstance(field_info, ComputedFieldInfo):
                field_descriptor = ComputedFieldDescriptor[field_type](field_name, cls.__name__.lower(), field_type or Any, getattr(cls, field_name, None))
            else:
                field_descriptor = CustomField[field_type](field_name, cls.__name__.lower(), field_type or Any)
            fields.append(field_descriptor)

            # Handle different field types
            nested_class = None
            try:
                # Check if it's a Base subclass directly
                if field_type and hasattr(field_type, '__mro__') and Base in field_type.__mro__:
                    nested_class = field_type
                # Check if it's Optional[Base subclass] (Union with None)
                elif hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
                    # Get the args of the Union
                    args = getattr(field_type, '__args__', ())
                    # Filter out None and check if any remaining type is a Base subclass
                    for arg in args:
                        if arg is not type(None) and hasattr(arg, '__mro__') and Base in arg.__mro__:
                            nested_class = arg
                            break

                if nested_class:
                    # Create a nested field descriptor that allows chaining
                    nested_descriptor = NestedFieldDescriptor(field_name, cls.__name__.lower(), nested_class)
                    setattr(cls, field_name, nested_descriptor)
                else:
                    setattr(cls, field_name, field_descriptor)
            except (TypeError, AttributeError):
                # For other complex types, just use the field descriptor
                setattr(cls, field_name, field_descriptor)

            # replace Base instance with Union[annotation, RecordID]
            if field_name in cls.model_fields:
                cls.model_fields[field_name].annotation = replace_type(cls.model_fields[field_name].annotation, Base, Union[Base, RecordID])


        table = Table(name=cls.__name__.lower(), base_class=Base, model_class=cls, fields=tuple(fields), relation=relation)
        for tokenizer in table.tokenizers:
            Base._tokenizers.add(tokenizer.define())

        cls._table = table
        # I want to keep _registry as immutable as possible and only append data to it
        Base.add_table(table, cls)
        cls.model_rebuild(force=True)


    @classmethod
    def registered_tables(cls) -> set[str]:
        """
        Get the names of all registered tables.

        Returns:
            set[str]: Set of table names that have been registered

        Example:
            >>> tables = Base.registered_tables()
            >>> print(tables)
            {'person', 'entity', 'role', ...}
        """
        return {f.name for f in cls._registry}


    @classmethod
    def add_table(cls, table: Table, child_class: Type[Base]):
        """
        Register a new table in the system registry.

        Args:
            table: The Table definition to register
            child_class: The model class associated with the table

        Notes:
            This is called automatically when subclasses are defined.
            Users typically don't need to call this directly.
        """
        cls._registry = tuple(t for t in chain(cls._registry, (table, )))
        cls.child_classes[table.name] = child_class


    @classmethod
    def registered_models(cls) -> list[Table]:
        """
        Get all registered table definitions.

        Returns:
            list[Table]: List of Table objects that have been registered

        Example:
            >>> models = Base.registered_models()
            >>> for model in models:
            ...     print(f"Table: {model.name}")
        """
        return list(cls._registry)


    @classmethod
    def generate_schema(cls) -> str:
        """
        Generate complete SurrealQL schema for all registered tables.

        Creates the SQL statements needed to define all tables, fields, indexes,
        and tokenizers in SurrealDB. This should be executed when setting up
        a new database or updating the schema.

        Returns:
            str: Complete SurrealQL schema definition

        Example:
            >>> async with AsyncSurreal(url) as db:
            ...     await db.signin({"username": "root", "password": "root"})
            ...     await db.use("mydb", "myns")
            ...     schema = Base.generate_schema()
            ...     await db.query(schema)

        Notes:
            - Includes table definitions with SCHEMAFULL
            - Defines all fields with proper types
            - Sets up full-text search indexes
            - Configures tokenizers for text analysis
            - Creates relationship constraints
        """
        blocks = [t.generate_table_sql() for t in cls._registry]
        return "\n\n".join(chain(cls._tokenizers, blocks))


    @classmethod
    def deserialize_record(cls, data: dict) -> Any:
        """
        Deserialize a SurrealDB record into a Pydantic model instance.

        Automatically converts SurrealDB records to the appropriate model class
        based on the record's table name.

        Args:
            data: Dictionary containing the record data from SurrealDB

        Returns:
            An instance of the appropriate model class, or the original data
            if no matching model is found

        Notes:
            - Handles edge records by converting 'in' and 'out' to 'in_' and 'out_'
            - Automatically determines the model class from the record ID
            - Validates data using Pydantic validation
        """
        if not isinstance(data, dict):
            return data

        if "in" in data and "out" in data:
            data["in_"] = data.pop("in", None)
            data["out_"] = data.pop("out", None)

        # Get the model class from the record ID
        record_id = data.get('id')
        if not record_id or not isinstance(record_id, RecordID):
            return data

        model_class = cls.child_classes.get(record_id.table_name)
        if not model_class:
            return data

        # The model validator will handle RecordID conversion
        # here maybe specify if the users wants related records as ids or full objects
        return model_class.model_validate(data, context="could this parameter be of any use ?")


    @classmethod
    def deserialize_response(cls, response: Any) -> Any:
        """
        Deserialize a complete SurrealDB response.

        Recursively processes responses to convert all records to their
        appropriate model instances.

        Args:
            response: The response from SurrealDB (can be list, dict, or primitive)

        Returns:
            The deserialized response with records converted to model instances

        Example:
            >>> result = await db.select("person")
            >>> people = Base.deserialize_response(result)
            >>> # people is now a list of Person instances
        """
        if isinstance(response, list):
            return [cls.deserialize_record(item) if isinstance(item, dict) else item for item in response]
        elif isinstance(response, dict):
            return cls.deserialize_record(response)
        return response


    def db_dump(self) -> dict[str, Any]:
        """
        Serialize the model instance for database insertion/update.

        Prepares the model data for sending to SurrealDB by:
        - Removing the ID field (handled separately by SurrealDB)
        - Converting Python types to SurrealDB-compatible formats
        - Serializing nested objects appropriately

        Returns:
            dict[str, Any]: Dictionary ready for database operations

        Example:
            >>> person = Person(first_name="John", last_name="Doe")
            >>> data = person.db_dump()
            >>> await db.create("person", data)
        """
        serialized = self.model_dump(context={"root": True})
        serialized.pop('id', None)
        # this convert_types fonction is only here
        return convert_types(serialized)
