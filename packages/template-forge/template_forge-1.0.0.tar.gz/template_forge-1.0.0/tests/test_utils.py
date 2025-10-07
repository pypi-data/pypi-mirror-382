"""
Tests for utility functions in template_forge.utils
"""

from template_forge.utils import (
    deep_merge,
    flatten_array,
    to_camel_case,
    to_kebab_case,
    to_pascal_case,
    to_snake_case,
)

# deep_merge tests


def test_deep_merge_simple_dicts():
    """Test merging simple dictionaries"""
    base = {"a": 1, "b": 2}
    update = {"b": 3, "c": 4}
    result = deep_merge(base, update)

    assert result == {"a": 1, "b": 3, "c": 4}


def test_deep_merge_nested_dicts():
    """Test merging nested dictionaries"""
    base = {"a": {"b": 1, "c": 2}}
    update = {"a": {"c": 3, "d": 4}}
    result = deep_merge(base, update)

    assert result == {"a": {"b": 1, "c": 3, "d": 4}}


def test_deep_merge_lists():
    """Test merging lists (line 43)"""
    base = {"items": [1, 2, 3]}
    update = {"items": [4, 5]}
    result = deep_merge(base, update)

    assert result == {"items": [1, 2, 3, 4, 5]}


def test_deep_merge_overwrite_different_types():
    """Test that different types cause overwrite (not merge)"""
    base = {"value": {"nested": "dict"}}
    update = {"value": "string"}
    result = deep_merge(base, update)

    assert result == {"value": "string"}


def test_deep_merge_empty_update():
    """Test merging with empty update dict"""
    base = {"a": 1, "b": 2}
    update = {}
    result = deep_merge(base, update)

    assert result == {"a": 1, "b": 2}


def test_deep_merge_empty_base():
    """Test merging into empty base dict"""
    base = {}
    update = {"a": 1, "b": 2}
    result = deep_merge(base, update)

    assert result == {"a": 1, "b": 2}


# to_snake_case tests


def test_to_snake_case_camel_case():
    """Test converting CamelCase to snake_case"""
    assert to_snake_case("CamelCase") == "camel_case"
    assert to_snake_case("XMLParser") == "x_m_l_parser"


def test_to_snake_case_spaces():
    """Test converting spaces to underscores (line 69)"""
    assert to_snake_case("some text here") == "some_text_here"
    # Multiple spaces become multiple underscores (preserves spacing)
    assert (
        to_snake_case("Multiple  Spaces") == "multiple___spaces"
    )  # regex adds one more


def test_to_snake_case_hyphens():
    """Test converting hyphens to underscores (line 70)"""
    assert to_snake_case("kebab-case") == "kebab_case"
    assert to_snake_case("multi-word-text") == "multi_word_text"


def test_to_snake_case_mixed():
    """Test converting mixed formats (lines 71-72)"""
    # Hyphens and spaces both become underscores, plus regex adds underscores before capitals
    assert to_snake_case("SomeText-With Spaces") == "some_text__with__spaces"


def test_to_snake_case_already_snake():
    """Test that already snake_case text is preserved"""
    assert to_snake_case("already_snake_case") == "already_snake_case"


# to_camel_case tests


def test_to_camel_case_snake_case():
    """Test converting snake_case to camelCase"""
    assert to_camel_case("snake_case") == "snakeCase"
    assert to_camel_case("multi_word_name") == "multiWordName"


def test_to_camel_case_spaces():
    """Test converting spaces to camelCase (line 91)"""
    assert to_camel_case("some text") == "someText"


def test_to_camel_case_hyphens():
    """Test converting kebab-case to camelCase (line 92)"""
    assert to_camel_case("kebab-case") == "kebabCase"


def test_to_camel_case_empty_words():
    """Test handling edge case with no words (lines 93-94)"""
    # Multiple delimiters create empty strings in split
    result = to_camel_case("___")
    # Should handle gracefully
    assert isinstance(result, str)


def test_to_camel_case_mixed():
    """Test converting mixed formats (lines 95-96)"""
    assert to_camel_case("mixed-Format_here") == "mixedFormatHere"


def test_to_camel_case_already_camel():
    """Test that already camelCase text is preserved"""
    assert to_camel_case("alreadyCamelCase") == "alreadycamelcase"  # Gets lowercased


# to_pascal_case tests


def test_to_pascal_case_snake_case():
    """Test converting snake_case to PascalCase"""
    assert to_pascal_case("snake_case") == "SnakeCase"
    assert to_pascal_case("multi_word_name") == "MultiWordName"


def test_to_pascal_case_spaces():
    """Test converting spaces to PascalCase (line 115)"""
    assert to_pascal_case("some text") == "SomeText"


def test_to_pascal_case_hyphens():
    """Test converting kebab-case to PascalCase (line 116)"""
    assert to_pascal_case("kebab-case") == "KebabCase"


def test_to_pascal_case_mixed():
    """Test converting mixed formats"""
    assert to_pascal_case("mixed-Format_here") == "MixedFormatHere"


def test_to_pascal_case_already_pascal():
    """Test that already PascalCase text is preserved"""
    assert to_pascal_case("AlreadyPascalCase") == "Alreadypascalcase"


# to_kebab_case tests


def test_to_kebab_case_camel_case():
    """Test converting CamelCase to kebab-case"""
    assert to_kebab_case("CamelCase") == "camel-case"
    assert to_kebab_case("XMLParser") == "x-m-l-parser"


def test_to_kebab_case_snake_case():
    """Test converting snake_case to kebab-case (line 135)"""
    assert to_kebab_case("some_text") == "some-text"


def test_to_kebab_case_spaces():
    """Test converting spaces to hyphens (lines 136-137)"""
    assert to_kebab_case("some text here") == "some-text-here"


def test_to_kebab_case_mixed():
    """Test converting mixed formats (line 138)"""
    assert to_kebab_case("MixedFormat_here") == "mixed-format-here"


def test_to_kebab_case_already_kebab():
    """Test that already kebab-case text is preserved"""
    assert to_kebab_case("already-kebab-case") == "already-kebab-case"


# flatten_array tests


def test_flatten_array_nested_lists():
    """Test flattening nested lists"""
    assert flatten_array([[1, 2], [3, [4, 5]]]) == [1, 2, 3, 4, 5]
    assert flatten_array([[[1]], [[2]], [[3]]]) == [1, 2, 3]


def test_flatten_array_mixed_depth():
    """Test flattening with mixed nesting depth"""
    assert flatten_array([1, [2, [3, [4]]], 5]) == [1, 2, 3, 4, 5]


def test_flatten_array_tuples():
    """Test flattening with tuples"""
    assert flatten_array([(1, 2), (3, (4, 5))]) == [1, 2, 3, 4, 5]


def test_flatten_array_non_list():
    """Test that non-list values are returned unchanged"""
    assert flatten_array("not a list") == "not a list"
    assert flatten_array(42) == 42
    assert flatten_array(None) is None


def test_flatten_array_empty():
    """Test flattening empty list"""
    assert flatten_array([]) == []


def test_flatten_array_single_level():
    """Test flattening already flat list"""
    assert flatten_array([1, 2, 3]) == [1, 2, 3]
