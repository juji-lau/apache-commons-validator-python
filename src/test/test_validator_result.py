import pytest
from src.main.validator_result_new import ValidatorResult

def test_add_and_get_result():
    result = ValidatorResult(field="testField")
    result.add("required", True, "value passed")

    assert result.contains_action("required")
    assert result.get_result("required") == "value passed"
    assert result.is_valid("required") is True

def test_add_failure():
    result = ValidatorResult(field="age")
    result.add("intRange", False, "Too low")

    assert result.contains_action("intRange")
    assert result.get_result("intRange") == "Too low"
    assert result.is_valid("intRange") is False

def test_get_result_missing():
    result = ValidatorResult(field="missingField")
    assert result.get_result("nonexistent") is None
    assert result.is_valid("nonexistent") is False
    assert result.contains_action("nonexistent") is False

def test_get_actions_iterator():
    result = ValidatorResult(field="testField")
    result.add("required", True)
    result.add("email", True)

    actions = list(result.get_actions())
    assert "required" in actions
    assert "email" in actions
    assert len(actions) == 2

def test_get_action_map_immutable():
    result = ValidatorResult(field="testField")
    result.add("required", True)
    action_map = result.get_action_map()

    assert "required" in action_map
    with pytest.raises(TypeError):
        action_map["new"] = "fail"  # Should raise because MappingProxyType is immutable