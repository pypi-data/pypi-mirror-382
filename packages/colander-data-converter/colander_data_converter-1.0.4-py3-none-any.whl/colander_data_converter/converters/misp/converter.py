from typing import Optional, Union, List, Tuple

from pymisp import AbstractMISP, MISPTag, MISPObject, MISPAttribute, MISPEvent, MISPFeed

from colander_data_converter.base.common import TlpPapLevel
from colander_data_converter.base.models import (
    EntityTypes,
    Case,
    ColanderFeed,
    EntityRelation,
    ColanderRepository,
    Entity,
)
from colander_data_converter.converters.misp.models import Mapping, EntityTypeMapping, TagStub
from colander_data_converter.converters.misp.utils import get_attribute_by_name
from colander_data_converter.converters.stix2.utils import get_nested_value


class MISPMapper:
    """
    Base mapper class for MISP conversions.

    Provides common functionality for mapping Colander data structures to MISP objects.
    """

    def __init__(self):
        self.mapping = Mapping()
        ColanderRepository().clear()

    @staticmethod
    def tlp_level_to_tag(tlp_level: TlpPapLevel) -> MISPTag:
        """
        Convert a Colander TLP (Traffic Light Protocol) level to a MISP tag.

        Args:
            tlp_level: The TLP level to convert

        Returns:
            A MISP tag object with the TLP level name
        """
        t = MISPTag()
        t.name = tlp_level.name
        return t


