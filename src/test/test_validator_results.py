import pytest
from types import MappingProxyType

from src.main.validator_results import ValidatorResults
from src.main.field import Field

@pytest.fixture
def sample_field():
    field = Field()
    field.field_property = "email"
    field.key = "email"
    return field


def test_add_and_get_validator_result(sample_field):
    results = ValidatorResults()
    results.add(sample_field, "required", True, "value ok")

    result = results.get_validator_result("email")
    assert result is not None
    assert result.contains_action("required")
    assert result.is_valid("required") is True
    assert result.get_result("required") == "value ok"


def test_get_property_names(sample_field):
    results = ValidatorResults()
    results.add(sample_field, "required", True)
    property_names = results.get_property_names()

    assert "email" in property_names
    assert isinstance(property_names, set)


def test_get_result_value_map(sample_field):
    results = ValidatorResults()
    results.add(sample_field, "required", True, "foo")
    results.add(sample_field, "length", False, "too short")

    result_map = results.get_result_value_map()
    assert result_map["email.required"] == "foo"
    assert result_map["email.length"] == "too short"


def test_is_empty_and_clear(sample_field):
    results = ValidatorResults()
    assert results.is_empty()

    results.add(sample_field, "required", True)
    assert not results.is_empty()

    results.clear()
    assert results.is_empty()


def test_merge_results(sample_field):
    results1 = ValidatorResults()
    results1.add(sample_field, "required", True, "ok")

    results2 = ValidatorResults()
    results2.add(sample_field, "length", False, "too short")

    results1.merge(results2)
    result = results1.get_validator_result("email")

    assert result.contains_action("required")
    assert result.contains_action("length")
    assert result.get_result("length") == "too short"
    assert result.is_valid("length") is False


def test_get_action_map(sample_field):
    results = ValidatorResults()
    results.add(sample_field, "required", True)

    action_map = results.get_action_map("email")
    assert isinstance(action_map, MappingProxyType)
    assert "required" in action_map
    with pytest.raises(TypeError):
        action_map["new"] = "value"  # Should raise because it's immutable