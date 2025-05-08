import pytest
from src.main.validator import Validator
from src.main.validator_results import ValidatorResults
from src.main.validator_exception import ValidatorException
from src.main.validator_resources import ValidatorResources
from src.main.form import Form
from src.main.field import Field
from src.main.validator_action import ValidatorAction
from src.main.validator_result import ValidatorResult


class DummyValidator:
    def validate(self, field, params, results, pos):
        result = ValidatorResult(field)
        result.add("required", True, "ok")
        results[field.key] = result
        return True


@pytest.fixture
def validator_resources_with_form():
    resources = ValidatorResources()

    # Create form, field, and action
    form = Form()
    field = Field()
    field.field_property = "username"
    field.depends = "required"

    action = ValidatorAction()
    action.name = "required"
    action.method = "validate"
    action._ValidatorAction__validator_class = DummyValidator

    form.add_field(field)

    # Patch internal structures directly
    locale_key = resources.__build_locale_key("en", "US", None, "testForm")
    resources._forms[locale_key] = form
    resources._validator_actions["required"] = action

    return resources


def test_get_result_success(validator_resources_with_form):
    validator = Validator(validator_resources_with_form, "testForm", {
        "java.lang.Object": {"username": "value"}
    })

    result = validator.get_result()
    assert isinstance(result, ValidatorResults)
    assert result.get_validator_result("username").is_valid("required")


def test_get_result_raises_exception_if_form_missing():
    resources = ValidatorResources()
    validator = Validator(resources, "missingForm")

    with pytest.raises(ValidatorException) as exc_info:
        validator.get_result()

    assert "Form 'missingForm' not found" in str(exc_info.value)


def test_validate_field_specific(validator_resources_with_form):
    validator = Validator(validator_resources_with_form, "testForm", {
        "java.lang.Object": {"username": "value"}
    })

    result = validator.validate_field("username")
    assert isinstance(result, ValidatorResults)
    assert result.get_validator_result("username").is_valid("required")


def test_set_and_get_parameter(validator_resources_with_form):
    validator = Validator(validator_resources_with_form, "testForm")
    validator.set_parameter("key", 123)
    assert validator.get_parameter("key") == 123


def test_locale_affects_form_resolution(validator_resources_with_form):
    validator = Validator(validator_resources_with_form, "testForm")
    validator.set_locale("en", "US")
    result = validator.get_result()
    assert isinstance(result, ValidatorResults)


def test_set_page_and_error_flag(validator_resources_with_form):
    validator = Validator(validator_resources_with_form, "testForm")
    validator.set_page(1)
    validator.set_only_return_errors(True)

    assert validator._page == 1
    assert validator._only_return_errors is True