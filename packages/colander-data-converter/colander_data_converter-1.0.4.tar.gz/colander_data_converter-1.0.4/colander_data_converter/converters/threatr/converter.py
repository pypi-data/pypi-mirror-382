from datetime import datetime, UTC
from typing import Union, List, get_args, cast, Optional
from uuid import uuid4, UUID

from pydantic import UUID4

from colander_data_converter.base.common import ObjectReference
from colander_data_converter.base.models import (
    ColanderFeed,
    EntityTypes,
    EntityRelation as ColanderEntityRelation,
    Entity as ColanderEntity,
    Event,
    CommonEntitySuperType,
    ColanderRepository,
    CommonEntitySuperTypes,
    Observable,
)
from colander_data_converter.base.types.base import CommonEntityType
from colander_data_converter.base.types.event import EventTypes
from colander_data_converter.base.utils import BaseModelMerger
from colander_data_converter.converters.threatr.mapping import ThreatrMapper
from colander_data_converter.converters.threatr.models import (
    ThreatrFeed,
    Entity as ThreatrEntity,
    Event as ThreatrEvent,
    EntityRelation as ThreatrEntityRelation,
)


class ColanderToThreatrMapper(ThreatrMapper):
    """
    Mapper for converting Colander data model to Threatr data model.

    This class handles the conversion of Colander feeds, entities, relations, and events
    to their corresponding Threatr equivalents. It processes reference fields and creates
    appropriate relationship mappings between entities.

    Note:
        The mapper uses the mapping configuration loaded from the parent ThreatrMapper
        class to determine appropriate field and relation name mappings.
    """

    def _get_relation_name_from_field(self, source_type: str, target_type: str, field_name: str) -> str:
        """
        Get the relation name for a field based on the mapping configuration.

        Args:
            source_type: The source entity type name
            target_type: The target entity type name
            field_name: The field name to map

        Returns:
            The mapped relation name or a default based on the field name

        Note:
            If no mapping is found in the configuration, returns a normalized
            version of the field name with underscores replaced by spaces.
        """
        assert source_type is not None
        assert target_type is not None
        assert field_name is not None

        relation_name = field_name.lower().replace("_", " ")
        for mapping in self.mapping_loader.mapping_data:
            if (
                mapping["source_type"] == source_type.lower()
                and mapping["target_type"] == target_type.lower()
                and field_name in mapping["fields"]
            ):
                relation_name = mapping["fields"][field_name]

        return relation_name

    def convert(self, colander_feed: ColanderFeed, root_entity: Union[str, UUID4, EntityTypes]) -> ThreatrFeed:
        """
        Convert a Colander data model to a Threatr data model.

        This method transforms a complete Colander feed including all entities, relations,
        and events into the equivalent Threatr representation. It handles reference field
        extraction and conversion to explicit relations.

        Args:
            colander_feed: The Colander feed to convert
            root_entity: The root entity ID, UUID, or entity object to use as the root

        Returns:
            ThreatrFeed: A ThreatrFeed object containing the converted data

        Raises:
            ValueError: If the root entity cannot be found or is invalid

        Important:
            The root entity must exist in the provided Colander feed. If a string ID
            is provided, it must be a valid UUID format.
        """
        # Get the root entity object if an ID was provided
        root_entity_obj = None
        if isinstance(root_entity, str):
            try:
                root_entity = UUID(root_entity, version=4)
            except Exception:
                raise ValueError(f"Invalid UUID {root_entity}")
        if isinstance(root_entity, UUID):
            root_entity_obj = colander_feed.entities.get(str(root_entity))
            if not root_entity_obj:
                raise ValueError(f"Root entity with ID {root_entity} not found in feed")
        else:
            root_entity_obj = root_entity

        # Convert the root entity to a Threatr entity
        threatr_root_entity = self._convert_entity(root_entity_obj)
        threatr_events = []

        # Convert all entities
        threatr_entities = [threatr_root_entity]
        for entity_id, entity in colander_feed.entities.items():
            # Skip the root entity as it's already included
            if str(entity.id) == str(root_entity_obj.id):
                continue
            threatr_entity = self._convert_entity(entity)
            if isinstance(threatr_entity, ThreatrEvent):
                threatr_events.append(threatr_entity)
            else:
                threatr_entities.append(threatr_entity)

        # Convert all relations
        threatr_relations = []
        for relation_id, relation in colander_feed.relations.items():
            threatr_relation = self._convert_relation(relation)
            threatr_relations.append(threatr_relation)

        # Convert reference fields to relations
        reference_relations = self._extract_reference_relations(colander_feed)
        threatr_relations.extend(reference_relations)

        # Create and return the Threatr feed
        return ThreatrFeed(
            root_entity=threatr_root_entity,
            entities=threatr_entities,
            relations=threatr_relations,
            events=threatr_events,
        )

    def _convert_entity(self, entity: ColanderEntity) -> Union[ThreatrEntity, ThreatrEvent]:
        """
        Convert a Colander entity to a Threatr entity or event.

        Args:
            entity: The Colander entity to convert

        Returns:
            A Threatr entity or event based on the input type

        Note:
            Events are detected by checking if the entity is an instance of the Event class
            and are converted to ThreatrEvent objects accordingly.
        """
        # Create a base entity with common fields
        model_class = ThreatrEntity
        if isinstance(entity, Event):
            model_class = ThreatrEvent
        threatr_entity = model_class(
            id=entity.id,
            created_at=getattr(entity, "created_at", datetime.now(UTC)),
            updated_at=getattr(entity, "updated_at", datetime.now(UTC)),
            name=entity.name,
            type=cast(CommonEntityType, entity.type),
            super_type=cast(CommonEntitySuperType, entity.super_type),
            attributes={},
        )

        bm = BaseModelMerger()
        bm.merge(entity, threatr_entity)

        return threatr_entity

    def _convert_relation(self, relation: ColanderEntityRelation) -> ThreatrEntityRelation:
        """
        Convert a Colander entity relation to a Threatr entity relation.

        Args:
            relation: The Colander entity relation to convert

        Returns:
            A Threatr entity relation

        Note:
            Object references are normalized to UUIDs during conversion to maintain
            consistency in the Threatr model.
        """
        # Create a base relation with common fields
        threatr_relation = ThreatrEntityRelation(
            id=relation.id,
            created_at=getattr(relation, "created_at", datetime.now(UTC)),
            updated_at=getattr(relation, "updated_at", datetime.now(UTC)),
            name=relation.name,
            description=getattr(relation, "description", None),
            obj_from=relation.obj_from if isinstance(relation.obj_from, UUID) else relation.obj_from.id,
            obj_to=relation.obj_to if isinstance(relation.obj_to, UUID) else relation.obj_to.id,
            attributes={},
        )

        bm = BaseModelMerger()
        bm.merge(relation, threatr_relation)

        return threatr_relation

    def _extract_reference_relations(self, colander_feed: ColanderFeed) -> List[ThreatrEntityRelation]:
        """
        Extract reference fields from Colander entities and convert them to Threatr relations.

        This method processes all entities in the feed to identify ObjectReference fields
        and converts them into explicit EntityRelation objects in the Threatr model.

        Args:
            colander_feed: The Colander feed containing entities

        Returns:
            A list of Threatr entity relations extracted from reference fields

        Note:
            Both single ObjectReference fields and List[ObjectReference] fields are processed
            to create appropriate relationship mappings.
        """
        relations = []

        for entity_id, entity in colander_feed.entities.items():
            entity_type_name = type(entity).__name__.lower()

            for field_name, field_info in entity.__class__.model_fields.items():
                field_annotation = get_args(field_info.annotation)
                field_value = getattr(entity, field_name, None)

                if not field_value or not field_annotation:
                    continue

                # Handle single ObjectReference
                if ObjectReference in field_annotation:
                    relation = self._create_relation_from_reference(
                        entity, field_name, field_value, entity_type_name, colander_feed, is_list=False
                    )
                    if relation:
                        relations.append(relation)

                # Handle List[ObjectReference]
                elif List[ObjectReference] in field_annotation:
                    for object_reference in field_value:
                        relation = self._create_relation_from_reference(
                            entity, field_name, object_reference, entity_type_name, colander_feed, is_list=True
                        )
                        if relation:
                            relations.append(relation)

        return relations

    def _create_relation_from_reference(
        self, entity, field_name, reference_value, entity_type_name, colander_feed, is_list=False
    ):
        """
        Helper method to create a relation from a reference field.

        Args:
            entity: The source entity containing the reference
            field_name: The name of the reference field
            reference_value: The reference value (UUID or object)
            entity_type_name: The source entity type name
            colander_feed: The feed containing target entities
            is_list: Whether the reference comes from a list field. Defaults to False.

        Returns:
            A new ThreatrEntityRelation or None if target not found
        """
        target_id = reference_value if isinstance(reference_value, UUID) else reference_value.id
        target_entity = colander_feed.entities.get(str(target_id))

        if not target_entity:
            return None

        target_entity_type_name = type(target_entity).__name__.lower()

        # Get relation name based on whether it's a list or single reference
        if is_list:
            relation_name = self._get_relation_name_from_field(entity_type_name, target_entity_type_name, field_name)
        else:
            relation_name = field_name.replace("_", " ")

        return ThreatrEntityRelation(
            id=uuid4(),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            name=relation_name,
            description=f"Relation extracted from {entity_type_name}.{field_name} reference to {target_entity_type_name}",
            obj_from=entity.id,
            obj_to=target_entity.id,
            attributes={},
        )


