from __future__ import annotations

from enum import Enum
from typing import Any, Optional, Union, Type, TypeVar, Generic, TYPE_CHECKING
from dataclasses import dataclass, field as dataclass_field
from pydantic.fields import FieldInfo, ComputedFieldInfo
from surrealdb import RecordID


# Import at module level to avoid circular imports
if TYPE_CHECKING:
    from .node import Node
    from .edge import Edge


T = TypeVar('T')

class Field(Generic[T]):
    """Represents a field in a SurrealDB model with type-safe comparisons."""

    def __init__(self, name: str, model_class: str, field_type: Type[T]):
        self.name = name
        self.model_class = model_class
        self.field_type = field_type

    def __repr__(self):
        return f"{self.model_class}.{self.name}"

    # Comparison operators with proper type hints
    def __eq__(self, other: T) -> Condition:  # type: ignore[override]
        return Condition(self, "==", other)

    def __ne__(self, other: T) -> Condition:  # type: ignore[override]
        return Condition(self, "!=", other)

    def __lt__(self, other: T) -> Condition:
        return Condition(self, "<", other)

    def __le__(self, other: T) -> Condition:
        return Condition(self, "<=", other)

    def __gt__(self, other: T) -> Condition:
        return Condition(self, ">", other)

    def __ge__(self, other: T) -> Condition:
        return Condition(self, ">=", other)

    def __matmul__(self, other: T) -> Condition:
        """Fulltext search operator using @ symbol."""
        return Condition(self, "@", other)


class ComputedFieldDescriptor(Field[T]):
    """Descriptor for computed fields that delegates to Pydantic's property."""

    def __init__(self, name: str, model_class: str, field_type: Type[T], original_descriptor: Optional[property] = None):
        super().__init__(name, model_class, field_type)
        self.original_descriptor = original_descriptor

    def __get__(self, instance, owner):
        if instance is None:
            # When accessed on the class, return the Field for query building
            return self
        # When accessed on an instance, delegate to Pydantic's descriptor
        if self.original_descriptor:
            return self.original_descriptor.__get__(instance, owner)
        raise AttributeError(f"No descriptor for {self.name}")

    def __set__(self, instance, value):
        if hasattr(self.original_descriptor, '__set__'):
            return self.original_descriptor.__set__(instance, value)
        raise AttributeError(f"can't set attribute {self.name}")

    def __delete__(self, instance):
        if hasattr(self.original_descriptor, '__delete__'):
            return self.original_descriptor.__delete__(instance)
        raise AttributeError(f"can't delete attribute {self.name}")

    def __matmul__(self, other: T) -> Condition:
        """Fulltext search operator using @ symbol."""
        return Condition(self, "@", other)


class NestedField(Field[T]):
    """Field representing a nested path like role.entity."""

    def __init__(self, path: str, parent_class: str, field_type: Type[T]):
        self.path = path
        self.parent_class = parent_class
        self.field_type = field_type
        # Use the full path as the name
        super().__init__(path, parent_class, field_type)

    def __repr__(self):
        return f"{self.parent_class}.{self.path}"


class NestedFieldDescriptor:
    """Descriptor for nested field access in queries."""

    def __init__(self, field_name: str, parent_class: str, nested_class: type):
        self.field_name = field_name
        self.parent_class = parent_class
        self.nested_class = nested_class

        # Create field descriptors for the nested class
        if hasattr(nested_class, 'model_fields'):
            for nested_field_name, nested_field_info in nested_class.model_fields.items():
                nested_field_type = nested_field_info.annotation if isinstance(nested_field_info, FieldInfo) else nested_field_info.return_type
                # Create a custom field that represents the nested path
                nested_field = NestedField(f"{field_name}.{nested_field_name}", parent_class, nested_field_type)
                setattr(self, nested_field_name, nested_field)

    def __eq__(self, other):
        """Allow direct comparison on the nested field."""
        field = Field(self.field_name, self.parent_class, self.nested_class)
        return Condition(field, "==", other)

    def __ne__(self, other):
        field = Field(self.field_name, self.parent_class, self.nested_class)
        return Condition(field, "!=", other)

    def __matmul__(self, other):
        """Allow fulltext search on the nested field."""
        field = Field(self.field_name, self.parent_class, self.nested_class)
        return Condition(field, "@", other)


class Direction(Enum):
    """Graph traversal direction."""
    FORWARD = "->"
    BACKWARD = "<-"
    BIDIRECTIONAL = "<->"





