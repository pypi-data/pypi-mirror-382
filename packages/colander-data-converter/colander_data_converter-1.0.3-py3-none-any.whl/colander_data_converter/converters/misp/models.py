import json
from importlib import resources
from typing import Optional, Dict, Any, Type, List, Tuple, Union

from pydantic import BaseModel, ConfigDict
from pymisp import MISPObject, AbstractMISP, MISPAttribute, MISPTag

from colander_data_converter.base.models import CommonEntitySuperTypes, CommonEntitySuperType
from colander_data_converter.base.types.base import CommonEntityType
from colander_data_converter.converters.misp.utils import get_attribute_by_name

type ColanderMISPMapping = Dict[str, Any]
type RelationMapping = Dict[str, Any]


class TagStub(str):
    pass


class Discriminator(BaseModel):
    type: str
    property: str
    target: str
    value: Optional[str] = None


class MISPColanderMapping(BaseModel):
    also: Optional[List[str]] = None
    discriminator: Optional[Discriminator] = None


class EntityTypeMapping(BaseModel):
    colander_type: str
    misp_object: str
    misp_type: Optional[str] = None
    misp_definition: Optional[str] = None
    misp_colander_mapping: MISPColanderMapping
    colander_misp_mapping: ColanderMISPMapping
    colander_super_type: Optional[CommonEntitySuperType] = None

    @property
    def colander_entity_type(self) -> CommonEntityType:
        return self.colander_super_type.type_by_short_name(self.colander_type)

    def get_misp_model_class(self) -> Tuple[Type[AbstractMISP], str]:
        if self.misp_object == "misp-attribute":
            return MISPAttribute, self.misp_type
        elif self.misp_object == "misp-tag":
            return MISPTag, self.misp_type
        return MISPObject, self.misp_object

    def get_colander_misp_field_mapping(self) -> List[Optional[Tuple[str, str]]]:
        return [(src, dst) for src, dst in self.colander_misp_mapping.items() if isinstance(dst, str)]

    def get_colander_misp_literals_mapping(self) -> List[Optional[Tuple[str, str]]]:
        return [(src, dst) for src, dst in self.colander_misp_mapping.get("literals", {}).items()]

    def get_colander_misp_attributes_mapping(self) -> List[Optional[Tuple[str, str]]]:
        return [
            (src, dst)
            for src, dst in self.colander_misp_mapping.get("misp_attributes", {}).items()
            if isinstance(dst, str)
        ]


class EntitySuperTypeMapping(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
    )
    colander_super_type: str
    model_class: Any
    types_mapping: Dict[str, EntityTypeMapping] = {}

    def get_supported_colander_types(self) -> List[Optional[str]]:
        return list(self.types_mapping.keys())