class ThreatrToColanderMapper(ThreatrMapper):
    """
    Mapper for converting Threatr data model to Colander data model.

    This class handles the conversion of Threatr feeds, entities, events, and relations
    to their corresponding Colander equivalents. It processes explicit relations and
    attempts to convert them back to reference fields where appropriate.

    Important:
        This mapper maintains state during conversion, storing the input ThreatrFeed
        and building the output ColanderFeed incrementally.

    Attributes:
        threatr_feed: The input Threatr feed being converted
        colander_feed: The output Colander feed being built
    """

    def __init__(self):
        """
        Initialize the mapper with empty feed containers.

        Note:
            The mapper creates a new ColanderFeed instance for each conversion process.
        """
        super().__init__()
        self.threatr_feed: Optional[ThreatrFeed] = None
        self.colander_feed: ColanderFeed = ColanderFeed()

    def _get_field_from_relation_name(self, source_type: str, target_type: str, relation_name: str) -> Optional[str]:
        """
        Get the field name for a relation based on the mapping configuration.

        Args:
            source_type: The source entity type name
            target_type: The target entity type name
            relation_name: The relation name to reverse-map

        Returns:
            The corresponding field name or None if no mapping found

        Note:
            This method performs reverse lookup in the mapping configuration
            to find field names that correspond to relation names.
        """
        assert source_type is not None
        assert target_type is not None
        assert relation_name is not None
        relation_name = relation_name.lower().replace("_", " ")
        for mapping in self.mapping_loader.mapping_data:
            if mapping["source_type"] == source_type.lower() and mapping["target_type"] == target_type.lower():
                for fn, rn in mapping["fields"].items():
                    if rn == relation_name:
                        return fn
        return None

    def _create_immutable_relation(self, threatr_relation: ThreatrEntityRelation) -> bool:
        """
        Attempt to convert a Threatr relation back to a reference field.

        This method tries to convert explicit relations back into reference fields
        on the source entity, which is the preferred representation in the Colander model.

        Args:
            threatr_relation: The Threatr relation to convert

        Returns:
            True if the relation was successfully converted to a reference field

        Important:
            Only relations that map to known reference fields can be converted.
            Other relations remain as explicit EntityRelation objects.
        """
        relation_name = threatr_relation.name
        source_entity_id: UUID4 = (
            threatr_relation.obj_from if isinstance(threatr_relation.obj_from, UUID) else threatr_relation.obj_from.id
        )
        target_entity_id: UUID4 = (
            threatr_relation.obj_to if isinstance(threatr_relation.obj_to, UUID) else threatr_relation.obj_to.id
        )

        source_entity = ColanderRepository() >> source_entity_id
        target_entity = ColanderRepository() >> target_entity_id

        # Ensure both source and target entities are valid Colander entities
        if not isinstance(source_entity, ColanderEntity) or not isinstance(target_entity, ColanderEntity):
            return False

        if (
            field_name := self._get_field_from_relation_name(
                source_entity.super_type.short_name, target_entity.super_type.short_name, relation_name
            )
        ) is not None and field_name in source_entity.__class__.model_fields.keys():
            setattr(source_entity, field_name, target_entity)
            return True

        return False

    def _convert_relation(self, relation: ThreatrEntityRelation) -> Optional[ColanderEntityRelation]:
        """
        Convert a Threatr entity relation to a Colander entity relation.

        Args:
            relation: The Threatr entity relation to convert

        Returns:
            A Colander entity relation or None if conversion fails

        Raises:
            AssertionError: If relation or its object references are None

        Note:
            This method checks if the relation has already been converted to avoid
            duplicate processing.
        """
        assert relation is not None
        assert relation.obj_from is not None
        assert relation.obj_to is not None

        colander_relation: ColanderEntityRelation = ColanderRepository() >> relation.id
        if isinstance(colander_relation, ColanderEntityRelation):
            return colander_relation

        obj_from = ColanderRepository() >> relation.obj_from.id
        obj_to = ColanderRepository() >> relation.obj_to.id
        if obj_from and obj_to:
            colander_relation = ColanderEntityRelation(
                id=relation.id,
                name=relation.name,
                created_at=relation.created_at,
                updated_at=relation.updated_at,
                obj_from=obj_from,
                obj_to=obj_to,
            )
            bm = BaseModelMerger()
            bm.merge(relation, colander_relation)
            return colander_relation

        return None

    def _convert_entity(self, entity: ThreatrEntity) -> Optional[EntityTypes]:
        """
        Convert a Threatr entity to a Colander entity.

        This method determines the appropriate Colander entity type based on the
        Threatr entity's super_type and type, then creates the corresponding instance.

        Args:
            entity: The Threatr entity to convert

        Returns:
            A Colander entity or None if conversion is not supported

        Raises:
            AssertionError: If entity is None or not a ThreatrEntity instance

        Note:
            Entities that have already been processed are returned from the repository
            without re-conversion to maintain object identity.
        """
        assert entity is not None
        assert isinstance(entity, ThreatrEntity)

        # The entity has already been processed
        if (colander_entity := ColanderRepository() >> entity.id) is not None and isinstance(
            colander_entity, ColanderEntity
        ):
            return colander_entity

        # The super type is not supported
        if (super_type := CommonEntitySuperTypes.by_short_name(short_name=entity.super_type.short_name)) is None:
            return None

        # The entity type is not supported
        if (sub_type := super_type.type_by_short_name(entity.type.short_name)) is None:
            return None

        colander_entity = super_type.model_class(
            id=entity.id,
            name=entity.name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            type=sub_type,
        )
        bm = BaseModelMerger()
        bm.merge(entity, colander_entity, ignored_fields=["super_type"])
        return colander_entity

    def _convert_event(self, event: ThreatrEvent) -> Event:
        """
        Convert a Threatr event to a Colander event.

        Args:
            event: The Threatr event to convert

        Returns:
            A Colander event

        Raises:
            AssertionError: If event is None or not a ThreatrEvent instance

        Note:
            Events that have already been processed are returned from the repository
            without re-conversion. Involved entities are automatically linked if they
            are Observable instances.
        """
        assert event is not None
        assert isinstance(event, ThreatrEvent)

        # The event has already been processed
        if (colander_event := ColanderRepository() >> event.id) is not None and isinstance(colander_event, Event):
            return colander_event

        sub_type = EventTypes.by_short_name(event.type.short_name)

        colander_event = Event(
            id=event.id,
            name=event.name,
            created_at=event.created_at,
            updated_at=event.updated_at,
            first_seen=event.first_seen,
            last_seen=event.last_seen,
            count=event.count,
            type=sub_type,
        )

        if (involved_entity := event.involved_entity) is not None:
            involved_entity = ColanderRepository() >> involved_entity.id
            if isinstance(involved_entity, Observable):
                colander_event.involved_observables.append(involved_entity)

        bm = BaseModelMerger()
        bm.merge(event, colander_event, ignored_fields=["involved_entity", "super_type"])
        return colander_event

    def convert(self, threatr_feed: ThreatrFeed) -> ColanderFeed:
        """
        Convert a Threatr data model to a Colander data model.

        This method performs a complete conversion of a ThreatrFeed to a ColanderFeed,
        handling entities, events, and relations. It attempts to convert explicit
        relations back to reference fields where possible.

        Args:
            threatr_feed: The Threatr feed to convert

        Returns:
            A ColanderFeed object containing the converted data

        Raises:
            AssertionError: If threatr_feed is None or not a ThreatrFeed instance

        Important:
            The method resolves all references in the input feed before processing
            to ensure consistent object relationships.
        """
        assert threatr_feed is not None
        assert isinstance(threatr_feed, ThreatrFeed)
        self.threatr_feed = threatr_feed
        self.threatr_feed.resolve_references()
        self.colander_feed.description = "Feed automatically generated from a Threatr feed."

        if (root_entity := threatr_feed.root_entity) is not None:
            if (colander_entity := self._convert_entity(root_entity)) is not None:
                self.colander_feed.entities[str(root_entity.id)] = colander_entity

        for entity in threatr_feed.entities or []:
            if (colander_entity := self._convert_entity(entity)) is not None:
                self.colander_feed.entities[str(entity.id)] = colander_entity

        for event in threatr_feed.events or []:
            if (colander_event := self._convert_event(event)) is not None:
                self.colander_feed.entities[str(event.id)] = colander_event

        for relation in threatr_feed.relations or []:
            if not self._create_immutable_relation(relation):
                if (colander_relation := self._convert_relation(relation)) is not None:
                    self.colander_feed.relations[str(relation.id)] = colander_relation

        return self.colander_feed


class ThreatrConverter:
    """
    Converter for Threatr data to Colander data and vice versa.
    Uses the mapping file to convert between formats.
    """

    @staticmethod
    def threatr_to_colander(threatr_feed: ThreatrFeed) -> ColanderFeed:
        """
        Converts Threatr data to Colander data using the mapping file.

        Args:
            threatr_feed: The Threatr data to convert.

        Returns:
            The converted Colander data.
        """
        mapper = ThreatrToColanderMapper()
        return mapper.convert(threatr_feed)

    @staticmethod
    def colander_to_threatr(colander_feed: ColanderFeed, root_entity: Union[str, UUID4, EntityTypes]) -> ThreatrFeed:
        """
        Converts Colander data to Threatr data using the mapping file.

        Args:
            colander_feed: The Colander data to convert.
            root_entity: The root entity ID, UUID, or entity object to use as the root

        Returns:
            The converted Threatr data.
        """
        mapper = ColanderToThreatrMapper()
        colander_feed.resolve_references()
        return mapper.convert(colander_feed, root_entity)