class ColanderToMISPMapper(MISPMapper):
    """
    Mapper class for converting Colander objects to MISP format.

    Handles the conversion of various Colander entity types (threats, actors, events,
    artifacts, etc.) to their corresponding MISP object representations using
    predefined mapping configurations.
    """

    def convert_colander_object(self, colander_object: EntityTypes) -> Optional[Union[AbstractMISP, TagStub]]:
        """
        Convert a Colander object to its corresponding MISP representation.

        This method performs the core conversion logic by:

        1. Looking up the appropriate mapping for the Colander object type
        2. Creating the corresponding MISP object (Attribute or Object)
        3. Mapping fields, literals, and attributes from Colander to MISP format

        Args:
            colander_object: The Colander object to convert

        Returns:
            The converted MISP object, or None if no mapping exists
        """
        # Get the mapping configuration for this Colander object type
        entity_type_mapping: EntityTypeMapping = self.mapping.get_mapping_to_misp(
            colander_object.get_super_type(), colander_object.type
        )

        if entity_type_mapping is None:
            return None

        # Determine the MISP model class and type to create
        misp_model, misp_type = entity_type_mapping.get_misp_model_class()

        # Create the appropriate MISP object based on the model type
        if issubclass(misp_model, MISPAttribute):
            misp_object: MISPAttribute = misp_model(strict=True)
            misp_object.type = misp_type
        elif issubclass(misp_model, MISPObject):
            misp_object: MISPObject = misp_model(name=misp_type, strict=True)
        elif issubclass(misp_model, MISPTag):
            tag_pattern = entity_type_mapping.colander_misp_mapping.get("literals", {}).get("name")
            return TagStub(tag_pattern.format(value=colander_object.name))
        else:
            return None

        # Set common MISP object properties
        # ToDo: add tag for TLP
        misp_object.uuid = str(colander_object.id)
        misp_object.first_seen = colander_object.created_at
        misp_object.last_seen = colander_object.updated_at

        # Convert Colander object to dictionary for nested field access
        colander_object_dict = colander_object.model_dump(mode="json")

        # Map direct field mappings from Colander to MISP object properties
        for source_field, target_field in entity_type_mapping.get_colander_misp_field_mapping():
            value = getattr(colander_object, source_field, None)
            if value is not None:
                setattr(misp_object, target_field, value)

        # Set constant/literal values on the MISP object
        for target_field, value in entity_type_mapping.get_colander_misp_literals_mapping():
            if target_field in ["category", "comment"]:
                setattr(misp_object, target_field, value)
            else:
                misp_object.add_attribute(target_field, value=value)

        # Map Colander fields to MISP object attributes
        for source_field, target_field in entity_type_mapping.get_colander_misp_attributes_mapping():
            if "." in source_field:
                # Handle nested field access using dot notation
                value = get_nested_value(colander_object_dict, source_field)
                if value is not None:
                    misp_object.add_attribute(target_field, value=value)
            else:
                # Handle direct field access
                value = getattr(colander_object, source_field, None)
                if value is not None:
                    misp_object.add_attribute(target_field, value=value)

        return misp_object

    @staticmethod
    def get_element_from_event(
        event: MISPEvent, uuid: str, types: List[str]
    ) -> Tuple[Optional[Union[MISPObject, MISPAttribute]], Optional[str]]:
        """
        Retrieve an element (object or attribute) from a MISP event by UUID and type.

        Args:
            event: The MISP event to search within.
            uuid: The UUID of the element to find.
            types: List of types to search for ("object", "attribute").

        Returns:
            The found element and its type as a string ("Object" or "Attribute"), or (None, None) if not found.
        """
        if "object" in types:
            for obj in event.objects:
                if hasattr(obj, "uuid") and obj.uuid == uuid:
                    return obj, "Object"
        if "attribute" in types:
            for obj in event.attributes:
                if hasattr(obj, "uuid") and obj.uuid == uuid:
                    return obj, "Attribute"
        return None, None

    def convert_immutable_relations(self, event: MISPEvent, colander_object: EntityTypes):
        """
        Create relationships in a MISP event based on the Colander object's immutable relations.

        This method processes each immutable relation defined in the Colander object, determines the appropriate
        mapping and direction, and adds the corresponding relationship or tag to the MISP event.

        Args:
            event: The MISP event to which relationships or tags will be added.
            colander_object: The Colander object containing immutable relations.

        Note:
            - If the relation mapping specifies 'use_tag', a tag is added to the relevant MISP attribute.
            - Otherwise, a relationship is created between MISP objects or attributes as defined by the mapping.
        """
        super_type = colander_object.super_type
        # Create relationships based on immutable relations
        for _, relation in colander_object.get_immutable_relations().items():
            reference_name = relation.name
            relation_mapping = self.mapping.get_relation_mapping_to_misp(super_type, reference_name)

            if not relation_mapping:
                continue

            reverse = relation_mapping.get("reverse", False)
            source_id = str(relation.obj_from.id) if not reverse else str(relation.obj_to.id)
            target_id = str(relation.obj_to.id) if not reverse else str(relation.obj_from.id)
            relation_name = relation_mapping.get("name", reference_name.replace("_", "-"))

            # Tags only on MISPAttribute or MISPEvent
            if relation_mapping.get("use_tag", False):
                source_object, _ = self.get_element_from_event(event, source_id, types=["attribute"])
                if reverse:
                    tag = self.convert_colander_object(relation.obj_from)
                else:
                    tag = self.convert_colander_object(relation.obj_to)
                if source_object and isinstance(tag, TagStub):
                    event.add_attribute_tag(tag, source_id)
            # Regular immutable relation between a MISPObject and another MISPObject or MISPAttribute
            else:
                source_object, _ = self.get_element_from_event(event, source_id, types=["object"])
                target_object, type_name = self.get_element_from_event(event, target_id, types=["object", "attribute"])
                if source_object and target_object:
                    source_object.add_relationship(type_name, target_id, relation_name)

    def convert_relations(self, event: MISPEvent, colander_relations: List[EntityRelation]):
        """
        Create relationships in a MISP event based on a list of Colander relations.

        This method finds the corresponding MISP objects or attributes for each relation and
        adds the relationship to the source object.

        Args:
            event: The MISP event to which relationships will be added.
            colander_relations: List of Colander relations to convert.
        """
        for relation in colander_relations:
            source_id = str(relation.obj_from.id)
            target_id = str(relation.obj_to.id)
            source_object, _ = self.get_element_from_event(event, source_id, types=["object"])
            target_object, type_name = self.get_element_from_event(event, target_id, types=["object", "attribute"])
            if source_object and target_object:
                source_object.add_relationship(type_name, target_id, relation.name)

    def convert_case(self, case: Case, feed: ColanderFeed) -> Tuple[Optional[MISPEvent], List[EntityTypes]]:
        """
        Convert a Colander Case and its associated ColanderFeed into a MISPEvent.

        This method performs the following steps:

        1. Initializes a new MISPEvent using the case information.
        2. Iterates over all entities in the feed, converting each to a MISP object or attribute.

           - Entities that cannot be converted are added to the skipped list.
           - MISPAttributes are added as attributes to the event.
           - MISPObjects are added as objects to the event.
        3. Processes immutable relations for each entity, adding corresponding relationships or tags to the event.
        4. Processes regular (non-immutable) relations for each entity, adding relationships to the event.
        5. Returns the constructed MISPEvent and a list of skipped entities.

        Args:
            case: The Colander case to convert.
            feed: The feed containing entities and relations to convert.

        Returns:
            The resulting MISPEvent and a list of entities that were skipped during conversion.
        """
        skipped = []
        misp_event = MISPEvent()
        misp_event.uuid = str(case.id)
        misp_event.info = case.description
        misp_event.date = case.created_at
        for entity in feed.entities.values():
            if entity.case != case:
                continue
            misp_object = self.convert_colander_object(entity)
            if not misp_object:
                skipped.append(entity)
                continue
            if isinstance(misp_object, MISPAttribute):
                misp_event.add_attribute(**misp_object.to_dict())
            elif isinstance(misp_object, MISPObject):
                misp_event.add_object(misp_object)

        # Immutable relations
        for entity in feed.entities.values():
            self.convert_immutable_relations(misp_event, entity)

        # Regular relations
        for entity in feed.entities.values():
            self.convert_relations(misp_event, list(feed.get_outgoing_relations(entity).values()))

        return misp_event, skipped


