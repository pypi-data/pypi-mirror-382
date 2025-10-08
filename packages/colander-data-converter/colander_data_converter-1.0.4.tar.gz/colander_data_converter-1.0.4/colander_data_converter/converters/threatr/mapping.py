import json
from importlib import resources
from typing import Dict, Any, List

from colander_data_converter.base.models import ColanderRepository
from colander_data_converter.converters.threatr.models import ThreatrRepository

resource_package = __name__


class ThreatrMappingLoader:
    """
    Loads and provides access to the Threatr to Colander mapping data.

    This class is responsible for loading the mapping configuration from a JSON file
    that defines how Threatr entities, events, and relations should be converted to
    their Colander equivalents. The mapping data includes field mappings, type
    conversions, and relationship definitions.

    Note:
        The mapping data is loaded once during initialization and cached for
        subsequent use.

    Attributes:
        mapping_data: The loaded mapping data

    Example:
        >>> loader = ThreatrMappingLoader()
        >>> mappings = loader.mapping_data
        >>> isinstance(mappings, list)
        True
    """

    def __init__(self):
        """
        Initialize the mapping loader and load the mapping data.

        Raises:
            ValueError: If the mapping file cannot be found or parsed
        """
        self.mapping_data = self._load_mapping_data()

    @staticmethod
    def _load_mapping_data() -> List[Dict[str, Any]]:
        """
        Load the mapping data from the JSON file.

        This method reads the mapping configuration from the JSON file located at
        ``data/threatr_colander_mapping.json`` relative to this module's package.

        Returns:
            The mapping data loaded from the JSON file

        Raises:
            ValueError: If the file cannot be found or contains invalid JSON
            FileNotFoundError: If the mapping file does not exist
            ~json.JSONDecodeError: If the mapping file contains malformed JSON

        Important:
            The JSON file must contain a root object with a "mapping" key that holds
            an array of mapping definitions.
        """
        json_file = resources.files(resource_package).joinpath("data").joinpath("threatr_colander_mapping.json")
        try:
            with json_file.open() as f:
                return json.load(f).get("mapping")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to load mapping data: {e}")


class ThreatrMapper:
    """
    Base class for mapping between Threatr and Colander data using the mapping file.

    This abstract base class provides common functionality for all Threatr to Colander
    mappers. It initializes the mapping loader and provides access to the mapping
    data that defines how different data formats should be converted between the
    two systems.

    Attributes:
        mapping_loader: Instance of ThreatrMappingLoader for accessing mapping data

    Note:
        This is a base class that should be subclassed by specific mapper
        implementations. The mapping data is loaded once and shared across
        all mapper instances.

    Example:
        >>> class CustomMapper(ThreatrMapper):
        ...     def __init__(self):
        ...         super().__init__()
        ...
        >>> mapper = CustomMapper()
        >>> hasattr(mapper, 'mapping_loader')
        True
    """

    def __init__(self):
        """
        Initialize the mapper with the mapping loader.

        Creates an instance of ThreatrMappingLoader to provide access to the
        mapping configuration data. This data will be used by subclasses to
        perform the actual conversion between Threatr and Colander formats.
        """
        self.mapping_loader = ThreatrMappingLoader()
        ColanderRepository().clear()
        ThreatrRepository().clear()
