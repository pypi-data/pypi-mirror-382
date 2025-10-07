from abc import ABC, abstractmethod
from pydantic_core import CoreSchema
from pydantic_core import core_schema
from typing import Generic, TypeVar, Any
from pydantic import GetCoreSchemaHandler


class Tokenizer(ABC):
    """
    Abstract base class for defining text tokenizers for full-text search.

    Tokenizers define how text fields are analyzed and indexed for search
    operations in SurrealDB. Subclasses should implement the define() method
    to return the SurrealQL DEFINE ANALYZER statement.

    Attributes:
        name: The name of the tokenizer/analyzer in SurrealDB
    """
    name: str

    @classmethod
    @abstractmethod
    def define(cls) -> str:
        """
        Generate the SurrealQL definition for this tokenizer.

        Returns:
            str: The DEFINE ANALYZER statement for SurrealDB
        """
        pass


class FrenchTokenizer(Tokenizer):
    """
    Tokenizer for French text with proper handling of elisions and stemming.

    This tokenizer:
    - Removes French elisions (l', d', qu', etc.)
    - Applies lowercase transformation
    - Removes accents (ASCII filter)
    - Applies French stemming using the Snowball algorithm

    Example:
        >>> class Article(Node):
        ...     title: Text[FrenchTokenizer]
        ...     content: Text[FrenchTokenizer]
    """
    name = "french_analyzer"

    @classmethod
    def define(cls) -> str:
        """
        Generate the French analyzer definition for SurrealDB.

        Returns:
            str: Complete analyzer definition including elision function
        """
    # -- 1) Function to remove French elisions like l', d', qu', lorsqu', jusqu', etc.
	# -- Remove the leading elided article + apostrophe (case-insensitive)
	# -- Note: the regex uses an inline (?i) flag for case-insensitive matching.
	# -- Adjust the list if you want more/less tokens to be elided.
        function = """
DEFINE FUNCTION fn::french_elide($input: string) -> string {
    string::replace(
        $input,
        /(?i)\b(?:l|m|t|qu|n|s|j|d|c|jusqu|quoiqu|lorsqu|puisqu)\'/,
        ''
    );
};
        """

    #    -- 2) Analyzer that runs the function first, tokenizes, lowercases, removes accents, and stems (Snowball French)
    #    -- We use class + punct tokenizers to approximate ICU tokenization for general unicode-aware splitting.
        analyzer = f"""
DEFINE ANALYZER {cls.name}
    FUNCTION fn::french_elide
    TOKENIZERS class, punct
    FILTERS lowercase, ascii, snowball(french);
        """
        return function + analyzer


T = TypeVar("T", bound = Tokenizer)

class Text(str, Generic[T]):
    """
    A string type that enables full-text search indexing in SurrealDB.

    Text fields are automatically indexed for full-text search using the
    specified tokenizer. The tokenizer defines how the text is analyzed,
    including language-specific processing like stemming and elision removal.

    Type Parameters:
        T: A Tokenizer subclass that defines the text analysis strategy

    Example:
        >>> from tapestry import Node, Text
        >>> from tapestry.tokenizer import FrenchTokenizer
        >>>
        >>> class Article(Node):
        ...     title: Text[FrenchTokenizer]  # Indexed for French search
        ...     content: Text[FrenchTokenizer]
        ...     summary: str  # Regular string, not indexed
        ...
        >>> # Search using full-text search operator @
        >>> articles = await Q(Article).where(
        ...     Article.title @ "politique"
        ... ).execute(db)

    Notes:
        - Inherits from str, so can be used wherever strings are expected
        - Automatically creates search indexes in SurrealDB
        - Supports language-specific text processing
        - Use the @ operator in queries for full-text search
        - If no tokenizer is specified, defaults to FrenchTokenizer
    """
    # todo : find a way to make type checkers understand we can assign str to Text

    def __class_getitem__(cls, key):
        """
        Parameterize the Text type with a specific tokenizer.

        Args:
            key: Should be a Tokenizer subclass

        Returns:
            The Text class (for type checking purposes)

        Raises:
            TypeError: If key is not a Tokenizer subclass
        """
        if not (isinstance(key, type) and issubclass(key, Tokenizer)):
            raise TypeError(f"Text should be parametrized by a Tokenizer, not {key}")
        return cls # not sure I should return this

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """
        Generate Pydantic core schema for Text fields.

        This method tells Pydantic that Text fields should be treated as
        strings for validation purposes, while maintaining the Text type
        for ORM functionality.

        Args:
            source_type: The source type being processed
            handler: Pydantic's schema generation handler

        Returns:
            CoreSchema: A string schema for Pydantic validation
        """
        return core_schema.str_schema()
