import csv
from typing import List, get_args, Dict, Set, TextIO

from pydantic import BaseModel

from colander_data_converter.base.common import ObjectReference
from colander_data_converter.base.models import ColanderFeed
from colander_data_converter.exporters.exporter import BaseExporter


class CsvExporter(BaseExporter):
    """
    A class to export entities from a ColanderFeed to CSV format.

    This exporter filters entities by type and exports their fields to a CSV file,
    excluding certain internal fields and object references.
    """

    excluded_fields: List[str] = ["colander_internal_type", "attributes"]
    """Fields to exclude from CSV export"""

    def __init__(self, feed: ColanderFeed, entity_type: type[BaseModel]):
        """
        Initialize the CSV exporter.

        Args:
            feed: The feed containing entities to export
            entity_type: The Pydantic model type to filter entities by

        Raises:
            AssertionError: If :py:obj:`entity_type` is not a subclass of :py:class:`pydantic.BaseModel` or
                :py:obj:`feed` is not a :py:class:`~colander_data_converter.base.models.ColanderFeed`.
        """
        assert issubclass(entity_type, BaseModel)
        assert isinstance(feed, ColanderFeed)

        self.feed = feed
        self.entity_type = entity_type
        self.entities: List[entity_type] = []
        self.fields: Set[str] = {"super_type"}
        self.feed.resolve_references()
        self._filter_entities()
        self._compute_field_list()

    def _filter_entities(self):
        """
        Filter entities from the feed to include only those matching the specified entity type.

        Populates the self.entities list with matching entities.
        """
        for _, entity in self.feed.entities.items():
            if isinstance(entity, self.entity_type):
                self.entities.append(entity)

    def _compute_field_list(self, exclude_none=True):
        """
        Compute the list of fields to include in the CSV export.

        This method performs a two-pass filtering process to determine which fields
        should be included in the CSV output:

        1. First pass: Identifies candidate fields by excluding internal fields and object references
        2. Second pass: Optionally excludes fields that are None for all entities

        Args:
            exclude_none: Whether to exclude fields that are None for all entities. Defaults to True.

        Returns:
            None: Updates :py:obj:`self.fields` in-place with the computed field list

        Side effects:
            - Modifies self.fields by adding qualifying field names
            - self.fields is sorted alphabetically after computation
            - 'super_type' is always included regardless of other filtering criteria

        Note:
            This method assumes self.entities has already been populated with filtered entities
            and self.entity_type contains the Pydantic model definition with field information.
        """
        candidate_fields = set()

        # First pass: collect all potential fields
        for field, info in self.entity_type.model_fields.items():
            if field in self.excluded_fields:
                continue
            annotation_args = get_args(info.annotation)
            if ObjectReference in annotation_args or List[ObjectReference] in annotation_args:
                continue
            candidate_fields.add(field)

        # Second pass: exclude fields that are None for all entities
        if exclude_none:
            for field in candidate_fields:
                has_non_none_value = False
                for entity in self.entities:
                    if hasattr(entity, field) and getattr(entity, field) is not None:
                        has_non_none_value = True
                        break  # Exit early if we find at least one non-None value

                if has_non_none_value:
                    self.fields.add(field)

        self.fields.add("super_type")
        self.fields = sorted(self.fields)

    def export(self, output: TextIO, **csv_options):
        """
        Export the filtered entities to a CSV file. The CSV includes a header row and one row per entity with the
        computed field values.

        Args:
            output: A file-like object to write the CSV to
            csv_options: Optional keyword arguments passed to :py:class:`csv.DictWriter`. Common options include:

                - quoting: csv.QUOTE_ALL, csv.QUOTE_MINIMAL, etc.
                - delimiter: Field delimiter
                - quotechar: Character used for quoting
                - lineterminator: Line terminator
                - extrasaction: How to handle extra fields

        Raises:
            AssertionError: If output is not a file-like object
        """
        assert output is not None

        # Set default CSV options if not provided
        csv_defaults = {"quoting": csv.QUOTE_ALL, "delimiter": ",", "quotechar": '"', "lineterminator": "\n"}

        # Merge user options with defaults (user options take precedence)
        writer_options = {**csv_defaults, **csv_options}

        objects: List[Dict] = []
        for e in self.entities:
            obj = e.model_dump(mode="json")
            obj["type"] = str(e.type)
            obj["super_type"] = str(e.super_type)
            objects.append({k: obj[k] for k in sorted(self.fields) if k not in self.excluded_fields})

        writer = csv.DictWriter(output, fieldnames=self.fields, **writer_options)
        writer.writeheader()
        writer.writerows(objects)
