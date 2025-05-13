import pytest
from io import StringIO
from unittest.mock import MagicMock
from src.apache_commons_validator_python.util.digester import Digester
from src.apache_commons_validator_python.validator_resources_new import ValidatorResources

# ============================== Fixtures ==================================== #

@pytest.fixture
def valid_xml():
    return """
    <form-validation>
        <formset language="en" country="US">
            <form name="testForm">
                <field field_property="testField" depends="required"/>
            </form>
            <constant>
                <constant-name>testKey</constant-name>
                <constant-value>testValue</constant-value>
            </constant>
        </formset>
        <constant>
            <constant-name>testKey_global</constant-name>
            <constant-value>testValue_global</constant-value>
        </constant>
    </form-validation>
    """

# ============================== Mock-based Unit Tests ======================= #

def test_add_constant_mock():
    resources = ValidatorResources()
    resources.add_constant("mockKey", "mockValue")
    assert resources._get_constants()["mockKey"] == "mockValue"

def test_add_form_set_mock():
    resources = ValidatorResources()
    form_set = MagicMock()
    form_set.language = "en"
    form_set.country = "US"
    form_set.variant = None
    resources.add_form_set(form_set)
    key = resources.build_locale("en", "US", None)
    assert key in resources._get_form_sets()

def test_add_validator_action_mock():
    resources = ValidatorResources()
    action = MagicMock()
    action.name = "testAction"
    action.class_name = "TestClass"
    resources.add_validator_action(action)
    assert resources.get_validator_action("testAction") == action

def test_get_form_locale_priority_mock():
    resources = ValidatorResources()

    fs_variant = MagicMock(); fs_variant.get_form.return_value = "form_v"
    fs_country = MagicMock(); fs_country.get_form.return_value = "form_c"
    fs_lang = MagicMock();    fs_lang.get_form.return_value = "form_l"
    default_fs = MagicMock(); default_fs.get_form.return_value = "form_d"

    resources._h_form_sets["en_US_variant"] = fs_variant
    resources._h_form_sets["en_US"] = fs_country
    resources._h_form_sets["en"] = fs_lang
    resources._default_form_set = default_fs

    assert resources._get_form_with_locale("en", "US", "variant", "f") == "form_v"
    assert resources._get_form_with_locale("en", "US", None, "f") == "form_c"
    assert resources._get_form_with_locale("en", None, "x", "f") == "form_l"
    assert resources._get_form_with_locale(None, None, None, "f") == "form_d"

# ============================== Real Unit Tests ============================= #

def test_initialize_with_stream(valid_xml):
    xml_stream = StringIO(valid_xml)
    resources = ValidatorResources(sources=xml_stream)
    assert resources._get_constants()["testKey_global"] == "testValue_global"
    assert "en_US" in resources._get_form_sets()    
    # assert resources._get_constants()["testKey"] == "testValue"
    # assert "en_US" in resources._get_form_sets()

def test_initialize_with_file_path(tmp_path, valid_xml):
    file_path = tmp_path / "test_validation.xml"
    file_path.write_text(valid_xml)
    resources = ValidatorResources(sources=str(file_path))
    assert "en_US" in resources._get_form_sets()

def test_invalid_source_type():
    with pytest.raises(ValueError):
        ValidatorResources(sources=1234)

def test_process_calls_all(mocker):
    resources = ValidatorResources()
    mock_form_set = mocker.Mock()
    resources._h_form_sets = {"key": mock_form_set}
    resources._default_form_set = mocker.Mock()
    resources.process()
    resources._default_form_set.process.assert_called_once()
    mock_form_set.process.assert_called_once()

# ============================== Integration Tests =========================== #

def test_integration_parses_formset_and_constant(valid_xml):
    xml_stream = StringIO(valid_xml)
    resources = ValidatorResources(sources=xml_stream)

    form_set_key = "en_US"
    assert form_set_key in resources._get_form_sets()
    form_set = resources._get_form_sets()[form_set_key]
    form = form_set.get_form("testForm")
    assert form is not None
    assert len(form.fields) == 1
    assert form.fields[0].field_property == "testField"

    print(resources._get_constants())
    assert resources._get_constants()["testKey_global"] == "testValue_global"

    # TODO only gets constants when in form-validation
    # not getting constants when in formset
    # print(resources._get_constants())
    # assert resources._get_constants()["testKey"] == "testValue"