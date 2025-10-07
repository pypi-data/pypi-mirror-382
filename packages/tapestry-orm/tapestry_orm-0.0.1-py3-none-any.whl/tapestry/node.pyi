from __future__ import annotations

from typing import ClassVar, Iterable, Self, TypeVar
from surrealdb import AsyncWsSurrealConnection, AsyncHttpSurrealConnection

from .base import Base

T = TypeVar('T', bound='Node')

class Node(Base):
    _is_relation: ClassVar[bool]

    @classmethod
    async def insert(
        cls: type[T],
        db: AsyncWsSurrealConnection | AsyncHttpSurrealConnection,
        others: Iterable[T]
    ) -> list[T]: ...

    async def create(
        self: T,
        db: AsyncWsSurrealConnection | AsyncHttpSurrealConnection
    ) -> T: ...

    async def save(
        self: T,
        db: AsyncWsSurrealConnection | AsyncHttpSurrealConnection
    ) -> T: ...
