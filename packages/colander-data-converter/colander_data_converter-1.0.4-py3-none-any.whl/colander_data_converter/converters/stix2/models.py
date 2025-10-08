from datetime import datetime, UTC
from typing import Dict, Optional, TYPE_CHECKING, Literal, List, TypeVar, Annotated, Union, Generator, Type
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict

from colander_data_converter.base.common import Singleton

# Avoid circular imports
if TYPE_CHECKING:
    pass


class Stix2Repository(object, metaclass=Singleton):
    """
    Singleton repository for managing and storing STIX2 objects.

    This class provides centralized storage and reference management for all STIX2 objects,
    supporting conversion to and from Colander data.
    """

    stix2_objects: Dict[str, "Stix2ObjectTypes"]

    def __init__(self):
        """
        Initializes the repository with an empty dictionary for STIX2 objects.
        """
        self.stix2_objects = {}

    def __lshift__(self, stix2_object: "Stix2ObjectTypes") -> None:
        """
        Adds a STIX2 object to the repository.

        Args:
            stix2_object (Dict[str, Any]): The STIX2 object to add.
        """
        self.stix2_objects[stix2_object.id] = stix2_object

    def __rshift__(self, object_id: str) -> Optional["Stix2ObjectTypes"]:
        """
        Retrieves a STIX2 object from the repository by its ID.

        Args:
            object_id (str): The ID of the STIX2 object to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The STIX2 object if found, None otherwise.
        """
        return self.stix2_objects.get(object_id)

    def clear(self) -> None:
        """
        Clears all STIX2 objects from the repository.
        """
        self.stix2_objects.clear()


Stix2Object_T = TypeVar("Stix2Object_T", bound="Stix2ObjectBase")
Stix2ObjectTypes = Annotated[
    Union[
        "File",
        "Indicator",
        "Infrastructure",
        "Identity",
        "Malware",
        "ThreatActor",
        "Relationship",
    ],
    Field(discriminator="type"),
]


class Stix2ObjectBase(BaseModel):
    type: str = Field(..., frozen=True)
    created: str = Field(frozen=True, default=datetime.now(UTC).isoformat())
    modified: str = Field(default=datetime.now(UTC).isoformat())
    description: str | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        extra="allow",
    )

    def model_post_init(self, __context):
        """Executes post-initialization logic for the model, ensuring the repository
        registers the current subclass instance.

        Args:
            __context (Any): Additional context provided for post-initialization handling.
        """
        _ = Stix2Repository()
        _ << self

    @classmethod
    def subclasses(cls) -> Dict[str, Type["Stix2ObjectBase"]]:
        subclasses: Dict[str, Type["Stix2ObjectBase"]] = {}
        for subclass in cls.__subclasses__():
            subclasses[subclass.__name__.lower()] = subclass
        return subclasses

    @classmethod
    def get_supported_types(cls) -> List[str]:
        types = []
        for _, subclass in cls.subclasses().items():
            types.append(subclass.model_fields["type"].default)
        return types

    @classmethod
    def get_model_class(cls, type_name: str) -> Optional[Type["Stix2ObjectBase"]]:
        for _, subclass in cls.subclasses().items():
            if type_name == subclass.model_fields["type"].default:
                return subclass
        return None


class File(Stix2ObjectBase):
    id: str = Field(frozen=True, default_factory=lambda: f"file--{uuid4()}")
    type: Literal["file"] = "file"
    name: str = Field(...)


class Indicator(Stix2ObjectBase):
    id: str = Field(frozen=True, default_factory=lambda: f"indicator--{uuid4()}")
    type: Literal["indicator"] = "indicator"
    name: str = Field(...)
    pattern: str = ""
    pattern_type: str = "stix"


class Infrastructure(Stix2ObjectBase):
    id: str = Field(frozen=True, default_factory=lambda: f"infrastructure--{uuid4()}")
    type: Literal["infrastructure"] = "infrastructure"
    name: str = Field(...)
    infrastructure_types: List[str] = []


class Identity(Stix2ObjectBase):
    id: str = Field(frozen=True, default_factory=lambda: f"identity--{uuid4()}")
    type: Literal["identity"] = "identity"
    name: str = Field(...)
    identity_class: str = ""


class Malware(Stix2ObjectBase):
    id: str = Field(frozen=True, default_factory=lambda: f"malware--{uuid4()}")
    type: Literal["malware"] = "malware"
    name: str = Field(...)
    malware_types: List[str] = []


class ThreatActor(Stix2ObjectBase):
    id: str = Field(frozen=True, default_factory=lambda: f"threat-actor--{uuid4()}")
    type: Literal["threat-actor"] = "threat-actor"
    name: str = Field(...)
    threat_actor_types: List[str] = []


class Relationship(Stix2ObjectBase):
    id: str = Field(frozen=True, default_factory=lambda: f"relationship--{uuid4()}")
    type: Literal["relationship"] = "relationship"
    relationship_type: str = ""
    source_ref: str
    target_ref: str


class Stix2Bundle(BaseModel):
    id: str = Field(frozen=True, default_factory=lambda: f"bundle--{uuid4()}")
    type: Literal["bundle"] = "bundle"
    spec_version: Literal["2.1"] = "2.1"
    objects: List[Stix2ObjectTypes] = []

    def by_type(self, object_type: Type["Stix2Object_T"]) -> Generator[Stix2Object_T, None, None]:
        for obj in self.objects:
            if obj.type == object_type.model_fields["type"].default:
                yield obj

    def by_id(self, obj_id: str) -> Optional[Stix2Object_T]:
        for obj in self.objects:
            if obj.id == obj_id:
                return obj
        return None

    @staticmethod
    def load(raw_object: dict) -> "Stix2Bundle":
        supported_types = Stix2ObjectBase.get_supported_types()
        objects_to_process = []

        for obj in raw_object["objects"]:
            if obj["type"] in supported_types:
                objects_to_process.append(obj)

        raw_object["objects"] = objects_to_process
        bundle = Stix2Bundle.model_validate(raw_object)

        for relation in bundle.by_type(Relationship):
            source = bundle.by_id(relation.source_ref)
            target = bundle.by_id(relation.target_ref)
            # Remove partially resolved relationships
            if not source or not target:
                bundle.objects.remove(relation)

        return bundle
