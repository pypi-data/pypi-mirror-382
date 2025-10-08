from datetime import datetime, UTC
from typing import Optional, Dict, Any, List, Union, get_args
from uuid import uuid4, UUID

from pydantic import Field, BaseModel, model_validator, ConfigDict
from pydantic.types import UUID4, PositiveInt

from colander_data_converter.base.common import (
    TlpPapLevel,
    ObjectReference,
    Singleton,
)
from colander_data_converter.base.models import CommonEntitySuperType, CommonEntitySuperTypes
from colander_data_converter.base.types.base import CommonEntityType


class ThreatrRepository(object, metaclass=Singleton):
    """Singleton repository for managing and storing Entity, Event, and EntityRelation objects.

    This class provides centralized storage and reference management for all model instances,
    supporting insertion, lookup, and reference resolution/unlinking. Uses the Singleton
    pattern to ensure a single global repository instance.

    Warning:
        As a singleton, this repository persists for the entire application lifecycle.
        Use the ``clear()`` method to reset state when needed.
    """

    entities: Dict[str, "Entity"]
    """Dictionary storing Entity objects by their string ID."""

    events: Dict[str, "Event"]
    """Dictionary storing Event objects by their string ID."""

    relations: Dict[str, "EntityRelation"]
    """Dictionary storing EntityRelation objects by their string ID."""

    def __init__(self):
        """Initializes the repository with empty dictionaries for events, entities, and relations.

        Note:
            Due to the Singleton pattern, this method is only called once per application run.
        """
        self.events = {}
        self.entities = {}
        self.relations = {}

    def clear(self):
        """Clears all stored entities, events, and relations from the repository.

        Caution:
            This operation cannot be undone and will remove all data from the repository.
        """
        self.events.clear()
        self.relations.clear()
        self.entities.clear()

    def __lshift__(self, other: Union["Entity", "Event", "EntityRelation"]) -> None:
        """Inserts an object into the appropriate repository dictionary using the left shift operator.

        This method overloads the ``<<`` operator to provide a convenient way to register
        Entity, Event, and EntityRelation objects in their respective dictionaries.
        The object's ID is used as the key, converted to string format for consistency.

        Args:
            other: The object to insert into the repository.
        """
        if isinstance(other, Entity):
            self.entities[str(other.id)] = other
        elif isinstance(other, EntityRelation):
            self.relations[str(other.id)] = other
        elif isinstance(other, Event):
            self.events[str(other.id)] = other

    def __rshift__(self, other: str | UUID4) -> Union["Entity", "Event", "EntityRelation", str, UUID4]:
        """Retrieves an object by its string or UUID identifier using the right shift operator.

        This method overloads the ``>>`` operator to provide a convenient way to lookup
        Entity, Event, and EntityRelation objects from their respective dictionaries.
        The method searches through entities, relations, and events in that order,
        returning the first match found.

        Args:
            other: The string or UUID identifier to look up in the repository.

        Returns:
            The found Entity, Event, or EntityRelation object, or the original
            identifier if no matching object is found.
        """
        _other = str(other)
        if _other in self.entities:
            return self.entities[_other]
        elif _other in self.relations:
            return self.relations[_other]
        elif _other in self.events:
            return self.events[_other]
        return other

    def unlink_references(self):
        """Unlinks all object references in relations and events by replacing them with UUIDs.

        This method calls ``unlink_references()`` on all stored relations and events to
        convert object references back to UUID references for serialization purposes.

        Note:
            This operation modifies the stored objects in-place.
        """
        for _, relation in self.relations.items():
            relation.unlink_references()
        for _, event in self.events.items():
            event.unlink_references()

    def resolve_references(self, strict=False):
        """Resolves all UUID references in relations and events to their corresponding objects.

        This method iterates through all stored relations and events in the repository,
        calling their respective ``resolve_references`` methods to convert UUID references
        back to actual object instances. This is typically used after deserialization
        to restore object relationships.

        Args:
            strict: If True, raises a ValueError when a UUID reference cannot be resolved.
                If False, unresolved references remain as UUIDs. Defaults to False.

        Raises:
            ValueError: If strict is True and any UUID reference cannot be resolved
                to an existing object in the repository.

        Important:
            Use ``strict=True`` to ensure data integrity when all references must be resolvable.
        """
        for _, relation in self.relations.items():
            relation.resolve_references(strict=strict)
        for _, event in self.events.items():
            event.resolve_references(strict=strict)


