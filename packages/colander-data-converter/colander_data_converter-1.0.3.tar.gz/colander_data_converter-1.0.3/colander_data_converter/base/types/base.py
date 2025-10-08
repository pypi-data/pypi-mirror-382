import abc
import json
from importlib import resources
from typing import List, Dict, Optional, Any, TypeVar

from pydantic import BaseModel, Field, ConfigDict

resource_package = __name__


def load_entity_supported_types(name: str) -> List[Dict]:
    json_file = (
        resources.files(resource_package)
        .joinpath("..")
        .joinpath("..")
        .joinpath("data")
        .joinpath("types")
        .joinpath(f"{name}_types.json")
    )
    with json_file.open() as f:
        return json.load(f)


EntityType_T = TypeVar("EntityType_T", bound="CommonEntityType")


class CommonEntityType(BaseModel, abc.ABC):
    """CommonEntityType is an abstract base class for defining shared attributes across various entity data types.

    This class provides fields for identifiers, names, descriptions, and other metadata.
    """

    model_config: ConfigDict = ConfigDict(str_strip_whitespace=True, arbitrary_types_allowed=True, from_attributes=True)

    short_name: str = Field(frozen=True, max_length=32)
    """A short name for the model type."""

    name: str = Field(frozen=True, max_length=512)
    """The name of the model type."""

    description: str | None = Field(default=None, exclude=False)
    """An optional description of the model type."""

    icon: str | None = Field(default=None, exclude=True)
    """Optional icon name for the model type (e.g., mdi:home)."""

    nf_icon: str | None = Field(default=None, exclude=True)
    """Optional NerdFont icon name for the model type."""

    value_example: str | None = Field(default=None, exclude=True)
    """Optional example value for the model type."""

    regex: str | None = Field(default=None, exclude=True)
    """Optional regex used to suggest a type based on the entity name."""

    default_attributes: Optional[Dict[str, str]] = Field(default=None, exclude=True)
    """Optional dictionary of default attributes."""

    type_hints: Dict[Any, Any] | None = Field(default=None, exclude=True)
    """Optional dictionary of type hints."""

    def __str__(self):
        return self.short_name

    def __repr__(self):
        return self.short_name