class Mapping(object):
    TYPES = [
        (CommonEntitySuperTypes.ACTOR.value, "actor"),
        (CommonEntitySuperTypes.ARTIFACT.value, "artifact"),
        (CommonEntitySuperTypes.DEVICE.value, "device"),
        (CommonEntitySuperTypes.EVENT.value, "event"),
        (CommonEntitySuperTypes.DATA_FRAGMENT.value, "data_fragment"),
        (CommonEntitySuperTypes.DETECTION_RULE.value, "detection_rule"),
        (CommonEntitySuperTypes.OBSERVABLE.value, "observable"),
        (CommonEntitySuperTypes.THREAT.value, "threat"),
    ]

    def __init__(self):
        self.misp_objects_mapping: Dict[str, List[EntityTypeMapping]] = {}
        self.misp_attributes_mapping: Dict[str, List[EntityTypeMapping]] = {}
        self.misp_tags_mapping: Dict[str, EntityTypeMapping] = {}
        self.colander_super_types_mapping: Dict[str, EntitySuperTypeMapping] = {}
        self.colander_relation_mapping = self._load_relation_mapping_definition()
        for type_class, prefix in self.TYPES:
            self.colander_super_types_mapping[type_class.short_name] = self._load_mapping_definition(type_class, prefix)
        self._build_misp_mapping()

    @staticmethod
    def _load_relation_mapping_definition() -> RelationMapping:
        resource_package = __name__
        json_file = resources.files(resource_package).joinpath("data").joinpath("relation_misp_mapping.json")
        with json_file.open() as f:
            return json.load(f)

    @staticmethod
    def _load_mapping_definition(type_class: CommonEntitySuperType, filename_prefix: str) -> EntitySuperTypeMapping:
        resource_package = __name__
        json_file = resources.files(resource_package).joinpath("data").joinpath(f"{filename_prefix}_misp_mapping.json")
        super_type_mapping = EntitySuperTypeMapping(colander_super_type=type_class.short_name, model_class=type_class)
        with json_file.open() as f:
            raw = json.load(f)
            for definition in raw:
                type_mapping = EntityTypeMapping.model_validate(definition)
                type_mapping.colander_super_type = type_class
                super_type_mapping.types_mapping[type_mapping.colander_type] = type_mapping
        return super_type_mapping

    def _build_misp_mapping(self):
        for _, super_type_mapping in self.colander_super_types_mapping.items():
            for _, type_mapping in super_type_mapping.types_mapping.items():
                if type_mapping.misp_object == "misp-attribute":
                    if type_mapping.misp_type not in self.misp_attributes_mapping:
                        self.misp_attributes_mapping[type_mapping.misp_type] = []
                    for s in type_mapping.misp_colander_mapping.also or []:
                        self.misp_attributes_mapping[s] = [type_mapping]
                    self.misp_attributes_mapping[type_mapping.misp_type].append(type_mapping)
                if type_mapping.misp_object == "misp-tag":
                    tag_name = type_mapping.colander_misp_mapping["literals"]["name"].replace("{value}", "")
                    self.misp_tags_mapping[tag_name] = type_mapping
                else:
                    if type_mapping.misp_object not in self.misp_objects_mapping:
                        self.misp_objects_mapping[type_mapping.misp_object] = []
                    self.misp_objects_mapping[type_mapping.misp_object].append(type_mapping)

    def get_relation_mapping_to_misp(
        self, super_type: CommonEntitySuperType, reference_name: str
    ) -> Optional[RelationMapping]:
        mapping = self.colander_relation_mapping.get(super_type.short_name, {})
        return mapping.get(reference_name, None)

    def get_mapping_to_misp(
        self, entity_super_type: CommonEntitySuperType, entity_type: CommonEntityType
    ) -> Optional[EntityTypeMapping]:
        est_mapping = self.colander_super_types_mapping.get(entity_super_type.short_name, None)
        if est_mapping:
            return est_mapping.types_mapping.get(entity_type.short_name, None)
        return None

    def get_misp_object_or_attribute_value(self) -> Optional[str]:
        return None

    def match_discriminator(self, misp_object: Union[MISPObject, MISPAttribute], discriminator: Discriminator) -> bool:
        matched = False
        if not discriminator or not misp_object:
            return matched

        target_type = discriminator.target
        if target_type == "self" and not isinstance(misp_object, MISPAttribute):
            raise Exception("Discriminator target of type 'self' is only supported for MISPAttribute")
        if target_type == "attribute-value" and not isinstance(misp_object, MISPObject):
            raise Exception("Discriminator target of type 'attribute-value' is only supported for MISPObject")

        value = None
        if target_type == "self":
            value = getattr(misp_object, discriminator.property)
        elif target_type == "attribute-value":
            attribute = get_attribute_by_name(misp_object, discriminator.property)
            if attribute:
                value = attribute.value

        if discriminator.type == "match":
            matched = value == discriminator.value

        return matched

    def get_misp_object_mapping(self, misp_object: MISPObject) -> Optional[EntityTypeMapping]:
        if not misp_object:
            return None
        candidates = self.misp_objects_mapping.get(misp_object.name, [])
        if len(candidates) == 1:
            return candidates[0]
        for candidate in candidates:
            types_class = candidate.colander_super_type.types_class
            if (discriminator := candidate.misp_colander_mapping.discriminator) is None:
                continue
            if discriminator.type == "suggest":
                value = None
                if discriminator.target == "self":
                    value = getattr(misp_object, discriminator.property)
                elif discriminator.target == "attribute-value":
                    if (attribute := get_attribute_by_name(misp_object, discriminator.property)) is None:
                        return None
                    value = attribute.value
                if not value:
                    return None
                if (suggested_type := types_class.suggest(value)) is None:
                    return None
                mapping = self.get_mapping_to_misp(candidate.colander_super_type, suggested_type)
                return mapping
            elif self.match_discriminator(misp_object, discriminator):
                return candidate
        return None

    def get_misp_attribute_mapping(self, misp_attribute: MISPAttribute) -> Optional[EntityTypeMapping]:
        if not misp_attribute:
            return None
        candidates = self.misp_attributes_mapping.get(misp_attribute.type, [])
        if len(candidates) == 1:
            return candidates[0]
        for candidate in candidates:
            types_class = candidate.colander_super_type.types_class
            if (discriminator := candidate.misp_colander_mapping.discriminator) is None:
                continue
            if discriminator.type == "suggest":
                if (suggested_type := types_class.suggest(getattr(misp_attribute, discriminator.property))) is None:
                    return None
                mapping = self.get_mapping_to_misp(candidate.colander_super_type, suggested_type)
                return mapping
            elif self.match_discriminator(misp_attribute, discriminator):
                return candidate
        return None

    def get_misp_tag_mapping(self, misp_tag: MISPTag) -> Optional[EntityTypeMapping]:
        if not misp_tag:
            return None
        for tag_name, mapping in self.misp_tags_mapping.items():
            if tag_name in misp_tag.name:
                return mapping
        return None
