from typing import Dict, Optional, Union, List, Type, Any
from uuid import uuid4

from colander_data_converter.base.models import (
    Actor,
    Device,
    Artifact,
    Observable,
    Threat,
    Event,
    DetectionRule,
    DataFragment,
    EntityRelation,
    ColanderFeed,
    ColanderRepository,
    CommonEntitySuperType,
    CommonEntitySuperTypes,
    EntityTypes,
    Entity,
)
from colander_data_converter.base.types.actor import *
from colander_data_converter.base.types.artifact import *
from colander_data_converter.base.types.device import *
from colander_data_converter.base.types.observable import *
from colander_data_converter.base.types.threat import *
from colander_data_converter.converters.stix2.mapping import Stix2MappingLoader
from colander_data_converter.converters.stix2.models import (
    Stix2ObjectBase,
    Stix2ObjectTypes,
    Stix2Bundle,
    Stix2Repository,
    Relationship,
)
from colander_data_converter.converters.stix2.utils import (
    extract_uuid_from_stix2_id,
    get_nested_value,
    set_nested_value,
    extract_stix2_pattern_name,
    extract_stix2_pattern_value,
)


class Stix2Mapper:
    """
    Base class for mapping between STIX2 and Colander data using the mapping file.
    """

    def __init__(self):
        """
        Initialize the mapper.
        """
        self.mapping_loader = Stix2MappingLoader()
        ColanderRepository().clear()


