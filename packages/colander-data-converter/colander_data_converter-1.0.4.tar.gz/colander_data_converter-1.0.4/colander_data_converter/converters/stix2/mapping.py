import json
from importlib import resources
from typing import Dict, Any, List, Optional, Set, Tuple

from colander_data_converter.base.models import Entity

resource_package = __name__


class Stix2MappingLoader:
    """
    Loads and provides access to the STIX2 to Colander mapping data.
    """

    def __init__(self):
        """
        Initialize the mapping loader.
        """
        # Load the mapping data
        self.mapping_data = self._load_mapping_data()

    @staticmethod
    def _load_mapping_data() -> Dict[str, Any]:
        json_file = resources.files(resource_package).joinpath("data").joinpath("stix2_colander_mapping.json")
        try:
            with json_file.open() as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to load mapping data: {e}")

    def get_entity_type_mapping(self, entity_type: str) -> Dict[str, Any]:
        """
        Get the mapping data for a specific Colander entity type.

        Args:
            entity_type (str): The entity type (e.g., "actor", "device").

        Returns:
            Dict[str, Any]: The mapping data for the entity type.
        """
        _entity_type = entity_type.lower()
        if _entity_type not in self.mapping_data:
            return {}
        return self.mapping_data[_entity_type]

    def get_entity_subtype_mapping(self, entity_type: str, entity_subtype: str) -> Dict[str, Any]:
        """
        Get the mapping data for a specific Colander entity type.

        Args:
            entity_type (str): The entity type (e.g., "actor", "device").
            entity_subtype (str): The Colander entity subtype (e.g. "ipv4").

        Returns:
            Dict[str, Any]: The mapping data for the entity type.
        """
        _entity_type = entity_type.lower()
        _entity_subtype = entity_subtype.lower()
        if _entity_type not in self.mapping_data:
            return {}
        _entity_type_mapping = self.mapping_data[_entity_type]
        if _entity_subtype not in _entity_type_mapping["types"]:
            return {}
        return _entity_type_mapping["types"][_entity_subtype]

    def get_stix2_type_for_entity(self, entity: Entity) -> str:
        _entity_mapping = self.get_entity_subtype_mapping(
            entity.get_super_type().short_name, entity.get_type().short_name
        )
        return _entity_mapping.get("stix2_type", "")

    def get_supported_colander_types(self) -> List[str]:
        return self.mapping_data.get("supported_colander_types", [])

    def get_supported_stix2_types(self) -> List[str]:
        _types: Set[str] = set()
        for _supported_colander_type in self.get_supported_colander_types():
            _type_mapping = self.mapping_data.get(_supported_colander_type, {})
            for _subtype_name, _mapping in _type_mapping.get("types", {}).items():
                _types.add(_mapping.get("stix2_type", ""))
        return list(_types)

    def get_entity_type_for_stix2(self, stix2_type: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Get the Colander entity type for a STIX2 type (e.g. "indicator", "threat-actor").

        Args:
            stix2_type (str): The STIX2 type.

        Returns:
            Tuple[Optional[str], Optional[List[str]]]: The corresponding Colander type and the list of
            subtype candidates, or None if not found.
        """
        if stix2_type not in self.get_supported_stix2_types():
            return None, None

        # Create mapping between STIX2 and Colander types (e.g. "treat-actor" -> "actor")
        _stix2_type_mapping: Dict[str, str] = {}
        for _supported_colander_type in self.get_supported_colander_types():
            for _supported_colander_subtype, _mapping in self.mapping_data[_supported_colander_type]["types"].items():
                _stix2_type_mapping[_mapping["stix2_type"]] = _supported_colander_type
        if stix2_type not in _stix2_type_mapping:
            return None, None

        _colander_type_name = _stix2_type_mapping[stix2_type]  # e.g. observable
        _colander_type_mapping = self.get_entity_type_mapping(_colander_type_name)

        # Iterate over Colander subtypes(e.g. ipv4, domain)
        _subtype_candidates: Set[str] = set()
        for _colander_subtype_name, _mapping in _colander_type_mapping.get("types", {}).items():
            # List subtype candidates
            if "stix2_type" in _mapping and _mapping["stix2_type"] == stix2_type:
                _subtype_candidates.add(_colander_subtype_name)

        # If not candidates, append the "generic" subtype
        if len(_subtype_candidates) == 0:
            _subtype_candidates.add("generic")

        return _colander_type_name, list(_subtype_candidates)

    def get_stix2_to_colander_field_mapping(self, entity_type: str) -> Dict[str, str]:
        """
        Get the field mapping from STIX2 to Colander for a specific entity type.

        Args:
            entity_type (str): The entity type.

        Returns:
            Dict[str, str]: The field mapping from STIX2 to Colander.
        """
        entity_mapping = self.get_entity_type_mapping(entity_type)
        return entity_mapping.get("stix2_to_colander", {})

    def get_colander_to_stix2_field_mapping(self, entity_type: str) -> Dict[str, str]:
        entity_mapping = self.get_entity_type_mapping(entity_type)
        return entity_mapping.get("colander_to_stix2", {})

    def get_field_relationship_mapping(self) -> Dict[str, str]:
        return self.mapping_data.get("field_relationship_map", {})

    def get_observable_mapping(self, observable_type: str) -> Dict[str, Any]:
        return self.get_entity_subtype_mapping("observable", observable_type)

    def get_observable_pattern(self, observable_type: str) -> str:
        mapping = self.get_observable_mapping(observable_type)
        if mapping:
            return mapping["pattern"]
        return "[unknown:value = '{value}']"

    def get_threat_mapping(self, threat_type: str) -> Dict[str, Any]:
        return self.get_entity_subtype_mapping("threat", threat_type)

    def get_malware_types_for_threat(self, threat_type: str) -> List[str]:
        threat_mapping = self.get_threat_mapping(threat_type)
        return threat_mapping.get("malware_types", [])

    def get_actor_mapping(self, actor_type: str) -> Dict[str, Any]:
        return self.get_entity_subtype_mapping("actor", actor_type)

    def get_device_mapping(self, device_type: str) -> Dict[str, Any]:
        return self.get_entity_subtype_mapping("device", device_type)

    def get_entity_extra_values(self, entity_type: str, entity_subtype: str) -> Dict[str, Any]:
        mapping = self.get_entity_subtype_mapping(entity_type, entity_subtype).copy()
        if "stix2_type" in mapping:
            mapping.pop("stix2_type")
        return mapping
