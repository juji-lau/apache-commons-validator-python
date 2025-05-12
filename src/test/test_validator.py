# test_validator_api.py

import pytest

from src.main.validator import Validator
from src.main.validator_action import ValidatorAction
from src.main.validator_resources import ValidatorResources
from src.main.form import Form
from src.main.field import Field
from src.main.form_set import FormSet
from src.main.validator_exception import ValidatorException

def build_resources_with_field(name="email", depends="always", page=1):
    # ValidatorAction
    action = ValidatorAction()
    action.name = "always"
    action.class_name = "src.test.resources.always_pass_validator.AlwaysPassValidator"
    action.method = "validate_always_pass"

    # Field
    field = Field()
    field.field_property = name
    field.depends = depends
    field.page = page

    # Form
    form = Form()
    form.name = "profileForm"
    form.add_field(field)

    # Resources
    resources = ValidatorResources()
    resources.add_validator_action(action)

    form_set = FormSet()
    form_set.language = "en"
    form_set.add_form(form)
    resources.add_form_set(form_set)

    return resources


def test_validate_field_within_page():
    resources = build_resources_with_field(page=0)

    validator = Validator(resources, "profileForm", {"email": "test@example.com"})
    validator.set_locale("en")
    validator.set_page(0)

    results = validator.validate_field("email")
    assert results.get_validator_result("email").is_valid("always")


def test_validate_field_outside_page_is_skipped():
    resources = build_resources_with_field(page=2)  # Field is on page 2

    validator = Validator(resources, "profileForm", {"email": "test@example.com"})
    validator.set_locale("en")
    validator.set_page(0)  # Validator is set to page 0

    results = validator.validate_field("email")
    assert results.get_validator_result("email") is None  # Should be skipped


def test_get_and_set_parameter():
    resources = build_resources_with_field()
    validator = Validator(resources, "profileForm")
    validator.set_parameter("foo", 123)
    assert validator.get_parameter("foo") == 123


def test_missing_form_raises_exception():
    resources = ValidatorResources()  # No form added

    validator = Validator(resources, "nonexistentForm")
    validator.set_locale("en")

    with pytest.raises(ValidatorException) as excinfo:
        validator.get_result()
    assert "nonexistentForm" in str(excinfo.value)


def test_validate_field_not_found():
    resources = build_resources_with_field(name="real_field")

    validator = Validator(resources, "profileForm")
    validator.set_locale("en")

    with pytest.raises(ValidatorException) as excinfo:
        validator.validate_field("fake_field")
    assert "fake_field" in str(excinfo.value)
