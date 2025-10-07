from __future__ import annotations

from typing import TypeVar, Generic, Type, Union, Any, Optional, overload
from enum import Enum
from dataclasses import dataclass
from surrealdb import RecordID

from .node import Node
from .edge import Edge

T = TypeVar('T')

class Field(Generic[T]):
    name: str
    model_class: str
    field_type: Type[T]

    def __init__(self, name: str, model_class: str, field_type: Type[T]) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> Condition: ...  # type: ignore[override]
    def __ne__(self, other: object) -> Condition: ...  # type: ignore[override]
    def __lt__(self, other: T) -> Condition: ...
    def __le__(self, other: T) -> Condition: ...
    def __gt__(self, other: T) -> Condition: ...
    def __ge__(self, other: T) -> Condition: ...
    def __matmul__(self, other: T) -> Condition: ...

class ComputedFieldDescriptor(Field[T]):
    original_descriptor: Optional[property]

    def __init__(
        self,
        name: str,
        model_class: str,
        field_type: Type[T],
        original_descriptor: Optional[property] = None
    ) -> None: ...
    def __get__(self, instance: Any, owner: Type[Any]) -> T | ComputedFieldDescriptor[T]: ...
    def __set__(self, instance: Any, value: T) -> None: ...
    def __delete__(self, instance: Any) -> None: ...
    def __matmul__(self, other: T) -> Condition: ...

class NestedField(Field[T]):
    path: str
    parent_class: str

    def __init__(self, path: str, parent_class: str, field_type: Type[T]) -> None: ...
    def __repr__(self) -> str: ...

class NestedFieldDescriptor:
    field_name: str
    parent_class: str
    nested_class: type

    def __init__(self, field_name: str, parent_class: str, nested_class: type) -> None: ...
    def __eq__(self, other: object) -> Condition: ...  # type: ignore[override]
    def __ne__(self, other: object) -> Condition: ...  # type: ignore[override]
    def __matmul__(self, other: Any) -> Condition: ...

class Direction(Enum):
    FORWARD = "->"
    BACKWARD = "<-"
    BIDIRECTIONAL = "<->"

@dataclass
class Condition:
    left: Any
    operator: str
    right: Any

    def __and__(self, other: Condition) -> LogicalCondition: ...
    def __or__(self, other: Condition) -> LogicalCondition: ...
    def __invert__(self) -> NotCondition: ...
    def to_surreal(self) -> str: ...
    def _format_value(self, value: Any) -> str: ...

@dataclass
class LogicalCondition:
    left: Union[Condition, LogicalCondition]
    operator: str
    right: Union[Condition, LogicalCondition]

    def __and__(self, other: Union[Condition, LogicalCondition]) -> LogicalCondition: ...
    def __or__(self, other: Union[Condition, LogicalCondition]) -> LogicalCondition: ...
    def to_surreal(self) -> str: ...

@dataclass
class NotCondition:
    condition: Union[Condition, LogicalCondition]

    def to_surreal(self) -> str: ...

@dataclass
class Traversal:
    direction: Direction
    target: Union[Type[Node], Type[Edge], str]
    recursion_depth: int
    select_fields: Optional[str]
    where_condition: Optional[Union[Condition, LogicalCondition]]

    def __init__(
        self,
        direction: Direction,
        target: Union[Type[Node], Type[Edge], str],
        recursion_depth: int = 1,
        select_fields: Optional[str] = None,
        where_condition: Optional[Union[Condition, LogicalCondition]] = None
    ) -> None: ...
    def recurse(self, depth: int) -> Traversal: ...
    def select(self, fields: str = "*") -> Traversal: ...
    def where(self, condition: Union[Condition, LogicalCondition]) -> Traversal: ...
    def to_surreal(self) -> str: ...
    def _get_target_name(self) -> str: ...
