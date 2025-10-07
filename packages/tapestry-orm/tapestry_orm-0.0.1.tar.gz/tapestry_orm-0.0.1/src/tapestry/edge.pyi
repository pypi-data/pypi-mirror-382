from __future__ import annotations

from abc import ABC
from typing import ClassVar, Iterable, TypeVar, Type
from surrealdb import AsyncWsSurrealConnection, AsyncHttpSurrealConnection

from .base import Base
from .node import Node
from .field import Condition, Direction, Traversal

T = TypeVar('T', bound='Edge')

class EdgeWithCondition:
    edge_class: Type[Edge]
    condition: Condition

    def __init__(self, edge_class: Type[Edge], condition: Condition) -> None: ...
    def __repr__(self) -> str: ...
    def to_traversal(self, direction: Direction) -> Traversal: ...

class Edge(Base, ABC):
    _directed: ClassVar[bool]
    is_relation: ClassVar[bool]

    def __init_subclass__(cls, directed: bool = True, **kwargs: object) -> None: ...

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: object) -> None: ...

    def db_dump(self) -> dict[str, object]: ...

    async def relate(
        self: T,
        db: AsyncWsSurrealConnection | AsyncHttpSurrealConnection
    ) -> T: ...

    @classmethod
    async def insert(
        cls: type[T],
        db: AsyncWsSurrealConnection | AsyncHttpSurrealConnection,
        others: Iterable[T]
    ) -> list[T]: ...

    @classmethod
    def where(cls: type[T], condition: Condition) -> EdgeWithCondition: ...