class MISPToColanderMapper(MISPMapper):
    def convert_misp_event(self, event: MISPEvent) -> Tuple[Case, ColanderFeed]:
        """
        Convert a MISPEvent into a Colander case and feed.

        This method performs the following steps:

        1. Creates a new Case instance using the event information.
        2. Initializes a ColanderFeed and adds the case to it.
        3. Converts all MISP objects in the event to Colander entities and adds them to the feed.
        4. Converts all MISP attributes in the event to Colander entities and adds them to the feed.
        5. Converts all relations in the event to Colander relations and adds them to the feed.
        6. Returns the constructed Case and ColanderFeed.

        Args:
            event: The MISP event to convert.

        Returns:
            The resulting Case and Feed.
        """
        case = Case(id=event.uuid, name=event.info, description=f"Loaded from MISP event [{event.uuid}]")
        feed = ColanderFeed(cases={f"{case.id}": case})
        for entity in self._convert_objects(event):
            entity.case = case
            feed.entities[str(entity.id)] = entity
        for entity in self._convert_attributes(event):
            entity.case = case
            feed.entities[str(entity.id)] = entity
        for relation in self._convert_relations(event):
            relation.case = case
            feed.relations[str(relation.id)] = relation
        return case, feed

    def _convert_relations(self, event: MISPEvent) -> List[EntityRelation]:
        relations = []
        for misp_object in event.objects + event.attributes:
            source_object = ColanderRepository() >> misp_object.uuid
            if not isinstance(source_object, Entity):
                continue
            for misp_relation in misp_object.relationships or []:
                relation_name = misp_relation.relationship_type
                target_object = ColanderRepository() >> misp_relation.related_object_uuid
                if not isinstance(target_object, Entity):
                    continue
                if relation_name:
                    relations.append(
                        EntityRelation(
                            id=misp_relation.uuid, name=relation_name, obj_from=source_object, obj_to=target_object
                        )
                    )
        return relations

    def _prepare_colander_entity(
        self, misp_object: Union[MISPObject, MISPAttribute], entity_mapping: EntityTypeMapping, entity_name: str
    ) -> Optional[EntityTypes]:
        """
        Prepare and populate a Colander entity from a MISP object using the provided mapping and entity name.

        Args:
            misp_object: The MISP object or attribute to convert.
            entity_mapping: The mapping configuration for the entity type.
            entity_name: The name to assign to the Colander entity.

        Returns:
            The populated Colander entity, or None if creation fails.
        """
        # Get the Colander model class and entity type from the mapping
        colander_model_class = entity_mapping.colander_super_type.model_class
        colander_entity_type = entity_mapping.colander_entity_type

        # Instantiate the Colander entity with id, type, and name
        colander_entity = colander_model_class(id=misp_object.uuid, type=colander_entity_type, name=entity_name)

        # Map MISP object properties to Colander entity attributes based on the mapping
        for colander_attribute_name, misp_property_name in entity_mapping.colander_misp_mapping.items():
            # Skip mapping for literals, name, and misp_attributes keys
            if colander_attribute_name in ["literals", "name", "misp_attributes"]:
                continue
            misp_value = getattr(misp_object, misp_property_name, None)
            setattr(colander_entity, colander_attribute_name, misp_value)

        return colander_entity

    def _convert_object(self, misp_object: MISPObject) -> Optional[EntityTypes]:
        """
        Convert a MISPObject to its corresponding Colander entity.

        This method uses the mapping configuration to extract the entity name and attributes
        from the MISPObject, then creates and populates a Colander entity instance.

        Args:
            misp_object: The MISP object to convert.

        Returns:
            The resulting Colander entity, or None if mapping or name is missing.
        """
        # Get the mapping for this MISP object
        entity_mapping = self.mapping.get_misp_object_mapping(misp_object)
        if not entity_mapping or not entity_mapping.colander_super_type:
            return None

        entity_name = None
        misp_property_for_name = entity_mapping.colander_misp_mapping.get("name", "")
        misp_attributes = entity_mapping.colander_misp_mapping.get("misp_attributes", {})
        misp_attribute_for_name = misp_attributes.get("name", "")

        # Try to extract the entity name from the MISP object property or attribute
        if misp_property_for_name:
            entity_name = getattr(misp_object, misp_property_for_name, None)
        elif misp_attribute_for_name:
            if (misp_attribute := get_attribute_by_name(misp_object, misp_attribute_for_name)) is not None:
                entity_name = misp_attribute.value

        if not entity_name:
            return None

        # Prepare the Colander entity using the mapping and extracted entity name
        colander_entity = self._prepare_colander_entity(misp_object, entity_mapping, entity_name)

        # Map MISP attributes to Colander entity fields
        for colander_attribute_name, misp_property_name in misp_attributes.items():
            # Skip literals, name, and nested fields
            if colander_attribute_name in ["literals", "name"] or "." in colander_attribute_name:
                continue
            if (misp_attribute := get_attribute_by_name(misp_object, misp_property_name)) is None:
                continue
            if hasattr(colander_entity, colander_attribute_name) and misp_attribute.value:
                setattr(colander_entity, colander_attribute_name, misp_attribute.value)

        # If the Colander entity has an 'attributes' dict, add any extra MISP attributes not mapped above
        if hasattr(colander_entity, "attributes"):
            if not colander_entity.attributes:
                colander_entity.attributes = {}
            for attribute in misp_object.attributes:
                if attribute.object_relation not in misp_attributes.values():
                    colander_entity.attributes[attribute.object_relation.replace("-", "_")] = str(attribute.value)

        return colander_entity

    def _convert_objects(self, misp_object: MISPEvent) -> List[EntityTypes]:
        entities: List[EntityTypes] = []
        for misp_object in misp_object.objects:
            colander_entity = self._convert_object(misp_object)
            if colander_entity:
                entities.append(colander_entity)
        return entities

    def _convert_attribute(self, misp_attribute: MISPAttribute) -> Optional[EntityTypes]:
        entity_mapping = self.mapping.get_misp_attribute_mapping(misp_attribute)
        if not entity_mapping or not entity_mapping.colander_super_type:
            return None
        misp_property_for_name = entity_mapping.colander_misp_mapping.get("name")
        entity_name = getattr(misp_attribute, misp_property_for_name)
        colander_entity = self._prepare_colander_entity(misp_attribute, entity_mapping, entity_name)
        return colander_entity

    def _convert_attributes(self, misp_event: MISPEvent) -> List[EntityTypes]:
        entities: List[EntityTypes] = []
        for misp_attribute in misp_event.attributes:
            colander_entity = self._convert_attribute(misp_attribute)
            if colander_entity:
                entities.append(colander_entity)
        return entities


