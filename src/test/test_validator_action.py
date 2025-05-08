import pytest
from src.main.validator_action import ValidatorAction

# ============================= Mocks ================================ #
class MockValidator:
    @staticmethod
    def validate(validator, params):
        return bool(params.get("field_value"))

# ============================= Unit Tests ============================ #

def test_validator_action_init(monkeypatch):
    """Test dynamic loading with init()."""

    import types

    def mock_import_module(name):
        module = types.SimpleNamespace()
        module.MockValidator = MockValidator
        return module

    monkeypatch.setattr("importlib.import_module", mock_import_module)

    action = ValidatorAction()
    action.name = "required"
    action.class_name = "mock.module.MockValidator"
    action.method = "validate"

    action.init()

    assert action._ValidatorAction__validator_class == MockValidator

def test_validator_action_execute(monkeypatch):
    """Test executing the validator logic."""

    # Setup
    import types

    def mock_import_module(name):
        module = types.SimpleNamespace()
        module.MockValidator = MockValidator
        return module

    monkeypatch.setattr("importlib.import_module", mock_import_module)

    action = ValidatorAction()
    action.name = "required"
    action.class_name = "mock.module.MockValidator"
    action.method = "validate"
    action.init()

    # Should pass with non-empty value
    result = action.execute_validation_method(None, {"field_value": "test"})
    assert result is True

    # Should fail with empty value
    result = action.execute_validation_method(None, {"field_value": ""})
    assert result is False

def test_validator_action_dependencies():
    """Test dependency parsing."""
    action = ValidatorAction()
    action.depends = "required,email, minLength"
    deps = action.get_dependencies()
    assert deps == ["required", "email", "minLength"]

def test_validator_action_set_js_function():
    """Test setting and getting JS function."""
    action = ValidatorAction()
    action.setJavascript("function validate() {}")
    assert action.getJavascript() == "function validate() {}"

# ============================= Integration Tests ============================ #
class RequiredValidator:
    @staticmethod
    def validate(validator, params):
        return bool(params.get("field_value"))

def test_validator_action_full_integration():
    """Full integration: Digester -> ValidatorResources -> ValidatorAction.execute."""

    from src.main.validator_resources import ValidatorResources
    from src.main.util.digester import Digester
    import io

    # Step 1: Setup ValidatorResources and Digester
    resources = ValidatorResources()
    digester = Digester(root_object=resources)
    digester.load_rules("src/resources/digester-rules.xml")  # Adjust if needed

    # Step 2: Parse a minimal XML with a <validator>
    validation_xml = io.StringIO(
        """<?xml version="1.0"?>
        <form-validation>
            <validator name="required" classname="src.test.test_validator_action.RequiredValidator" method="validate">
                <javascript/>
            </validator>
        </form-validation>
        """
    )
    digester.parse(validation_xml)

    # Step 3: Get the ValidatorAction
    action = resources.get_validator_action("required")

    # Step 4: Execute the action
    params = {"field_value": "some_value"}
    result = action.execute_validation_method(None, params)

    # Step 5: Check
    assert result is True
    assert action.name == "required"
    assert action.class_name == "src.test.test_validator_action.RequiredValidator"
    assert action.method == "validate"