class ThreatrType(BaseModel):
    """Base model for Threatr objects, providing repository registration and reference management.

    This class ensures that all subclasses are automatically registered in the ThreatrRepository
    and provides methods to unlink and resolve object references for serialization and
    deserialization workflows.

    Important:
        All Threatr model classes must inherit from this base class to ensure proper
        repository integration and reference management.
    """

    model_config: ConfigDict = ConfigDict(str_strip_whitespace=True, arbitrary_types_allowed=True, from_attributes=True)

    def model_post_init(self, __context):
        """Executes post-initialization logic for the model.

        Ensures the repository registers the current subclass instance automatically
        after object creation.

        Args:
            __context: Additional context provided for post-initialization handling.

        Note:
            This method is called automatically by Pydantic after model initialization.
        """
        _ = ThreatrRepository()
        _ << self

    def _process_reference_fields(self, operation, strict=False):
        """Helper method to process reference fields for both unlinking and resolving operations.

        Args:
            operation: The operation to perform, either 'unlink' or 'resolve'.
            strict: If True, raises a ValueError when a UUID reference cannot be resolved.
                Only used for 'resolve' operation. Defaults to False.

        Raises:
            ValueError: If strict is True and a UUID reference cannot be resolved.
            AttributeError: If the class instance does not have the expected field or attribute.
        """
        for field, info in self.__class__.model_fields.items():
            annotation_args = get_args(info.annotation)
            if ObjectReference in annotation_args:
                ref = getattr(self, field)
                if operation == "unlink" and ref and type(ref) is not UUID:
                    setattr(self, field, ref.id)
                elif operation == "resolve" and type(ref) is UUID:
                    x = ThreatrRepository() >> ref
                    if strict and isinstance(x, UUID):
                        raise ValueError(f"Unable to resolve UUID reference {x}")
                    setattr(self, field, x)
            elif List[ObjectReference] in annotation_args:
                refs = getattr(self, field)
                new_refs = []
                _update = False
                for ref in refs:
                    if operation == "unlink" and ref and type(ref) is not UUID:
                        new_refs.append(ref.id)
                        _update = True
                    elif operation == "resolve" and type(ref) is UUID:
                        x = ThreatrRepository() >> ref
                        if strict and isinstance(x, UUID):
                            raise ValueError(f"Unable to resolve UUID reference {x}")
                        new_refs.append(x)
                        _update = True
                if _update:
                    setattr(self, field, new_refs)

    def unlink_references(self):
        """Unlinks object references by replacing them with their respective UUIDs.

        This method updates model fields annotated as ``ObjectReference`` or ``List[ObjectReference]``
        by replacing object references with their UUIDs for serialization purposes.

        Note:
            This operation modifies the object in-place and is typically used before serialization.

        Raises:
            AttributeError: If the class instance does not have the expected field or attribute.
        """
        self._process_reference_fields("unlink")

    def resolve_references(self, strict=False):
        """Resolves UUID references to their corresponding objects using the ThreatrRepository.

        Fields annotated with ``ObjectReference`` or ``List[ObjectReference]`` are processed
        to fetch and replace their UUID references with actual object instances.

        Args:
            strict: If True, raises a ValueError when a UUID reference cannot be resolved.
                If False, unresolved references remain as UUIDs. Defaults to False.

        Raises:
            ValueError: If strict is True and a UUID reference cannot be resolved.

        Important:
            Use ``strict=True`` to ensure all references are valid and resolvable.
        """
        self._process_reference_fields("resolve", strict)


class Entity(ThreatrType):
    """Represents an entity in the Threatr data model.

    Entities are the primary data objects in Threatr, representing observables,
    indicators, or other threat intelligence artifacts with associated metadata
    and classification levels.
    """

    id: UUID4 = Field(frozen=True, default_factory=lambda: uuid4())
    """The unique identifier for the entity."""

    created_at: datetime = Field(default=datetime.now(UTC), frozen=True)
    """The timestamp when the entity was created."""

    updated_at: datetime = Field(default=datetime.now(UTC))
    """The timestamp when the entity was last updated."""

    name: str = Field(..., min_length=1, max_length=512)
    """The name of the entity."""

    type: CommonEntityType
    """The specific type of the entity."""

    super_type: CommonEntitySuperType
    """The super type classification of the entity."""

    description: str | None = None
    """Optional description of the entity."""

    pap: TlpPapLevel = TlpPapLevel.WHITE
    """The PAP (Permissible Actions Protocol) level for the entity."""

    source_url: str | None = None
    """Optional source URL for the entity."""

    tlp: TlpPapLevel = TlpPapLevel.WHITE
    """The TLP (Traffic Light Protocol) level for the entity."""

    attributes: Optional[Dict[str, str | None]] = None
    """Dictionary of additional attributes."""


