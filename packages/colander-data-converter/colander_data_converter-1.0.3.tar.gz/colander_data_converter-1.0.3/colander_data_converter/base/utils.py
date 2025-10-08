import enum
from typing import get_args, List, Any, Optional

from pydantic import BaseModel

from colander_data_converter.base.common import ObjectReference


class MergingStrategy(str, enum.Enum):
    PRESERVE = "preserve"
    OVERWRITE = "overwrite"


class BaseModelMerger:
    """
    A utility class for merging :py:class:`pydantic.BaseModel` instances with configurable strategies.

    This class provides functionality to merge fields from a source BaseModel into a
    destination BaseModel, handling both regular model fields and extra attributes.
    Fields containing `ObjectReference` types are automatically
    excluded from merging and reported as unprocessed.

    The merger supports two strategies:

    - ``PRESERVE``: Only merge fields if the destination field is empty or `None`
    - ``OVERWRITE``: Always merge fields from source to destination

    Fields are merged based on type compatibility and field constraints. Extra
    attributes are automatically converted to strings when stored in the attributes
    dictionary (if supported by the destination model).

    Example:
        >>> from pydantic import BaseModel
        >>> class SourceModel(BaseModel):
        ...     name: str
        ...     age: int
        ...     attributes: dict = {}
        >>> class DestinationModel(BaseModel):
        ...     name: str
        ...     age: int
        ...     city: str = "Unknown"
        ...     attributes: dict = {}
        >>> source = SourceModel(name="Alice", age=30)
        >>> destination = DestinationModel(name="Bob", age=25)
        >>> merger = BaseModelMerger(strategy=MergingStrategy.OVERWRITE)
        >>> unprocessed = merger.merge(source, destination)
        >>> print(destination.name)
        Alice
        >>> print(destination.age)
        30
        >>> print(destination.city)
        Unknown

    Note:
        - Fields with ``ObjectReference`` types are never merged and are reported as unprocessed
        - Frozen fields cannot be modified and will be reported as unprocessed
        - Complex types (list, dict, tuple, set) in extra attributes are not supported
        - Extra attributes are converted to strings when stored
    """

    def __init__(self, strategy: MergingStrategy = MergingStrategy.OVERWRITE):
        """Initialize the ``BaseModelMerger`` with a merging strategy.

        Args:
            strategy: The strategy to use when merging fields.
        """
        self.strategy = strategy

    def merge_field(
        self, destination: BaseModel, field_name: str, field_value: Any, ignored_fields: Optional[List[str]] = None
    ) -> bool:
        """Merge a single field from source to destination model.

        This method handles the logic for merging individual fields, including
        type checking, field existence validation, and attribute handling. It
        processes both regular model fields and extra attributes based on the
        destination model's capabilities and field constraints.

        Note:
            The method follows these rules:

            - Skips fields listed in ignored_fields
            - Skips empty/None field values
            - For fields not in the destination model schema: stores as string in
              attributes dict (if supported) unless the value is a complex type
            - For schema fields: merges only if type-compatible, not frozen, not
              containing ObjectReference, and destination is empty (``PRESERVE``) or
              strategy is ``OVERWRITE``

        Args:
            destination: The target model to merge into.
            field_name: The name of the field to merge.
            field_value: The value to merge from the source.
            ignored_fields: List of field names to skip during merging.

        Returns:
            True if the field was processed (successfully merged or handled),
            False if the field could not be processed
        """
        field_processed = False
        if not field_value:
            return field_processed
        if not ignored_fields:
            ignored_fields = []
        extra_attributes_supported = hasattr(destination, "attributes")
        source_field_value = field_value
        source_field_value_type = type(field_value)
        if field_name in ignored_fields:
            return field_processed
        # Append in extra attribute dict if supported
        if (
            field_name not in destination.__class__.model_fields
            and extra_attributes_supported
            and source_field_value_type not in [list, dict, tuple, set, ObjectReference]
            and not isinstance(source_field_value, BaseModel)
        ):
            destination.attributes[field_name] = str(source_field_value)
            field_processed = True
        elif field_name in destination.__class__.model_fields:
            field_info = destination.__class__.model_fields[field_name]
            annotation_args = get_args(field_info.annotation) or []  # type: ignore[var-annotated]
            if (
                ObjectReference not in annotation_args
                and List[ObjectReference] not in annotation_args
                and not field_info.frozen
                and (not getattr(destination, field_name, None) or self.strategy == MergingStrategy.OVERWRITE)
                and (source_field_value_type is field_info.annotation or source_field_value_type in annotation_args)
            ):
                setattr(destination, field_name, source_field_value)
                field_processed = True
        return field_processed

    def merge(self, source: BaseModel, destination: BaseModel, ignored_fields: Optional[List[str]] = None) -> List[str]:
        """Merge all compatible fields from the source object into the destination object.

        This method iterates through all fields in the source object and attempts
        to merge them into the destination object. It handles both regular object
        fields and extra attributes dictionary if supported.

        Args:
            source: The source model to merge from
            destination: The destination model to merge to
            ignored_fields: List of field names to skip during merging

        Returns:
            A list of field names that could not be processed during
            the merge operation. Fields containing ObjectReference types
            are automatically added to this list.
        """
        unprocessed_fields = []
        source_attributes = getattr(source, "attributes", None)
        destination_attributes = getattr(destination, "attributes", None)

        if destination_attributes is None and hasattr(destination, "attributes"):
            destination.attributes = {}

        # Merge model fields
        for field_name, field_info in source.__class__.model_fields.items():
            source_field_value = getattr(source, field_name, None)
            if ObjectReference in get_args(field_info.annotation):
                unprocessed_fields.append(field_name)
            elif not self.merge_field(destination, field_name, source_field_value, ignored_fields):
                unprocessed_fields.append(field_name)

        # Merge extra attributes
        if source_attributes:
            for name, value in source_attributes.items():
                if not self.merge_field(destination, name, value):
                    unprocessed_fields.append(f"attributes.{name}")

        return unprocessed_fields
