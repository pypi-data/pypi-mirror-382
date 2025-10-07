from __future__ import annotations

from typing import Any, ClassVar, Optional, Type, TypeVar, Unpack, Union, Self
from queue import LifoQueue
from pydantic import BaseModel, ConfigDict, Field
from pydantic.fields import FieldInfo, ComputedFieldInfo
from surrealdb import AsyncWsSurrealConnection, AsyncHttpSurrealConnection, RecordID

from .table import Table

T = TypeVar('T', bound='Base')

class Base(BaseModel):
    id: RecordID | None

    _registry: ClassVar[tuple[Table, ...]]
    _tokenizers: ClassVar[set[str]]
    _to_create: ClassVar[LifoQueue[Base]]
    child_classes: ClassVar[dict[str, Type[Base]]]
    _table: ClassVar[Table]
    _discarded: ClassVar[bool]

    @classmethod
    def validate_record_id(cls, v: Any) -> Optional[RecordID]: ...

    def _serialize(self, serializer: Any, info: Any) -> Any: ...

    @classmethod
    def validate_enums(cls, v: Any, info: Any) -> Any: ...

    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]) -> None: ...

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None: ...

    @classmethod
    def registered_tables(cls) -> set[str]: ...

    @classmethod
    def add_table(cls, table: Table, child_class: Type[Base]) -> None: ...

    @classmethod
    def registered_models(cls) -> list[Table]: ...

    @classmethod
    def generate_schema(cls) -> str: ...

    @classmethod
    def deserialize_record(cls, data: dict[str, Any]) -> Any: ...

    @classmethod
    def deserialize_response(cls, response: Any) -> Any: ...

    def db_dump(self) -> dict[str, Any]: ...
