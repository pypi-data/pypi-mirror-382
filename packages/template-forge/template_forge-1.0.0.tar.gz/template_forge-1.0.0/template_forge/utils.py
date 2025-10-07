#!/usr/bin/env python3
"""Utility functions for Template Forge.

This module contains common helper functions used across the template forge codebase,
including dict merging, transformations, and helper utilities.
"""

import re
from typing import Any, Dict


def deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries.

    For nested dictionaries, recursively merges keys.
    For lists, appends items.
    For other values, update overwrites base.

    Args:
        base: Base dictionary
        update: Dictionary with updates to merge in

    Returns:
        Merged dictionary

    Example:
        >>> base = {"a": {"b": 1, "c": 2}}
        >>> update = {"a": {"c": 3, "d": 4}}
        >>> deep_merge(base, update)
        {'a': {'b': 1, 'c': 3, 'd': 4}}
    """
    result = base.copy()

    for key, value in update.items():
        if key in result:
            base_value = result[key]

            # If both are dicts, recursively merge
            if isinstance(base_value, dict) and isinstance(value, dict):
                result[key] = deep_merge(base_value, value)
            # If both are lists, append
            elif isinstance(base_value, list) and isinstance(value, list):
                result[key] = base_value + value
            # Otherwise, update overwrites
            else:
                result[key] = value
        else:
            result[key] = value

    return result


def to_snake_case(text: str) -> str:
    """Convert text to snake_case.

    Args:
        text: Text to convert

    Returns:
        Text in snake_case format

    Example:
        >>> to_snake_case("CamelCase")
        'camel_case'
        >>> to_snake_case("some text here")
        'some_text_here'
    """
    # Replace spaces and hyphens with underscores
    text = text.replace(" ", "_").replace("-", "_")
    # Insert underscore before uppercase letters
    text = re.sub(r"(?<!^)(?=[A-Z])", "_", text)
    return text.lower()


def to_camel_case(text: str) -> str:
    """Convert text to camelCase.

    Args:
        text: Text to convert

    Returns:
        Text in camelCase format

    Example:
        >>> to_camel_case("snake_case")
        'snakeCase'
        >>> to_camel_case("some text")
        'someText'
    """
    # Split on spaces, underscores, hyphens
    words = re.split(r"[_\s-]+", text)
    if not words:
        return text

    # First word lowercase, rest capitalized
    return words[0].lower() + "".join(word.capitalize() for word in words[1:])


def to_pascal_case(text: str) -> str:
    """Convert text to PascalCase.

    Args:
        text: Text to convert

    Returns:
        Text in PascalCase format

    Example:
        >>> to_pascal_case("snake_case")
        'SnakeCase'
        >>> to_pascal_case("some text")
        'SomeText'
    """
    # Split on spaces, underscores, hyphens
    words = re.split(r"[_\s-]+", text)
    return "".join(word.capitalize() for word in words)


def to_kebab_case(text: str) -> str:
    """Convert text to kebab-case.

    Args:
        text: Text to convert

    Returns:
        Text in kebab-case format

    Example:
        >>> to_kebab_case("CamelCase")
        'camel-case'
        >>> to_kebab_case("some_text")
        'some-text'
    """
    # Replace spaces and underscores with hyphens
    text = text.replace(" ", "-").replace("_", "-")
    # Insert hyphen before uppercase letters
    text = re.sub(r"(?<!^)(?=[A-Z])", "-", text)
    return text.lower()


def flatten_array(value: Any) -> Any:
    """Recursively flatten nested arrays/lists.

    Args:
        value: Value to flatten (can be nested lists/tuples)

    Returns:
        Flattened list if value was a list/tuple, otherwise unchanged

    Example:
        >>> flatten_array([[1, 2], [3, [4, 5]]])
        [1, 2, 3, 4, 5]
        >>> flatten_array("not a list")
        'not a list'
    """
    if not isinstance(value, (list, tuple)):
        return value

    result = []
    for item in value:
        if isinstance(item, (list, tuple)):
            result.extend(flatten_array(item))
        else:
            result.append(item)

    return result