@dataclass
class Condition:
    """Represents a query condition."""

    left: Any
    operator: str
    right: Any

    def __and__(self, other: Condition) -> LogicalCondition:
        """Combine conditions with AND."""
        return LogicalCondition(self, "AND", other)

    def __or__(self, other: Condition) -> LogicalCondition:
        """Combine conditions with OR."""
        return LogicalCondition(self, "OR", other)

    def __invert__(self) -> NotCondition:
        """Negate the condition."""
        return NotCondition(self)

    def to_surreal(self) -> str:
        """Convert to SurrealQL syntax."""
        left_str = self._format_value(self.left)
        right_str = self._format_value(self.right)

        # Handle different operator types
        if self.operator in ("=", "=="):
            # Use = for RecordID comparisons, IS for other values
            if isinstance(self.right, RecordID) or (hasattr(self.right, "id") and isinstance(self.right.id, RecordID)):
                op = "="
            else:
                op = "IS"
        elif self.operator == "!=":
            if isinstance(self.right, RecordID) or (hasattr(self.right, "id") and isinstance(self.right.id, RecordID)):
                op = "!="
            else:
                op = "IS NOT"
        elif self.operator == "@":
            # Fulltext search operator - SurrealDB uses @N@ syntax where N is the index position
            # We default to @0@ for the first fulltext index
            op = "@0@"
        else:
            op = self.operator

        return f"{left_str} {op} {right_str}"

    def _format_value(self, value: Any) -> str:
        """Format a value for SurrealQL."""
        if isinstance(value, Field):
            return value.name
        elif isinstance(value, RecordID):
            return f"{value.table_name}:{value.id}"
        elif hasattr(value, "id") and isinstance(value.id, RecordID):
            return f"{value.id.table_name}:{value.id.id}"
        elif isinstance(value, str):
            # Check if it's a field reference or a literal string
            if "." in value and not value.startswith('"'):
                return value  # Field reference
            return f'"{value}"'  # String literal
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif value is None:
            return "NULL"
        elif hasattr(value, '__class__') and hasattr(value.__class__, '__mro__'):
            # Check if it's an Enum
            if Enum in value.__class__.__mro__:
                # Use the enum's value if it's a string, otherwise use its name
                if isinstance(value.value, str):
                    return f'"{value.value}"'
                else:
                    return f'"{value.name}"'
        return str(value)


@dataclass
class LogicalCondition:
    """Represents a logical combination of conditions."""

    left: Union[Condition, LogicalCondition]
    operator: str
    right: Union[Condition, LogicalCondition]

    def __and__(self, other: Union[Condition, LogicalCondition]) -> LogicalCondition:
        """Combine with another condition using AND."""
        return LogicalCondition(self, "AND", other)

    def __or__(self, other: Union[Condition, LogicalCondition]) -> LogicalCondition:
        """Combine with another condition using OR."""
        return LogicalCondition(self, "OR", other)

    def to_surreal(self) -> str:
        """Convert to SurrealQL syntax."""
        left_str = self.left.to_surreal()
        right_str = self.right.to_surreal()
        return f"({left_str} {self.operator} {right_str})"


@dataclass
class NotCondition:
    """Represents a negated condition."""

    condition: Union[Condition, LogicalCondition]

    def to_surreal(self) -> str:
        """Convert to SurrealQL syntax."""
        return f"NOT ({self.condition.to_surreal()})"


@dataclass
class Traversal:
    """Represents a graph traversal operation."""

    direction: Direction
    target: Union[Type[Node], Type[Edge], str]
    recursion_depth: int = 1
    select_fields: Optional[str] = None
    where_condition: Optional[Union[Condition, LogicalCondition]] = None

    def recurse(self, depth: int) -> Traversal:
        """Set recursion depth for this traversal."""
        self.recursion_depth = depth
        return self

    def select(self, fields: str = "*") -> Traversal:
        """Select specific fields from the traversal result."""
        self.select_fields = fields
        return self

    def where(self, condition: Union[Condition, LogicalCondition]) -> Traversal:
        """Add a WHERE condition to this traversal."""
        self.where_condition = condition
        return self

    def to_surreal(self) -> str:
        """Convert to SurrealQL syntax."""
        # Import here to avoid circular imports at module level
        from .node import Node

        target_name = self._get_target_name()

        # Build the basic traversal with optional WHERE clause
        where_clause = f"[WHERE {self.where_condition.to_surreal()} ]" if self.where_condition else ""

        if self.direction == Direction.BACKWARD:
            result = f"<-{target_name}{where_clause}"
        elif self.direction == Direction.FORWARD:
            result = f"->{target_name}{where_clause}"
        else:  # BIDIRECTIONAL
            result = f"<->{target_name}{where_clause}"

        # Add recursion if needed
        if self.recursion_depth > 1:
            result = f".{{{self.recursion_depth}}}({result})"

        # Check if target is a Node class to determine field selection
        is_node = False
        if isinstance(self.target, type):
            try:
                is_node = issubclass(self.target, Node)
            except:
                pass

        # Add field selection or default .* for nodes
        if self.select_fields:
            result += f".{self.select_fields}"
        elif is_node:
            result += ".*"

        return result

    def _get_target_name(self) -> str:
        """Get the name of the target table/edge."""
        if isinstance(self.target, type):
            return self.target.__name__.lower()
        return str(self.target)