class EntityRelation(ThreatrType):
    """Represents a relation between two entities in the Threatr data model.

    EntityRelations define directed relationships between entities, supporting
    complex threat intelligence graphs and entity associations.
    """

    id: UUID4 = Field(frozen=True, default_factory=lambda: uuid4())
    """The unique identifier for the entity relation."""

    created_at: datetime = Field(default=datetime.now(UTC), frozen=True)
    """The timestamp when the entity relation was created."""

    updated_at: datetime = Field(default=datetime.now(UTC))
    """The timestamp when the entity relation was last updated."""

    name: str = Field(..., min_length=1, max_length=512)
    """The name of the entity relation."""

    description: str | None = None
    """Optional description of the relation."""

    attributes: Optional[Dict[str, str | None]] = None
    """Dictionary of additional attributes for the relation."""

    obj_from: Entity | ObjectReference = Field(...)
    """The source entity or reference in the relation."""

    obj_to: Entity | ObjectReference = Field(...)
    """The target entity or reference in the relation."""


class Event(ThreatrType):
    """Represents an event in the Threatr data model.

    Events capture temporal occurrences related to threat intelligence,
    tracking when specific activities or observations took place.
    """

    id: UUID4 = Field(frozen=True, default_factory=lambda: uuid4())
    """The unique identifier for the event."""

    created_at: datetime = Field(default=datetime.now(UTC), frozen=True)
    """The timestamp when the event was created."""

    updated_at: datetime = Field(default=datetime.now(UTC))
    """The timestamp when the event was last updated."""

    name: str = Field(..., min_length=1, max_length=512)
    """The name of the event."""

    description: str | None = None
    """Optional description of the event."""

    attributes: Optional[Dict[str, str | None]] = None
    """Dictionary of additional attributes for the event."""

    first_seen: datetime = datetime.now(UTC)
    """The timestamp when the event was first observed."""

    last_seen: datetime = datetime.now(UTC)
    """The timestamp when the event was last observed."""

    count: PositiveInt = 1
    """The number of times this event was observed."""

    type: CommonEntityType
    """The type of the event."""

    super_type: CommonEntitySuperType = CommonEntitySuperTypes.EVENT
    """The super type classification of the event."""

    involved_entity: Optional[Entity] | Optional[ObjectReference] = None
    """Optional entity or reference involved in this event."""

    @model_validator(mode="after")
    def _check_dates(self) -> Any:
        """Validates that the first_seen date is before the last_seen date.

        Returns:
            The validated model instance.

        Raises:
            ValueError: If first_seen is after last_seen.

        Important:
            This validation ensures temporal consistency for event data.
        """
        if self.first_seen > self.last_seen:
            raise ValueError("first_seen must be before last_seen")
        return self


class ThreatrFeed(ThreatrType):
    """Represents a feed of Threatr data, including entities, relations, and events.

    ThreatrFeed serves as a container for complete threat intelligence datasets,
    organizing related entities, their relationships, and associated events into
    a cohesive data structure.
    """

    root_entity: Entity
    """The root entity of the feed, corresponding to the primary requested entity."""

    entities: Optional[List[Entity]] = []
    """List of entity objects in the feed."""

    relations: Optional[List[EntityRelation]] = []
    """List of entity relation objects in the feed."""

    events: Optional[List[Event]] = []
    """List of event objects in the feed."""

    @staticmethod
    def load(
        raw_object: Dict[str, Union[Entity, Event, EntityRelation]],
        strict: bool = False,
    ) -> "ThreatrFeed":
        """Loads a ThreatrFeed from a raw object dictionary, resolving references.

        Args:
            raw_object: The raw data to validate and load.
            strict: If True, raises a ValueError when a UUID reference cannot be resolved.
                If False, unresolved references remain as UUIDs.

        Returns:
            The loaded and reference-resolved feed.

        Important:
            Use ``strict=True`` to ensure all references in the feed are valid and resolvable.
        """
        feed = ThreatrFeed.model_validate(raw_object)
        feed.resolve_references(strict=strict)
        return feed

    def resolve_references(self, strict=False):
        """Resolves references within entities, relations, and events.

        Iterates over each entity, relation, and event within the respective collections,
        calling their ``resolve_references`` method to update them with any referenced data.

        Args:
            strict: If True, raises a ValueError when a UUID reference cannot be resolved.
                If False, unresolved references remain as UUIDs.

        Note:
            This method synchronizes internal state with external dependencies after loading.
        """
        for entity in self.entities:
            entity.resolve_references(strict=strict)
        for event in self.events:
            event.resolve_references(strict=strict)
        for relation in self.relations:
            relation.resolve_references(strict=strict)

    def unlink_references(self) -> None:
        """Unlinks references from all entities, relations, and events within the feed.

        This method iterates through each entity, event, and relation, invoking their
        ``unlink_references()`` methods to replace object references with UUIDs.

        Note:
            This operation is useful for breaking dependencies or preparing data for serialization.
        """
        for entity in self.entities:
            entity.unlink_references()
        for event in self.events:
            event.unlink_references()
        for relation in self.relations:
            relation.unlink_references()
