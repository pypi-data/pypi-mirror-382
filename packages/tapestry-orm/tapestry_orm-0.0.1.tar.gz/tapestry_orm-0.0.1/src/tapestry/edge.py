from abc import ABC
from copy import deepcopy
from typing import Self, Iterable, get_type_hints, Any, ClassVar, Union, TYPE_CHECKING
from pydantic.fields import FieldInfo, ComputedFieldInfo
from surrealdb import AsyncWsSurrealConnection, AsyncHttpSurrealConnection, RecordID


from .base import Base
from .node import Node
from .utils import replace_type
from .table import Table, Link, flatten_type
from .field import Traversal, Direction, Condition, LogicalCondition, Field


class Edge(Base, ABC, discarded=True):
    """
    Base class for SurrealDB edge (relation) tables.

    Edge represents relationship tables in SurrealDB that connect two nodes.
    All relationship tables should inherit from this class and define
    'in_' and 'out_' fields to specify the connected node types.

    Class Attributes:
        _directed (bool): Whether the relationship is directional (default: True)

    Required Fields:
        in_: The source node of the relationship
        out_: The target node of the relationship

    Example:
        >>> from tapestry import Edge, Node
        >>> from datetime import date
        >>>
        >>> class Person(Node):
        ...     name: str
        ...
        >>> class Role(Node):
        ...     title: str
        ...
        >>> class BelongsTo(Edge):
        ...     in_: Person  # Person belongs to Role
        ...     out_: Role
        ...     begin_date: date
        ...     end_date: date | None = None
        ...
        >>> # Create a relationship
        >>> person = Person(name="John Doe")
        >>> role = Role(title="Manager")
        >>> belongs = BelongsTo(
        ...     in_=person,
        ...     out_=role,
        ...     begin_date=date(2020, 1, 1)
        ... )
        >>> await belongs.relate(db)

    Notes:
        - Requires both 'in_' and 'out_' fields to be defined
        - Automatically creates SurrealDB RELATION tables
        - Supports directional and bidirectional relationships
        - Can have additional fields beyond in_ and out_
        - Use relate() instead of create() for edge records
    """
    # in_: Node
    # out_: Node
    #
    _directed: bool = True

    def __init_subclass__(cls, directed: bool = True, **kwargs):
        """
        Configure edge subclasses with relationship properties.

        Args:
            directed: Whether the relationship is directional. If False,
                     creates a bidirectional relationship where in/out
                     order doesn't matter.
            **kwargs: Additional configuration passed to parent

        Raises:
            TypeError: If the subclass doesn't define both 'in_' and 'out_' fields
        """
        super().__init_subclass__(**kwargs)

        # Get type hints for the subclass
        hints = get_type_hints(cls)

        # Check if required fields are annotated
        required_fields = {'in_', 'out_'}
        missing_fields = required_fields - set(hints.keys())
        if missing_fields:
            raise TypeError(
                f"Class {cls.__name__} must have field annotations for: {missing_fields}"
            )

        cls._directed = directed


    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        relation = None
        in_, out_ = cls.model_fields.pop('in_', None), cls.model_fields.pop('out_', None)
        if in_ or out_:
            if in_ and out_:
                assert in_.annotation
                assert out_.annotation
                assert all(issubclass(t, Node) for t in flatten_type(in_.annotation))
                assert all(issubclass(t, Node) for t in flatten_type(out_.annotation))
                relation = Link(_in=in_.annotation, _out=out_.annotation, symetric=not cls._directed)
                cls.is_relation = True
            else:
                raise Exception("You need to specify both `_in` and `_out` to define a relation")
        else:
            raise Exception("You need to specify `_in` and `_out` to define an Edge")
        super().__pydantic_init_subclass__(relation=relation, **kwargs)
        # need to add those back for validation at instanciation
        # otherwise, the field is skipped
        in_.annotation = replace_type(in_.annotation, Base, Union[Base, RecordID])
        out_.annotation = replace_type(out_.annotation, Base, Union[Base, RecordID])
        cls.model_fields["in_"] = in_
        cls.model_fields["out_"] = out_
        cls.model_rebuild(force=True)



    def db_dump(self) -> dict[str, Any]:
        """
        Serialize the edge instance for database insertion.

        Converts Python field names to SurrealDB format by renaming
        'in_' to 'in' and 'out_' to 'out'.

        Returns:
            dict[str, Any]: Dictionary ready for SurrealDB relation operations
        """
        dump = super().db_dump()
        dump["in"] = dump.pop("in_")
        dump["out"] = dump.pop("out_")
        return dump


    async def relate(
        self,
        db: AsyncWsSurrealConnection | AsyncHttpSurrealConnection
    ) -> Self:
        """
        Create a relationship record in the database.

        Creates an edge record connecting two nodes in SurrealDB.
        This is the primary method for creating relationships.

        Args:
            db: Active SurrealDB connection (WebSocket or HTTP)

        Returns:
            Self: The same instance with ID assigned

        Example:
            >>> person = await Person.create(db)
            >>> role = await Role.create(db)
            >>> belongs = BelongsTo(
            ...     in_=person,
            ...     out_=role,
            ...     begin_date=date.today()
            ... )
            >>> await belongs.relate(db)
            >>> print(belongs.id)  # Has an ID like belongs_to:xyz

        Raises:
            Exception: If called on a non-relation table

        Notes:
            - Both in_ and out_ nodes must exist in the database
            - Creates a directed or bidirectional edge based on class configuration
            - The edge record gets a unique ID from SurrealDB
        """
        if not self.is_relation:
            raise Exception("You should use .create() to create a record")
        thing = self.__class__.__name__.lower()
        relation = await db.insert_relation(
            thing,
            self.db_dump()
        )
        if isinstance(relation, list):
            self.id = relation[0]["id"]
        else:
            self.id = relation["id"]
        return self


    @classmethod
    async def insert(
        cls,
        db: AsyncWsSurrealConnection | AsyncHttpSurrealConnection, others: Iterable[Self]
    ) -> list[Self]:
        """
        Batch insert multiple edge records into the database.

        Efficiently creates multiple relationships in a single operation.
        All edge instances are updated with their assigned IDs.

        Args:
            db: Active SurrealDB connection (WebSocket or HTTP)
            others: Iterable of edge instances to insert

        Returns:
            list[Self]: The same instances with IDs assigned

        Example:
            >>> relationships = [
            ...     BelongsTo(in_=person1, out_=role1, begin_date=date(2020, 1, 1)),
            ...     BelongsTo(in_=person2, out_=role2, begin_date=date(2021, 1, 1)),
            ... ]
            >>> inserted = await BelongsTo.insert(db, relationships)
            >>> # All relationships now have IDs

        Notes:
            - More efficient than multiple relate() calls
            - All edges are inserted in a single transaction
            - Original instances are modified with IDs
        """
        others = list(others)
        inserted = await db.insert_relation(
            cls.__name__.lower(),
            [other.db_dump() for other in others]
        )
        for insert, original in zip(inserted, others):
            original.id = insert["id"]
        return others

    @classmethod
    def where(cls, condition):
        """
        Add a WHERE condition to this edge for use in graph traversals.

        Creates a conditional edge that can be used in query traversals
        to filter relationships based on their properties.

        Args:
            condition: A condition expression that filters edge records

        Returns:
            EdgeWithCondition: A wrapped edge class with the condition attached

        Example:
            >>> # Find all people who belong to roles that started after 2020
            >>> query = (Q(Person) >>
            ...          BelongsTo.where(BelongsTo.begin_date > date(2020, 1, 1)) >>
            ...          Role)
            >>> results = await query.execute(db)

        Notes:
            - Used primarily in graph traversal queries
            - Conditions are applied during traversal, not at definition
            - Can filter based on any edge properties
        """

        # Create a new class-like object that wraps the Edge with a condition
        class EdgeWithCondition:
            def __init__(self, edge_class, condition):
                self.edge_class = edge_class
                self.condition = condition

            def __repr__(self):
                return f"{self.edge_class.__name__.lower()}[WHERE {self.condition.to_surreal()}]"

            # Allow this to be used in traversals
            def to_traversal(self, direction: Direction) -> Traversal:
                traversal = Traversal(direction, self.edge_class)
                traversal.where_condition = self.condition
                return traversal

        return EdgeWithCondition(cls, condition)