class Stix2ToColanderMapper(Stix2Mapper):
    """
    Maps STIX2 data to Colander data using the mapping file.
    """

    def convert(self, stix2_data: Dict[str, Any]) -> ColanderFeed:
        """
        Convert STIX2 data to Colander data.

        Args:
            stix2_data (Dict[str, Any]): The STIX2 data to convert.

        Returns:
            ColanderFeed: The converted Colander data.
        """
        repository = ColanderRepository()

        # Keep track of processed STIX2 object IDs to handle duplicates
        processed_ids: Dict[str, str] = {}

        # Process STIX2 objects
        for stix2_object in stix2_data.get("objects", []):
            stix2_id = stix2_object.get("id", "")
            stix2_type = stix2_object.get("type", "")

            # Skip if this ID has already been processed with a different type
            if stix2_id in processed_ids and processed_ids[stix2_id] != stix2_type:
                # Generate a new UUID for this object to avoid overwriting
                stix2_object = stix2_object.copy()
                stix2_object["id"] = f"{stix2_type}--{uuid4()}"

            colander_entity = self.convert_stix2_object(stix2_object)
            if colander_entity:
                repository << colander_entity
                processed_ids[stix2_id] = stix2_type

        # Handle object references
        for stix2_object in stix2_data.get("objects", []):
            stix2_id = stix2_object.get("id", "")
            if stix2_id not in processed_ids:
                continue
            stix2_type = stix2_object.get("type", "")
            if stix2_type == "relationship":
                continue
            for attr, value in stix2_object.items():
                if attr.endswith("_ref"):
                    self._convert_reference(attr, stix2_id, value)
                elif attr.endswith("_refs"):
                    for ref in stix2_object.get("refs", []):
                        self._convert_reference(attr, stix2_id, ref)

        bundle_id = extract_uuid_from_stix2_id(stix2_data.get("id", ""))

        feed_data = {
            "id": bundle_id,
            "name": stix2_data.get("name", "STIX2 Feed"),
            "description": stix2_data.get("description", "Converted from STIX2"),
            "entities": repository.entities,
            "relations": repository.relations,
        }

        return ColanderFeed.model_validate(feed_data)

    def _convert_reference(self, name: str, source_id: str, target_id: str) -> Optional[EntityRelation]:
        if not name or not source_id or not target_id:
            return None
        relation_name = name.replace("_refs", "").replace("_ref", "").replace("_", " ")
        source_object_id = extract_uuid_from_stix2_id(source_id)
        target_object_id = extract_uuid_from_stix2_id(target_id)
        source = ColanderRepository() >> source_object_id
        target = ColanderRepository() >> target_object_id
        if not source or not target:
            return None
        relation = EntityRelation(
            name=relation_name,
            obj_from=source,
            obj_to=target,
        )
        ColanderRepository() << relation
        return relation

    def convert_stix2_object(
        self, stix2_object: Dict[str, Any]
    ) -> Optional[
        Union[Actor, Device, Artifact, Observable, Threat, Event, DetectionRule, DataFragment, EntityRelation]
    ]:
        """
        Convert a STIX2 object to a Colander entity.

        Args:
            stix2_object (Dict[str, Any]): The STIX2 object to convert.

        Returns:
            Optional[Union[Actor, Device, Artifact, Observable, Threat, Event, DetectionRule, DataFragment, EntityRelation]]:
            The converted Colander entity, or None if the object type is not supported.
        """
        stix2_type = stix2_object.get("type", "")

        # Get the Colander entity type for this STIX2 type
        entity_type, entity_subtype_candidates = self.mapping_loader.get_entity_type_for_stix2(stix2_type)

        if entity_type and entity_subtype_candidates:
            # Use the appropriate conversion method based on the entity type
            if entity_type == "actor":
                return self._convert_to_actor(stix2_object, entity_subtype_candidates)
            elif entity_type == "device":
                return self._convert_to_device(stix2_object, entity_subtype_candidates)
            elif entity_type == "artifact":
                return self._convert_to_artifact(stix2_object, entity_subtype_candidates)
            elif entity_type == "observable":
                return self._convert_to_observable(stix2_object, entity_subtype_candidates)
            elif entity_type == "threat":
                return self._convert_to_threat(stix2_object, entity_subtype_candidates)

        # Handle relationship objects
        if stix2_type == "relationship":
            return self._convert_to_relation(stix2_object)

        return None

    def _convert_to_entity(
        self,
        stix2_object: Dict[str, Any],
        model_class: Type["EntityTypes"],
        colander_entity_type,
        default_name: str = "Unknown Entity",
    ) -> Any:
        # Get the field mapping for the entity type
        colander_entity_super_type: CommonEntitySuperType = CommonEntitySuperTypes.by_short_name(model_class.__name__)
        field_mapping = self.mapping_loader.get_stix2_to_colander_field_mapping(model_class.__name__)

        if not colander_entity_type:
            raise ValueError("Invalid entity type")

        # Create the base entity data
        stix2_id = stix2_object.get("id", "")
        extracted_uuid = extract_uuid_from_stix2_id(stix2_id)
        entity_data = {
            "id": extracted_uuid,
            "name": stix2_object.get("name", default_name),
            "description": stix2_object.get("description", ""),
            "super_type": colander_entity_super_type,
            "type": colander_entity_type,
            "attributes": {},
        }

        # Apply the field mapping
        for stix2_field, colander_field in field_mapping.items():
            value = get_nested_value(stix2_object, stix2_field)
            if value is not None:
                if "." in colander_field:
                    # Handle nested fields
                    set_nested_value(entity_data, colander_field, value)
                else:
                    entity_data[colander_field] = value

        # Add any additional attributes from the STIX2 object
        _ignore = ["id", "type"]
        for key, value in stix2_object.items():
            if key not in field_mapping and key not in _ignore and isinstance(value, (str, int, float, bool)):
                entity_data["attributes"][key] = str(value)

        try:
            return model_class.model_validate(entity_data)
        except Exception as e:
            raise e

    def _get_actor_type(self, stix2_object: Dict[str, Any], subtype_candidates: Optional[List[str]]) -> str:
        default_type = ArtifactTypes.default.value.short_name.lower()
        if not subtype_candidates:
            return default_type

        if stix2_object.get("type", "") == "threat-actor":
            default_type = "threat_actor"
            for subtype_candidate in subtype_candidates:
                if subtype_candidate.lower() in stix2_object.get("threat_actor_types", []):
                    return subtype_candidate
            return default_type

        if len(subtype_candidates) == 1:
            return subtype_candidates[0]

        return default_type

    def _convert_to_actor(self, stix2_object: Dict[str, Any], subtype_candidates: Optional[List[str]]) -> Actor:
        _stix2_object = stix2_object.copy()
        if "threat_actor_types" in _stix2_object and _stix2_object["threat_actor_types"] is not None:
            _stix2_object["threat_actor_types"] = ",".join(_stix2_object["threat_actor_types"])

        _actor_type = self._get_actor_type(_stix2_object, subtype_candidates)

        return self._convert_to_entity(
            stix2_object=_stix2_object,
            model_class=Actor,
            colander_entity_type=ActorTypes.by_short_name(_actor_type),
        )

    def _get_device_type(self, stix2_object: Dict[str, Any], subtype_candidates: Optional[List[str]]) -> str:
        default_type = DeviceTypes.default.value.short_name.lower()
        if not subtype_candidates:
            return default_type

        if len(subtype_candidates) == 1:
            return subtype_candidates[0]

        for subtype_candidate in subtype_candidates:
            if subtype_candidate.lower() in stix2_object.get("infrastructure_types", []):
                return subtype_candidate

        return default_type

    def _convert_to_device(self, stix2_object: Dict[str, Any], subtype_candidates: Optional[List[str]]) -> Device:
        _stix2_object = stix2_object.copy()
        if "infrastructure_types" in _stix2_object and _stix2_object["infrastructure_types"] is not None:
            _stix2_object["infrastructure_types"] = ",".join(_stix2_object["infrastructure_types"])

        _device_type = self._get_device_type(_stix2_object, subtype_candidates)
        return self._convert_to_entity(
            stix2_object=_stix2_object,
            model_class=Device,
            colander_entity_type=DeviceTypes.by_short_name(_device_type),
        )

    def _get_artifact_type(self, stix2_object: Dict[str, Any], subtype_candidates: Optional[List[str]]) -> str:
        default_type = ArtifactTypes.default.value.short_name.lower()
        if not subtype_candidates:
            return default_type

        artifact_type = ArtifactTypes.by_mime_type(stix2_object.get("mime_type", "unspecified")).short_name

        return artifact_type or default_type

    def _convert_to_artifact(self, stix2_object: Dict[str, Any], subtype_candidates: Optional[List[str]]) -> Artifact:
        _artifact_type = self._get_artifact_type(stix2_object, subtype_candidates)

        return self._convert_to_entity(
            stix2_object=stix2_object,
            model_class=Artifact,
            colander_entity_type=ArtifactTypes.by_short_name(_artifact_type),
        )

    def _get_observable_type(self, stix2_object: Dict[str, Any], subtype_candidates: Optional[List[str]]) -> str:
        default_type = ObservableTypes.default.value.short_name.lower()
        if not subtype_candidates:
            return default_type

        _pattern_name = extract_stix2_pattern_name(stix2_object.get("pattern", "")) or "unspecified"
        for _candidate in subtype_candidates:
            _mapping = self.mapping_loader.get_entity_subtype_mapping("observable", _candidate)
            if _pattern_name in _mapping["pattern"]:
                return _candidate

        # Return the generic subtype as it was not possible to narrow down the type selection
        return default_type

    def _convert_to_observable(
        self, stix2_object: Dict[str, Any], subtype_candidates: Optional[List[str]]
    ) -> Observable:
        _observable_type = self._get_observable_type(stix2_object, subtype_candidates)
        # Use the generic conversion method
        observable = self._convert_to_entity(
            stix2_object=stix2_object,
            model_class=Observable,
            colander_entity_type=ObservableTypes.by_short_name(_observable_type),
        )
        # Extract value from pattern
        pattern = stix2_object.get("pattern", "")
        extracted_value = extract_stix2_pattern_value(pattern)
        if extracted_value:
            observable.name = extracted_value
        return observable

    def _get_threat_type(self, stix2_object: Dict[str, Any], subtype_candidates: Optional[List[str]]) -> str:
        default_type = ThreatTypes.default.value.short_name.lower()
        if not subtype_candidates:
            return default_type

        for _candidate in subtype_candidates:
            if _candidate in stix2_object.get("malware_types", []):
                return _candidate

        # Return the generic subtype as it was not possible to narrow down the type selection
        return default_type

    def _convert_to_threat(self, stix2_object: Dict[str, Any], subtype_candidates: Optional[List[str]]) -> Threat:
        _threat_type = self._get_threat_type(stix2_object, subtype_candidates)
        # Use the generic conversion method
        return self._convert_to_entity(
            stix2_object=stix2_object,
            model_class=Threat,
            colander_entity_type=ThreatTypes.by_short_name(_threat_type),
        )

    def _convert_to_relation(self, stix2_object: Dict[str, Any]) -> Optional[EntityRelation]:
        relationship_type = stix2_object.get("relationship_type", "")
        source_ref = stix2_object.get("source_ref", "")
        target_ref = stix2_object.get("target_ref", "")

        if not relationship_type or not source_ref or not target_ref:
            return None

        # Extract UUIDs from the references
        source_id = extract_uuid_from_stix2_id(source_ref)
        target_id = extract_uuid_from_stix2_id(target_ref)

        if not source_id or not target_id:
            return None

        # Create the relation data
        relation_data = {
            "id": extract_uuid_from_stix2_id(stix2_object.get("id", "")),
            "name": stix2_object.get("name", relationship_type),
            "description": stix2_object.get("description", ""),
            "created_at": stix2_object.get("created"),
            "updated_at": stix2_object.get("modified"),
            "obj_from": source_id,
            "obj_to": target_id,
            "attributes": {},
        }

        # Add any additional attributes from the STIX2 object
        for key, value in stix2_object.items():
            if key not in [
                "id",
                "type",
                "name",
                "description",
                "created",
                "modified",
                "source_ref",
                "target_ref",
            ] and isinstance(value, (str, int, float, bool)):
                relation_data["attributes"][key] = str(value)

        return EntityRelation.model_validate(relation_data)


