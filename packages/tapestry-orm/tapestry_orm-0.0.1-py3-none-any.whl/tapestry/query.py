"""
Query builder for SurrealQL-like syntax in Python.

This module provides a fluent interface for building SurrealQL queries using
Python operators and method chaining. The Q class enables type-safe query
construction with support for graph traversals, filtering, and projections.

Example:
    >>> from tapestry import Q, Node
    >>>
    >>> class Person(Node):
    ...     name: str
    ...     age: int
    ...
    >>> # Simple query with filtering
    >>> adults = Q(Person).where(Person.age >= 18)
    >>> results = await adults.execute(db)
    >>>
    >>> # Graph traversal query
    >>> friends_of_john = (Q(Person)
    ...     .where(Person.name == "John")
    ...     >> FriendOf >> Person)
    >>> results = await friends_of_john.execute(db)
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional, Union, Type, TYPE_CHECKING, TypeVar, Generic, get_type_hints, overload
from dataclasses import dataclass, field as dataclass_field
from datetime import date, datetime
from pydantic.fields import FieldInfo, ComputedFieldInfo
from surrealdb import AsyncWsSurrealConnection, AsyncHttpSurrealConnection, RecordID

# Import at module level to avoid circular imports
if TYPE_CHECKING:
    from .node import Node
    from .edge import Edge

from .field import Traversal, Condition, Direction
from .base import Base

# TypeVar for the model being queried
T = TypeVar('T', bound='Base')


@dataclass
class Q(Generic[T]):
    """
    Main query builder class for constructing SurrealQL queries.

    The Q class provides a fluent interface for building complex database
    queries with support for filtering, graph traversals, and projections.
    It uses Python operators and method chaining to create readable and
    type-safe queries.

    Type Parameters:
        T: The model type being queried (Node or Edge subclass)

    Attributes:
        table: The Node or Edge class to query from
        _select_fields: List of specific fields to select
        _where_clause: WHERE condition for filtering
        _traversals: List of graph traversals to perform
        _value_only: Whether to return only values without field names

    Example:
        >>> # Basic query - type is inferred as Q[Person]
        >>> query = Q(Person)
        >>>
        >>> # With filtering
        >>> adults = Q(Person).where(Person.age >= 18)
        >>>
        >>> # Select specific fields
        >>> names = Q(Person).select("first_name", "last_name")
        >>>
        >>> # Graph traversal using >> operator
        >>> managers = Q(Person) >> BelongsTo >> Role.where(Role.title == "Manager")
        >>>
        >>> # Execute the query - returns list[Person]
        >>> results = await query.execute(db)

    Notes:
        - Uses >> for forward traversal and << for backward traversal
        - Automatically deserializes results to model instances
        - Supports chaining multiple operations
        - Generates valid SurrealQL syntax
        - Preserves type information for IDE autocomplete
    """

    table: Type[T]
    _select_fields: list[str] = dataclass_field(default_factory=list)
    _where_clause: Optional[str] = None
    _traversals: list[Traversal] = dataclass_field(default_factory=list)
    _value_only: bool = False

    def __post_init__(self):
        self.from_table = self.table.__name__.lower()

    def select(self, *fields: str) -> Q[T]:
        """
        Specify fields to include in the query results.

        Args:
            *fields: Field names to select from the table

        Returns:
            Q[T]: The query instance for chaining

        Example:
            >>> query = Q(Person).select("first_name", "last_name", "email")
            >>> # Generates: SELECT first_name, last_name, email FROM person;

        Notes:
            - If not called, all fields are selected (SELECT *)
            - Can be combined with value() for different output formats
        """
        self._select_fields.extend(fields)
        return self

    def value(self) -> Q[T]:
        """
        Return only values without field names.

        Makes the query return raw values instead of objects with field names.
        Useful for extracting single values or when field names are not needed.

        Returns:
            Q[T]: The query instance for chaining

        Example:
            >>> # Get just the names as a list of strings
            >>> names = Q(Person).select("name").value()
            >>> # Generates: SELECT VALUE name FROM person;
            >>>
            >>> # Get IDs from a traversal
            >>> ids = Q(Person).value() >> FriendOf >> Person
            >>> # Generates: SELECT VALUE ->friend_of->person.* FROM person;

        Notes:
            - Changes SELECT to SELECT VALUE in the generated query
            - Affects the structure of returned results
        """
        self._value_only = True
        return self

    def where(self, condition: Condition) -> Q[T]:
        """
        Add a WHERE clause to filter query results.

        Args:
            condition: A Condition object created using field comparisons

        Returns:
            Q[T]: The query instance for chaining

        Example:
            >>> # Simple condition
            >>> adults = Q(Person).where(Person.age >= 18)
            >>>
            >>> # Complex condition with AND
            >>> query = Q(Person).where(
            ...     (Person.age >= 18) & (Person.city == "Paris")
            ... )
            >>>
            >>> # Using OR
            >>> query = Q(Person).where(
            ...     (Person.role == "admin") | (Person.role == "moderator")
            ... )
            >>>
            >>> # Negation with ~
            >>> active = Q(Person).where(~(Person.status == "deleted"))

        Notes:
            - Conditions are created using field comparisons (==, !=, <, >, <=, >=)
            - Use & for AND, | for OR, ~ for NOT
            - Supports full-text search with @ operator
        """
        self._where_clause = condition.to_surreal()
        return self

    def traverse(self, traversal: Traversal) -> Q[T]:
        """
        Add a graph traversal to navigate relationships.

        Args:
            traversal: A Traversal object defining the path to follow

        Returns:
            Q[T]: The query instance for chaining

        Example:
            >>> # Direct traversal object
            >>> from tapestry.field import Traversal, Direction
            >>> traversal = Traversal(Direction.FORWARD, FriendOf)
            >>> query = Q(Person).traverse(traversal)

        Notes:
            - Prefer using >> and << operators for simpler syntax
            - This method gives more control over traversal configuration
        """
        self._traversals.append(traversal)
        return self

    def __rshift__(self, other: Union[Type['Edge'], Type['Node'], Traversal]) -> Q[T]:
        """
        Forward traversal using >> operator for graph navigation.

        Follows relationships in the forward direction (from in_ to out_).

        Args:
            other: An Edge class, Node class, or Traversal to follow

        Returns:
            Q[T]: The query instance for continued chaining

        Example:
            >>> # Navigate from Person through BelongsTo to Role
            >>> managers = Q(Person) >> BelongsTo >> Role
            >>> # Generates: SELECT ->belongs_to->role.* FROM person;
            >>>
            >>> # With conditions on edges
            >>> recent = (Q(Person) >>
            ...          BelongsTo.where(BelongsTo.begin_date > date(2020, 1, 1)) >>
            ...          Role)
            >>>
            >>> # Chain multiple traversals
            >>> network = Q(Person) >> FriendOf >> Person >> WorksAt >> Company

        Notes:
            - Forward means following from 'in_' to 'out_' of edges
            - Can traverse through multiple relationships
            - Supports conditional edges with .where()
        """
        if isinstance(other, type):
            traversal = Traversal(Direction.FORWARD, other)
            self._traversals.append(traversal)
        elif isinstance(other, Traversal):
            self._traversals.append(other)
        else:
            # Handle EdgeWithCondition
            if hasattr(other, 'to_traversal'):
                traversal = other.to_traversal(Direction.FORWARD)
                self._traversals.append(traversal)
            else:
                traversal = Traversal(Direction.FORWARD, other)
                self._traversals.append(traversal)
        return self

    def __lshift__(self, other: Union[Type['Edge'], Type['Node'], Traversal]) -> Q[T]:
        """
        Backward traversal using << operator for reverse graph navigation.

        Follows relationships in the backward direction (from out_ to in_).

        Args:
            other: An Edge class, Node class, or Traversal to follow

        Returns:
            Q[T]: The query instance for continued chaining

        Example:
            >>> # Find all people who belong to a specific role
            >>> members = Q(Role).where(Role.title == "Manager") << BelongsTo << Person
            >>> # Generates: SELECT <-belongs_to<-person.* FROM role WHERE title IS "Manager";
            >>>
            >>> # Reverse traversal to find who manages a department
            >>> managers = Q(Department) << Manages << Person
            >>>
            >>> # Mix forward and backward
            >>> related = Q(Person) >> FriendOf >> Person << WorksAt << Company

        Notes:
            - Backward means following from 'out_' to 'in_' of edges
            - Useful for finding inverse relationships
            - Can be combined with forward traversals
        """
        if isinstance(other, type):
            traversal = Traversal(Direction.BACKWARD, other)
            self._traversals.append(traversal)
        elif isinstance(other, Traversal):
            # Keep the original direction
            self._traversals.append(other)
        else:
            # Handle EdgeWithCondition
            if hasattr(other, 'to_traversal'):
                traversal = other.to_traversal(Direction.BACKWARD)
                self._traversals.append(traversal)
            else:
                traversal = Traversal(Direction.BACKWARD, other)
                self._traversals.append(traversal)
        return self

    def to_surreal(self) -> str:
        """
        Convert the query to SurrealQL syntax.

        Generates the complete SurrealQL query string that can be
        executed against a SurrealDB database.

        Returns:
            str: The SurrealQL query string

        Example:
            >>> query = (Q(Person)
            ...     .where(Person.age >= 18)
            ...     .select("name", "email"))
            >>> print(query.to_surreal())
            'SELECT name, email FROM person WHERE age >= 18;'
            >>>
            >>> traversal = Q(Person) >> FriendOf >> Person
            >>> print(traversal.to_surreal())
            'SELECT ->friend_of->person.* FROM person;'

        Notes:
            - Always ends with a semicolon
            - Generates valid SurrealQL syntax
            - Handles all query components (SELECT, FROM, WHERE, traversals)
        """
        parts = []

        # SELECT clause
        if self._value_only:
            parts.append("SELECT VALUE")
        elif self._select_fields:
            parts.append(f"SELECT {', '.join(self._select_fields)}")
        else:
            parts.append("SELECT")

        # Add traversals to the SELECT clause
        if self._traversals:
            traversal_str = self._build_traversal_string()
            if self._value_only or self._select_fields:
                parts[-1] += f" {traversal_str}"
            else:
                parts[-1] += f" {traversal_str}"
        elif not self._select_fields and not self._value_only:
            parts[-1] += " *"

        # FROM clause
        if self.from_table:
            parts.append(f"FROM {self.from_table}")

        # WHERE clause
        if self._where_clause:
            parts.append(f"WHERE {self._where_clause}")

        return " ".join(parts) + ";"

    def _build_traversal_string(self) -> str:
        """
        Build the traversal part of the query.

        Internal method that constructs the graph traversal syntax
        from the list of traversals.

        Returns:
            str: The traversal string for the query
        """
        return "".join(t.to_surreal() for t in self._traversals)

    async def execute(self, con: AsyncWsSurrealConnection | AsyncHttpSurrealConnection) -> list[T]:
        """
        Execute the query and return deserialized results.

        Runs the generated SurrealQL query against the database and
        automatically deserializes the results into the appropriate
        model instances based on the Base registry.

        Args:
            con: Active SurrealDB connection (WebSocket or HTTP)

        Returns:
            list[T]: The query results, deserialized to model instances

        Example:
            >>> # Get all adults as Person instances
            >>> query = Q(Person).where(Person.age >= 18)
            >>> people = await query.execute(db)
            >>> for person in people:
            ...     print(f"{person.first_name} {person.last_name}")
            >>>
            >>> # Get names only
            >>> names = await Q(Person).select("name").value().execute(db)
            >>> print(names)  # ['John', 'Jane', ...]

        Notes:
            - Automatically converts RecordIDs to model instances
            - Handles both single records and lists
            - Preserves non-record data types
            - Uses the Base.deserialize_response for conversion

        Raises:
            Exception: If the database query fails
        """

        result = await con.query(self.to_surreal())

        # If no results or not a list, return as-is
        if not result or not isinstance(result, list):
            return result

        # Let Base handle deserialization
        return Base.deserialize_response(result)
