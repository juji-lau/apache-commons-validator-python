import pytest

from src.main.validator_action_new import ValidatorAction
from src.main.field_new import Field
from src.main.form_new import Form
from src.main.form_set_new import FormSet
from src.main.validator_resources_new import ValidatorResources
from src.main.validator_new import Validator


def test_required_field_validation():
    # 1. Register ValidatorAction
    action = ValidatorAction()
    action.name = "required"
    action.class_name = "src.test.resources.required_validator.RequiredValidator"
    action.method = "validate_required"

    # 2. Create Field
    field = Field()
    field.field_property = "username"
    field.depends = "required"

    # 3. Create Form
    form = Form()
    form.name = "userForm"
    form.add_field(field)

    # 4. Create ValidatorResources
    resources = ValidatorResources()
    resources.add_validator_action(action)

    form_set = FormSet()
    form_set.language = "en"
    form_set.add_form(form)
    resources.add_form_set(form_set)

    # 5. Run Validator with invalid input
    validator = Validator(resources, "userForm", parameters={"username": "   "})
    validator.set_locale("en")
    result = validator.get_result()

    validator_result = result.get_validator_result("username")
    assert validator_result is not None
    assert validator_result.contains_action("required")
    assert not validator_result.is_valid("required")

    # 6. Run Validator with valid input
    validator = Validator(resources, "userForm", parameters={"username": "alice"})
    validator.set_locale("en")
    result = validator.get_result()

    validator_result = result.get_validator_result("username")
    assert validator_result is not None
    assert validator_result.contains_action("required")
    assert validator_result.is_valid("required")