class ColanderToStix2Mapper(Stix2Mapper):
    """
    Maps Colander data to STIX2 data using the mapping file.
    """

    def convert(self, colander_feed: ColanderFeed) -> Stix2Bundle:
        stix2_data = {
            "type": "bundle",
            "id": f"bundle--{colander_feed.id or uuid4()}",
            "spec_version": "2.1",
            "objects": [],
        }

        # Convert entities
        for _, entity in colander_feed.entities.items():
            if not issubclass(entity.__class__, Entity):
                continue
            if entity.super_type.short_name.lower() not in self.mapping_loader.get_supported_colander_types():
                continue
            stix2_object = self.convert_colander_entity(entity)
            if stix2_object:
                stix2_data["objects"].append(stix2_object)

        bundle = Stix2Bundle(**stix2_data)

        # Extract and convert immutable relations
        for _, entity in colander_feed.entities.items():
            if not issubclass(entity.__class__, Entity):
                continue
            if entity.super_type.short_name.lower() not in self.mapping_loader.get_supported_colander_types():
                continue
            for _, relation in entity.get_immutable_relations(
                mapping=self.mapping_loader.get_field_relationship_mapping(), default_name="related-to"
            ).items():
                stix2_object = self.convert_colander_relation(relation)
                if stix2_object:
                    bundle.objects.append(Relationship(**stix2_object))

        # Convert relations
        for relation_id, relation in colander_feed.relations.items():
            if isinstance(relation, EntityRelation):
                stix2_object = self.convert_colander_relation(relation)
                if stix2_object:
                    bundle.objects.append(Relationship(**stix2_object))

        return bundle

    def convert_colander_entity(
        self, entity: Union[Actor, Device, Artifact, Observable, Threat]
    ) -> Optional[Dict[str, Any]]:
        """
        Convert a Colander entity to a STIX2 object.

        Args:
            entity: The Colander entity to convert.

        Returns:
            Optional[Dict[str, Any]]: The converted STIX2 object, or None if the entity type is not supported.
        """
        if isinstance(entity, Actor):
            return self._convert_from_actor(entity)
        elif isinstance(entity, Device):
            return self._convert_from_device(entity)
        elif isinstance(entity, Artifact):
            return self._convert_from_artifact(entity)
        elif isinstance(entity, Observable):
            return self._convert_from_observable(entity)
        elif isinstance(entity, Threat):
            return self._convert_from_threat(entity)

        return None

    def convert_colander_relation(self, relation: EntityRelation) -> Optional[Dict[str, Any]]:
        """
        Convert a Colander EntityRelation to a STIX2 relationship object.

        Args:
            relation (~colander_data_converter.base.models.EntityRelation): The Colander EntityRelation to convert.

        Returns:
            Optional[Dict[str, Any]]: The converted STIX2 relationship object, or None if the relation cannot be
            converted.
        """
        return self._convert_from_relation(relation)

    def _convert_from_entity(
        self, entity: Any, additional_fields: Optional[Dict[str, Any]] = None
    ) -> Optional[Stix2ObjectTypes]:
        # Get the STIX2 type for the entity
        stix2_type = self.mapping_loader.get_stix2_type_for_entity(entity)
        if not stix2_type or (model_class := Stix2ObjectBase.get_model_class(stix2_type)) is None:
            return None

        # Get the field mapping for the entity type
        entity_type = entity.get_super_type().short_name
        field_mapping = self.mapping_loader.get_colander_to_stix2_field_mapping(entity_type)

        # Create the base STIX2 object
        stix2_object = {
            "type": stix2_type,
            "id": f"{stix2_type}--{entity.id}",
            "created": entity.created_at.isoformat(),
            "modified": entity.updated_at.isoformat(),
        }

        if "name" in model_class.model_fields:
            stix2_object["name"] = entity.name

        # Add any additional fields
        if additional_fields:
            stix2_object.update(additional_fields)

        # Apply the field mapping
        for colander_field, stix2_field in field_mapping.items():
            value = get_nested_value(entity.model_dump(), colander_field)
            if value is not None:
                if "." in stix2_field:
                    # Handle nested fields
                    set_nested_value(stix2_object, stix2_field, value)
                else:
                    stix2_object[stix2_field] = value

        # Add any additional attributes
        if hasattr(entity, "attributes") and entity.attributes:
            for key, value in entity.attributes.items():
                if key not in [field.split(".")[-1] for field in field_mapping.keys() if "." in field]:
                    stix2_object[key] = value

        return model_class(**stix2_object)

    def _convert_from_actor(self, actor: Actor) -> Optional[Dict[str, Any]]:
        mapping = self.mapping_loader.get_actor_mapping(actor.type.short_name)
        if not mapping:
            return None
        extra_attributes = self.mapping_loader.get_entity_extra_values("actor", actor.type.short_name)

        return self._convert_from_entity(actor, extra_attributes)

    def _convert_from_device(self, device: Device) -> Optional[Dict[str, Any]]:
        mapping = self.mapping_loader.get_device_mapping(device.type.short_name)
        if not mapping:
            return None
        extra_attributes = self.mapping_loader.get_entity_extra_values("device", device.type.short_name)
        return self._convert_from_entity(device, extra_attributes)

    def _convert_from_artifact(self, artifact: Artifact) -> Dict[str, Any]:
        return self._convert_from_entity(artifact)

    def _generate_observable_pattern(self, observable: Observable) -> Dict[str, Any]:
        pattern_fields = {}

        observable_type_short_name = observable.type.short_name.lower()
        pattern_template = self.mapping_loader.get_observable_pattern(observable_type_short_name)
        pattern_fields["pattern_type"] = "stix"
        if pattern_template:
            pattern_fields["pattern"] = pattern_template.format(value=observable.name)
        # If the observable type is not found in the mapping, use a generic pattern
        else:
            pattern_fields["pattern"] = f"[unknown:value = '{observable.name}']"

        return pattern_fields

    def _convert_from_observable(self, observable: Observable) -> Dict[str, Any]:
        # Generate pattern fields for the observable
        pattern_fields = self._generate_observable_pattern(observable)
        additional_fields = {}
        additional_fields.update(pattern_fields)

        # Add indicator_types to the additional fields
        if observable.associated_threat is not None:
            additional_fields.update({"indicator_types": ["malicious-activity"]})

        return self._convert_from_entity(observable, additional_fields)

    def _get_threat_malware_types(self, threat: Threat) -> Dict[str, Any]:
        additional_fields = {}

        # Get the STIX2 type for threats
        stix2_type = self.mapping_loader.get_stix2_type_for_entity(threat)

        # Add malware_types if the type is malware
        if stix2_type == "malware":
            threat_type_short_name = threat.type.short_name.lower()
            malware_types = self.mapping_loader.get_malware_types_for_threat(threat_type_short_name)
            if malware_types:
                additional_fields["malware_types"] = malware_types
            else:
                additional_fields["malware_types"] = ["unknown", threat_type_short_name]

        return additional_fields

    def _convert_from_threat(self, threat: Threat) -> Dict[str, Any]:
        additional_fields = self._get_threat_malware_types(threat)
        return self._convert_from_entity(threat, additional_fields)

    def _convert_from_relation(self, relation: EntityRelation) -> Optional[Dict[str, Any]]:
        if not relation.obj_from or not relation.obj_to:
            return None

        if not relation.is_fully_resolved():
            return None

        supported_types = self.mapping_loader.get_supported_colander_types()
        if (
            relation.obj_from.super_type.short_name.lower() not in supported_types
            or relation.obj_to.super_type.short_name.lower() not in supported_types
        ):
            return None

        source_prefix = self.mapping_loader.get_stix2_type_for_entity(relation.obj_from) or "unknown"
        target_prefix = self.mapping_loader.get_stix2_type_for_entity(relation.obj_to) or "unknown"
        source_ref = f"{source_prefix}--{relation.obj_from.id}"
        target_ref = f"{target_prefix}--{relation.obj_to.id}"
        repository = Stix2Repository()
        source = repository >> source_ref
        target = repository >> target_ref

        if not source or not target:
            return None

        # Create the base STIX2 relationship object
        stix2_object = {
            "type": "relationship",
            "id": f"relationship--{relation.id}",
            "relationship_type": relation.name.replace(" ", "-"),
            "created": relation.created_at.isoformat(),
            "modified": relation.updated_at.isoformat(),
            "source_ref": f"{source_prefix}--{relation.obj_from.id}",
            "target_ref": f"{target_prefix}--{relation.obj_to.id}",
        }

        # Add any additional attributes
        if hasattr(relation, "attributes") and relation.attributes:
            for key, value in relation.attributes.items():
                stix2_object[key] = value

        return stix2_object


class Stix2Converter:
    """
    Converter for STIX2 data to Colander data and vice versa.
    Uses the mapping file to convert between formats.
    """

    @staticmethod
    def stix2_to_colander(stix2_data: Dict[str, Any]) -> ColanderFeed:
        """
        Converts STIX2 data to Colander data using the mapping file.

        Args:
            stix2_data (Dict[str, Any]): The STIX2 data to convert.

        Returns:
            ColanderFeed: The converted Colander data.
        """
        mapper = Stix2ToColanderMapper()
        return mapper.convert(stix2_data)

    @staticmethod
    def colander_to_stix2(colander_feed: ColanderFeed) -> Stix2Bundle:
        """
        Converts Colander data to STIX2 data using the mapping file.

        Args:
            colander_feed (ColanderFeed): The Colander data to convert.

        Returns:
            Stix2Bundle: The converted STIX2 bundle.
        """
        mapper = ColanderToStix2Mapper()
        colander_feed.resolve_references()
        return mapper.convert(colander_feed)
