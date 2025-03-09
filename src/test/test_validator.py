import pytest
import src
from src.main.Validator import Validator
from src.main.ValidatorException import ValidatorException
from src.main.ValidatorResults import ValidatorResults
from src.main.ValidatorResources import ValidatorResources

class TestBean:
    def __init__(self):
        self.letter = None
        self.date = None
    
    def get_date(self):
        return self.date
    
    def get_letter(self):
        return self.letter
    
    def set_date(self, date):
        self.date = date
    
    def set_letter(self, letter):
        self.letter = letter

def format_date(bean, field):
    """Formats a string to a date. Returns None if validation fails."""
    value = getattr(bean, field.property, None)
    if not value:
        return None
    try:
        from datetime import datetime
        return datetime.strptime(value, "%m/%d/%Y")
    except ValueError:
        return None

def is_cap_letter(bean, field, errors):
    """Checks if the field is one upper-case letter between 'A' and 'Z'."""
    value = getattr(bean, field.property, None)
    if not value or len(value) != 1 or not ('A' <= value <= 'Z'):
        errors.append("Error")
        return False
    return True

def test_manual_boolean():
    resources = ValidatorResources()
    bean = TestBean()
    bean.set_letter("A")
    
    validator = Validator(resources, "testForm")
    validator.set_parameter(Validator.BEAN_PARAM, bean)
    validator.set_parameter("java.util.List", [])
    
    try:
        validator.validate()
    except Exception:
        pytest.fail("Validator.validate() raised an exception unexpectedly!")

def test_manual_object():
    resources = ValidatorResources()
    bean = TestBean()
    bean.set_date("2/3/1999")
    
    validator = Validator(resources, "testForm")
    validator.set_parameter(Validator.BEAN_PARAM, bean)
    
    try:
        results = validator.validate()
        assert results is not None
        result = results.get_validator_result("date")
        assert result is not None
        assert result.contains_action("date")
        assert result.is_valid("date")
    except Exception:
        pytest.fail("Validator.validate() raised an exception unexpectedly!")

def test_only_return_errors():
    resources = ValidatorResources()
    bean = TestBean()
    bean.set_date("2/3/1999")
    
    validator = Validator(resources, "testForm")
    validator.set_parameter(Validator.BEAN_PARAM, bean)
    
    results = validator.validate()
    assert results is not None
    assert "date" in results.property_names
    
    validator.set_only_return_errors(True)
    results = validator.validate()
    assert "date" not in results.property_names

def test_only_validate_field():
    resources = ValidatorResources()
    bean = TestBean()
    bean.set_date("2/3/1999")
    
    validator = Validator(resources, "testForm", "date")
    validator.set_parameter(Validator.BEAN_PARAM, bean)
    
    results = validator.validate()
    assert results is not None
    assert "date" in results.property_names