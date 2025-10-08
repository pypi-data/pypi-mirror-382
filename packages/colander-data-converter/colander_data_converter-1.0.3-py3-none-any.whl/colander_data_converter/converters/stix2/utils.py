"""
Utility functions for STIX2 to Colander conversion and vice versa.
"""

import re
from typing import Dict, Any, Optional
from uuid import uuid4, UUID

from pydantic import UUID4

# Precompile the regex for performance
STIX2_PATTERN_REGEX = re.compile(r"[^=]+\s*=\s*(?:['\"]([^'\"]+)['\"]|([^\s]+))")


def extract_stix2_pattern_value(pattern: str) -> Optional[str]:
    """
    Extract the value from a STIX2 pattern.

    Handles various STIX2 pattern formats like:

    - :textmonoborder:`[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']`
    - :textmonoborder:`[domain-name:value = 'example.com']`
    - :textmonoborder:`[ipv4-addr:value = '192.168.1.1']`
    - :textmonoborder:`[url:value = 'https://example.com/malicious']`
    - :textmonoborder:`[process:pid = 1234]`
    - :textmonoborder:`[network-traffic:src_port = 443]`

    Args:
        pattern (str): The STIX2 pattern string to parse.

    Returns:
        Optional[str]: The extracted value, or None if no value could be extracted
        or if the pattern contains multiple criteria.
    """
    if not pattern or not isinstance(pattern, str):
        return None

    # Remove outer brackets and whitespace
    pattern = pattern.strip()
    if pattern.startswith("[") and pattern.endswith("]"):
        pattern = pattern[1:-1].strip()

    # Check for multiple criteria (AND, OR operators)
    if " AND " in pattern.upper() or " OR " in pattern.upper():
        return None

    # Match the pattern using the precompiled regex
    match = STIX2_PATTERN_REGEX.search(pattern)
    if match:
        return match.group(1) or match.group(2)

    return None


def extract_uuid_from_stix2_id(stix2_id: str) -> UUID:
    """
    Extract a UUID from a STIX2 ID.

    This function parses a STIX2 identifier string to extract the UUID portion.
    STIX2 IDs follow the format :textmonoborder:`{type}--{uuid}`, where the UUID is the part
    after the double dash delimiter.

    :param stix2_id: The STIX2 ID to extract the UUID from
    :type stix2_id: str
    :return: The extracted UUID, or a new UUID if extraction fails
    :rtype: UUID

    .. important::
        If the input format is invalid or UUID extraction fails, a new random
        UUID is generated and returned instead of raising an exception.

    Examples:
        >>> # Valid STIX2 ID with UUID
        >>> stix_id = "indicator--44af6c9f-4bbc-4984-a74b-1404d1ac07ea"
        >>> uuid_obj = extract_uuid_from_stix2_id(stix_id)
        >>> str(uuid_obj)
        '44af6c9f-4bbc-4984-a74b-1404d1ac07ea'

        >>> # Invalid STIX2 ID format (no delimiter)
        >>> stix_id = "indicator-invalid-format"
        >>> uuid_obj = extract_uuid_from_stix2_id(stix_id)
        >>> isinstance(uuid_obj, UUID)  # Returns a new random UUID
        True

        >>> # Invalid UUID part
        >>> stix_id = "indicator--not-a-valid-uuid"
        >>> uuid_obj = extract_uuid_from_stix2_id(stix_id)
        >>> isinstance(uuid_obj, UUID)  # Returns a new random UUID
        True
    """
    try:
        if stix2_id and "--" in stix2_id:
            # Extract the part after the "--" delimiter
            uuid_part = stix2_id.split("--", 1)[1]
            # Try to create a UUID from the extracted part
            return UUID4(uuid_part, version=4)
    except (ValueError, IndexError):
        # If anything goes wrong, return a new UUID
        pass

    return uuid4()


