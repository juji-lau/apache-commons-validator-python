import pytest
from io import StringIO
from src.main.validator_resources import ValidatorResources

@pytest.fixture
def valid_xml():
    return """
    <form-validation>
        <formset>
            <form name="testForm">
                <field property="testField" depends="required"/>
            </form>
        </formset>
    </form-validation>
    """

def test_validator_resources_initialize_with_stream(valid_xml):
    xml_stream = StringIO(valid_xml)
    resources = ValidatorResources(sources=xml_stream)
    assert resources is not None
    assert resources._get_form_sets()

def test_validator_resources_initialize_with_file_path(tmp_path, valid_xml):
    file_path = tmp_path / "test_validation.xml"
    file_path.write_text(valid_xml)
    resources = ValidatorResources(sources=str(file_path))
    assert resources is not None
    assert resources._get_form_sets()

def test_validator_resources_invalid_source_type():
    with pytest.raises(ValueError):
        ValidatorResources(sources=1234)

def test_validator_resources_add_constant():
    resources = ValidatorResources()
    resources.add_constant("testKey", "testValue")
    assert resources._get_constants()["testKey"] == "testValue"

def test_validator_resources_add_form_set():
    from unittest.mock import MagicMock
    resources = ValidatorResources()
    form_set = MagicMock()
    form_set.language = "en"
    form_set.country = "US"
    form_set.variant = None
    resources.add_form_set(form_set)
    key = resources.build_locale("en", "US", None)
    assert key in resources._get_form_sets()

def test_validator_resources_get_validator_action():
    from unittest.mock import MagicMock
    resources = ValidatorResources()
    action = MagicMock()
    action.name = "testAction"
    action.class_name = "TestClass"
    resources.add_validator_action(action)
    assert resources.get_validator_action("testAction") == action

def test_validator_resources_build_locale():
    resources = ValidatorResources()
    assert resources.build_locale("en", "US", "variant") == "en_US_variant"
    assert resources.build_locale("en", None, None) == "en"

def test_validator_resources_get_validator_actions():
    from unittest.mock import MagicMock
    resources = ValidatorResources()
    action = MagicMock()
    action.name = "action1"
    action.class_name = "Class1"
    resources.add_validator_action(action)
    actions = resources.get_validator_actions()
    assert "action1" in actions


def test_validator_resources_process(mocker):
    resources = ValidatorResources()
    mock_form_set = mocker.Mock()
    resources._h_form_sets = {"key": mock_form_set}
    resources._default_form_set = mocker.Mock()
    resources.process()
    resources._default_form_set.process.assert_called_once()
    mock_form_set.process.assert_called_once()

def test_validator_resources_get_form_with_locale_language_country_variant():
    from unittest.mock import MagicMock
    resources = ValidatorResources()

    form_set_variant = MagicMock()
    form_variant = MagicMock()
    form_set_variant.get_form.return_value = form_variant
    resources._get_form_sets()["en_US_variant"] = form_set_variant

    retrieved_form = resources._get_form_with_locale("en", "US", "variant", "testForm")
    assert retrieved_form == form_variant
    form_set_variant.get_form.assert_called_once_with("testForm")

def test_validator_resources_get_form_with_locale_language_country():
    from unittest.mock import MagicMock
    resources = ValidatorResources()

    form_set_country = MagicMock()
    form_country = MagicMock()
    form_set_country.get_form.return_value = form_country
    resources._get_form_sets()["en_US"] = form_set_country

    retrieved_form = resources._get_form_with_locale("en", "US", "nothing", "testForm")
    assert retrieved_form == form_country
    form_set_country.get_form.assert_called_once_with("testForm")

def test_validator_resources_get_form_with_locale_language():
    from unittest.mock import MagicMock
    resources = ValidatorResources()

    form_set_language = MagicMock()
    form_language = MagicMock()
    form_set_language.get_form.return_value = form_language
    resources._get_form_sets()["en"] = form_set_language

    retrieved_form = resources._get_form_with_locale("en", None, "something", "testForm")
    assert retrieved_form == form_language
    form_set_language.get_form.assert_called_once_with("testForm")

def test_validator_resources_get_form_with_locale_default():
    from unittest.mock import MagicMock
    resources = ValidatorResources()

    form_default = MagicMock()
    resources._default_form_set = MagicMock()
    resources._default_form_set.get_form.return_value = form_default

    retrieved_form = resources._get_form_with_locale(None, None, None, "testForm")
    assert retrieved_form == form_default
    resources._default_form_set.get_form.assert_called_once_with("testForm")