class MISPConverter:
    """
    Converter for MISP data to Colander data and vice versa.
    Uses the mapping file to convert between formats.
    """

    @staticmethod
    def misp_to_colander(misp_feed: MISPFeed) -> Optional[List[ColanderFeed]]:
        """
        Convert a MISP feed to a list of Colander feeds. Each MISP event is converted to a separate Colander feed.

        Args:
            misp_feed: The MISP feed containing events to convert.

        Returns:
            A list of Colander feeds, or None if no events are found.
        """
        feeds: List[ColanderFeed] = []
        mapper = MISPToColanderMapper()
        if not misp_feed:
            return feeds
        events = misp_feed.get("response", None)
        if "response" not in misp_feed:
            events = [misp_feed]
        for event in events or []:
            misp_event = MISPEvent()
            misp_event.from_dict(**event)
            _, feed = mapper.convert_misp_event(misp_event)
            feed.resolve_references()
            feeds.append(feed)
        return feeds

    @staticmethod
    def colander_to_misp(colander_feed: ColanderFeed) -> Optional[List[MISPEvent]]:
        """
        Convert a Colander feed to a list of MISP events. Each Colander case is converted to a MISP event.

        Args:
            colander_feed: The Colander feed containing cases to convert.

        Returns:
            A list of MISP events, or None if no cases are found.
        """
        mapper = ColanderToMISPMapper()
        colander_feed.resolve_references()
        events: List[MISPEvent] = []
        for _, case in colander_feed.cases.items():
            misp_event, _ = mapper.convert_case(case, colander_feed)
            events.append(misp_event)
        return events