def extract_stix2_pattern_name(stix2_pattern: str) -> Optional[str]:
    """
    Extract the name from a STIX 2 pattern string.

    This function parses STIX2 pattern expressions to extract the field name
    portion before the equality operator. It removes brackets and extracts
    the left side of the comparison.

    :param stix2_pattern: The STIX 2 pattern string to extract the name from
    :type stix2_pattern: str
    :return: The extracted name or None if no name is found
    :rtype: Optional[str]

    .. note::
        The function handles various STIX2 pattern formats including nested
        hash references like :textmonoborder:`file:hashes.'SHA-256'`.

    Examples:
        >>> pattern = "[ipv4-addr:value = '192.168.1.1']"
        >>> extract_stix2_pattern_name(pattern)
        'ipv4-addr:value'

        >>> pattern = "[file:hashes.'SHA-256' = '123abc']"
        >>> extract_stix2_pattern_name(pattern)
        "file:hashes.'SHA-256'"
    """
    _to_replace = [
        ("[", ""),
        ("]", ""),
    ]
    if "=" not in stix2_pattern:
        return ""
    _stix2_pattern = stix2_pattern
    for _replace in _to_replace:
        _stix2_pattern = _stix2_pattern.replace(_replace[0], _replace[1])
    return _stix2_pattern.split("=")[0].strip()


def get_nested_value(obj: Dict[str, Any], path: str) -> Any:
    """
    Get a value from a nested dictionary using a dot-separated path.

    This function safely navigates through nested dictionaries using a
    dot-separated path string. It returns the value at the specified path
    or None if any part of the path is missing or invalid.

    :param obj: The dictionary to get the value from
    :type obj: Dict[str, Any]
    :param path: The dot-separated path to the value
    :type path: str
    :return: The value at the specified path, or None if not found
    :rtype: Any

    .. warning::
        This function returns None for missing paths rather than raising
        exceptions. Check for None return values when path existence is critical.

    Examples:
        >>> data = {
        ...     "user": {
        ...         "profile": {
        ...             "name": "John",
        ...             "age": 30
        ...         },
        ...         "settings": {
        ...             "theme": "dark"
        ...         }
        ...     }
        ... }
        >>> get_nested_value(data, "user.profile.name")
        'John'
        >>> get_nested_value(data, "user.settings.theme")
        'dark'
    """
    if not path:
        return None

    parts = path.split(".")
    current = obj

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None

    return current


def set_nested_value(obj: Dict[str, Any], path: str, value: Any) -> None:
    """
    Set a value in a nested dictionary using a dot-separated path.

    This function creates nested dictionaries as needed to set a value at
    the specified dot-separated path. If intermediate dictionaries don't
    exist, they are automatically created.

    :param obj: The dictionary to set the value in
    :type obj: Dict[str, Any]
    :param path: The dot-separated path to the value
    :type path: str
    :param value: The value to set
    :type value: Any

    .. note::
        The function modifies the input dictionary in-place and automatically
        creates any missing intermediate dictionary levels.

    Examples:
        >>> data = {}
        >>> set_nested_value(data, "user.profile.name", "John")
        >>> data
        {'user': {'profile': {'name': 'John'}}}

        >>> # Update existing nested value
        >>> data = {'user': {'settings': {'theme': 'light'}}}
        >>> set_nested_value(data, "user.settings.theme", "dark")
        >>> data
        {'user': {'settings': {'theme': 'dark'}}}

        >>> # Add new nested path to existing structure
        >>> set_nested_value(data, "user.profile.age", 30)
        >>> data
        {'user': {'settings': {'theme': 'dark'}, 'profile': {'age': 30}}}

        >>> # Empty path does nothing
        >>> original = {'a': 1}
        >>> set_nested_value(original, "", "value")
        >>> original
        {'a': 1}
    """
    if not path:
        return

    parts = path.split(".")
    current = obj

    # Navigate to the parent of the final part
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    # Set the value at the final part
    current[parts[-1]] = value
