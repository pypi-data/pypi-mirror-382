from typing import Self, Iterable, ClassVar
from surrealdb import AsyncWsSurrealConnection, AsyncHttpSurrealConnection, RecordID

from .base import Base

class Node(Base, discarded=True):
    """
    Base class for SurrealDB node (non-relation) tables.

    Node represents standard tables in SurrealDB that are not relationships.
    All regular tables should inherit from this class to gain database
    operation methods like insert, create, and save.

    Class Attributes:
        _is_relation: Always False for Node tables

    Example:
        >>> from tapestry import Node
        >>> from datetime import date
        >>>
        >>> class Person(Node):
        ...     first_name: str
        ...     last_name: str
        ...     date_of_birth: date
        ...
        >>> # Create instances
        >>> person = Person(
        ...     first_name="John",
        ...     last_name="Doe",
        ...     date_of_birth=date(1990, 1, 1)
        ... )
        ...
        >>> # Insert into database
        >>> async with db_session as db:
        ...     await person.create(db)

    Notes:
        - Provides CRUD operations for non-relation tables
        - Automatically handles ID assignment from database
        - Supports batch inserts for efficiency
        - Works with SurrealDB's SCHEMAFULL tables
    """
    _is_relation: ClassVar[bool] = False

    @classmethod
    async def insert(
        cls,
        db: AsyncWsSurrealConnection | AsyncHttpSurrealConnection, others: Iterable[Self]
    ) -> list[Self]:
        """
        Batch insert multiple records into the database.

        Efficiently inserts multiple instances of the model into SurrealDB
        in a single operation. The original instances are updated with their
        assigned IDs from the database.

        Args:
            db: Active SurrealDB connection (WebSocket or HTTP)
            others: Iterable of model instances to insert

        Returns:
            list[Self]: The same instances with IDs assigned

        Example:
            >>> people = [
            ...     Person(first_name="John", last_name="Doe"),
            ...     Person(first_name="Jane", last_name="Smith"),
            ... ]
            >>> inserted = await Person.insert(db, people)
            >>> # All instances now have IDs assigned
            >>> for person in inserted:
            ...     print(person.id)

        Notes:
            - More efficient than multiple create() calls
            - Original instances are modified in place with IDs
            - All records are inserted in a single database transaction
        """
        others = list(others)
        inserted = await db.insert(
            cls.__name__.lower(),
            [other.db_dump() for other in others]
        )
        # Simply update IDs from response
        for insert, original in zip(inserted, others):
            original.id = insert["id"]
        return others


    async def create(
        self,
        db: AsyncWsSurrealConnection | AsyncHttpSurrealConnection
    ) -> Self:
        """
        Create a single record in the database.

        Inserts this instance into SurrealDB and updates it with the
        assigned record ID.

        Args:
            db: Active SurrealDB connection (WebSocket or HTTP)

        Returns:
            Self: The same instance with ID assigned

        Example:
            >>> person = Person(
            ...     first_name="John",
            ...     last_name="Doe",
            ...     date_of_birth=date(1990, 1, 1)
            ... )
            >>> await person.create(db)
            >>> print(person.id)  # Now has an ID like person:ulid

        Notes:
            - If the instance already has an ID, it will be used
            - Otherwise, SurrealDB generates a new unique ID
            - The instance is modified in place
        """
        thing = self.id if isinstance(self.id, RecordID) else self.__class__.__name__.lower()
        creation = await db.create(
            thing,
            self.db_dump()
        )
        assert isinstance(creation, dict)
        self.id = creation["id"]
        return self


    async def save(
        self,
        db: AsyncWsSurrealConnection | AsyncHttpSurrealConnection
    ) -> Self:
        """
        Update an existing record in the database.

        Saves the current state of this instance to SurrealDB, replacing
        the existing record with the same ID.

        Args:
            db: Active SurrealDB connection (WebSocket or HTTP)

        Returns:
            Self: The same instance, potentially with updated fields

        Example:
            >>> # Fetch an existing person
            >>> person = await Person.get(db, "person:123")
            >>> # Modify fields
            >>> person.first_name = "Jane"
            >>> # Save changes to database
            >>> await person.save(db)

        Notes:
            - Requires the instance to have an ID (from create() or query)
            - Performs a full replacement of the record
            - Use for updating existing records after modifications

        Raises:
            AssertionError: If the database operation returns unexpected data
        """
        thing = self.id if isinstance(self.id, RecordID) else self.__class__.__name__.lower()
        creation = await db.update(
            thing,
            self.db_dump()
        )
        assert isinstance(creation, dict)
        self.id = creation["id"]
        return self
