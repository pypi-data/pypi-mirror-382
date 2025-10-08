from enum import Enum
from typing import Dict, Any

from pydantic import UUID4, BaseModel, model_serializer, GetCoreSchemaHandler, ValidationError, ConfigDict
from pydantic_core import core_schema

type ObjectReference = UUID4
"""ObjectReference is an alias for UUID4, representing a unique object identifier."""


class BasePydanticEnum(Enum):
    """Base class for creating Pydantic-compatible enums with flexible member resolution.

    This class extends Python's Enum to provide seamless integration with Pydantic models.
    It allows enum members to be resolved from various input types including codes,
    enum members, member values, or dictionary representations.

    The enum members are expected to have a `code` attribute for string-based lookup
    and support Pydantic model validation for dictionary inputs.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, _source: Any, _handler: GetCoreSchemaHandler):
        """Define the Pydantic core schema for enum validation and serialization.

        This method configures how Pydantic should validate and serialize enum instances.
        It sets up flexible input validation that accepts multiple input formats and
        serializes enum members using their code attribute.

        Args:
            _source (Any): The source type being processed (unused)
            _handler (GetCoreSchemaHandler): Core schema handler from Pydantic (unused)

        Returns:
            core_schema: A Pydantic core schema that handles JSON and Python validation
            with custom serialization to the member's code attribute
        """
        # Get the member from the enum no matter what we have as input.
        # If we fail to find a matching member, it will fail.
        # It accepts: code, enum member and enum member value as input.
        get_member_schema = core_schema.no_info_plain_validator_function(cls._get_member)

        return core_schema.json_or_python_schema(
            json_schema=get_member_schema,
            python_schema=get_member_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda member: member.value.code),
        )

    @classmethod
    def _get_member(cls, input_value: Any):
        """Resolve an enum member from various input formats.

        This method provides flexible member resolution supporting multiple input types:
        - Direct enum member instances
        - Enum member values (the objects stored in enum members)
        - String codes matching the member's value.code attribute
        - Dictionary representations that can be validated as member values

        Args:
            input_value (Any): The input to resolve to an enum member. Can be:
                - An enum member instance
                - A member value object
                - A string code
                - A dictionary representation of a member value

        Returns:
            Enum member: The resolved enum member

        Raises:
            ValueError: If the input_value cannot be resolved to any enum member

        Note:
            Dictionary validation is performed for each member during iteration,
            which may impact performance for large enums. Consider implementing
            a _get_value_type class method in subclasses for optimization.
        """
        for member in cls:
            # If the input is already a member or is a member value, let's use it.
            if input_value == member or input_value == member.value:
                return member

            # If not, search for the member with input_value as code.
            if member.value.code == input_value:
                return member

            # Try to validate the input as a model, in case the user supplied a dict
            # representing a member. Validating during each loop is suboptimal,
            # improve this if you care about this feature.
            # Not easy since you can't know easily the type of you member values by
            # default. Forcing the child to implement a _get_value_type class method
            # would solve this.
            try:
                model = type(member.value).model_validate(input_value)
            except ValidationError:
                continue
            else:
                # Validated successfully and matches the current member.
                if member.value == model:
                    return member

        # Raise a ValueError if our search fails for Pydantic to create its proper
        # ValidationError.
        raise ValueError(f"Failed to convert {input_value} to a member of {cls}")


class Level(BaseModel):
    """A Pydantic model representing a hierarchical level with ordering capabilities.

    This class defines a level with a code, name, ordering value, and optional description.
    It provides comparison operators based on the ordering_value field, allowing levels
    to be sorted and compared in a meaningful hierarchy.

    Example:
        >>> level1 = Level(code="LOW", name="Low Priority", ordering_value=10)
        >>> level2 = Level(code="HIGH", name="High Priority", ordering_value=20)
        >>> level1 < level2
        True
        >>> str(level1)
        'Low Priority'
    """

    model_config: ConfigDict = ConfigDict(str_strip_whitespace=True, arbitrary_types_allowed=True, from_attributes=True)

    code: str
    name: str
    ordering_value: int
    description: str | None = None

    @model_serializer
    def ser_model(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def __le__(self, other: Any) -> bool:
        if isinstance(other, Level):
            return self.ordering_value <= other.ordering_value
        return False

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, Level):
            return self.ordering_value >= other.ordering_value
        return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Level):
            return self.ordering_value < other.ordering_value
        return False

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, Level):
            return self.ordering_value > other.ordering_value
        return False

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Level):
            return self.ordering_value == other.ordering_value and self.name == other.name
        return False


class TlpPapLevel(BasePydanticEnum):
    """Traffic Light Protocol (TLP) and Permissible Actions Protocol (PAP) classification levels.

    The TLP is a set of designations used to ensure that sensitive information is shared
    with the appropriate audience. PAP complements TLP by providing guidance on what
    actions can be taken with the information.

    Note:
        See `FIRST TLP Standard <https://www.first.org/tlp/>`_ for complete specification.

    Example:
        >>> level = TlpPapLevel.RED
        >>> print(level)
        RED
        >>> str(level) == "RED"
        True
    """

    RED = Level(name="RED", code="RED", ordering_value=40)
    """Highly sensitive information, restricted to specific recipients."""

    AMBER = Level(name="AMBER", code="AMBER", ordering_value=30)
    """Sensitive information, limited to a defined group."""

    GREEN = Level(name="GREEN", code="GREEN", ordering_value=20)
    """Information that can be shared within the community."""

    WHITE = Level(name="WHITE", code="WHITE", ordering_value=10)
    """Information that can be shared publicly."""

    @classmethod
    def by_name(cls, name: str) -> "TlpPapLevel":
        """Retrieve a TLP/PAP level enum member by its name.

        This method provides a convenient way to access enum members using their
        string names (e.g., "RED", "AMBER", "GREEN", "WHITE").

        Args:
            name (str): The name of the TLP/PAP level to retrieve. Must match
                       exactly one of the enum member names: "RED", "AMBER",
                       "GREEN", or "WHITE".

        Returns:
            Level: The Level object associated with the specified enum member

        Raises:
            AttributeError: If the provided name does not correspond to any
                           enum member

        Example:
            >>> level = TlpPapLevel.by_name("RED")
            >>> print(level.name)
            RED
            >>> print(level.value.ordering_value)
            40
        """
        return getattr(cls, name)

    def __str__(self):
        """Return the string representation of the TLP level.

        Returns:
            str: The TLP level value as a string
        """
        return self.value.name

    def __repr__(self):
        return self.name


class Singleton(type):
    """Metaclass implementation of the Singleton design pattern.

    This metaclass ensures that only one instance of a class can exist at any time.
    Subsequent instantiation attempts will return the existing instance rather than
    creating a new one.

    Note:
        The singleton instance is created lazily on first instantiation and persists
        for the lifetime of the Python process.

        Classes using this metaclass should be designed to handle reinitialization
        gracefully, as ``__init__`` may be called multiple times on the same instance.

    Example:
        >>> class Configuration(metaclass=Singleton):
        ...     def __init__(self, value=None):
        ...         if not hasattr(self, 'initialized'):
        ...             self.value = value
        ...             self.initialized = True
        ...
        >>> config1 = Configuration(value=42)
        >>> config2 = Configuration(value=99)
        >>> print(config1 is config2)  # Both variables point to the same instance
        True
        >>> print(config1.value)  # The value from first initialization
        42
    """

    _instances: Dict[type, type] = {}

    def __call__(cls, *args, **kwargs):
        """Control instance creation to ensure singleton behavior.

        Args:
            cls (type): The class being instantiated
            *args: Positional arguments for class initialization
            **kwargs: Keyword arguments for class initialization

        Returns:
            type: The singleton instance of the class

        Note:
            If an instance already exists, ``__init__`` will still be called with
            the provided arguments, but no new instance is created.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
