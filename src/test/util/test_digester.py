import pytest
import io
import xml.sax
from src.main.util.digester import Digester
from src.main.validator_resources import ValidatorResources
from src.main.form_set import FormSet
from src.main.form import Form
from src.main.field import Field
from src.main.var import Var
from src.main.msg import Msg

@pytest.fixture
def digester():
    resources = ValidatorResources()
    digester = Digester(root_object=resources)

    # Load digester rules from the real digester-rules.xml file
    digester.load_rules("src/resources/digester-rules.xml")
    return digester, resources

def test_digester_parse_validation_xml(digester):
    digester, resources = digester
    validation_xml = io.StringIO(
        """<?xml version="1.0"?>
        <form-validation>
            <formset>
                <form name="userForm">
                    <field field_property="username" depends="required">
                        <var name="maxLength" value="50"/>
                        <msg name="error" key="username.required"/>
                    </field>
                </form>
            </formset>
        </form-validation>
    """)
    digester.parse(validation_xml)

    assert resources._get_form_sets()  # Ensure at least one form set exists
    form_set = next(iter(resources._get_form_sets().values()))
    assert isinstance(form_set, FormSet)
    assert len(form_set.get_forms()) == 1

    form = next(iter(form_set.get_forms().values()))
    assert isinstance(form, Form)
    assert form.name == "userForm"

    field = form.fields[0]
    assert isinstance(field, Field)
    assert field.field_property == "username"
    assert field.depends == "required"

    var = next(iter(field.vars.values()))
    assert isinstance(var, Var)
    assert var.name == "maxLength"
    assert var.value == "50"

    msg = next(iter(field.msgs.values()))
    assert isinstance(msg, Msg)
    assert msg.name == "error"
    assert msg.key == "username.required"

def test_digester_multiple_fields(digester):
    digester, resources = digester
    validation_xml = io.StringIO(
        """<?xml version="1.0"?>
        <form-validation>
            <formset>
                <form name="multiFieldForm">
                    <field field_property="username" depends="required"/>
                    <field field_property="email" depends="email"/>
                </form>
            </formset>
        </form-validation>
    """)
    digester.parse(validation_xml)

    form_set = next(iter(resources._get_form_sets().values()))
    form = form_set.get_forms()["multiFieldForm"]
    assert len(form.fields) == 2
    assert form.fields[0].field_property == "username"
    assert form.fields[1].field_property == "email"

def test_digester_constants(digester):
    digester, resources = digester
    validation_xml = io.StringIO(
        """<?xml version="1.0"?>
        <form-validation>
            <constant>
                <constant-name>minLength</constant-name>
                <constant-value>5</constant-value>
            </constant>
        </form-validation>
    """)
    digester.parse(validation_xml)

    assert "minLength" in resources._get_constants()
    assert resources._get_constants()["minLength"] == "5"

def test_digester_multiple_constants(digester):
    digester, resources = digester
    validation_xml = io.StringIO(
        """<?xml version="1.0"?>
        <form-validation>
            <constant>
                <constant-name>minLength</constant-name>
                <constant-value>5</constant-value>
            </constant>
            <constant>
                <constant-name>maxLength</constant-name>
                <constant-value>10</constant-value>
            </constant>
        </form-validation>
    """)
    digester.parse(validation_xml)

    assert "minLength" in resources._get_constants()
    assert resources._get_constants()["minLength"] == "5"

    assert "maxLength" in resources._get_constants()
    assert resources._get_constants()["maxLength"] == "10"

def test_digester_constants_inside_formset(digester):
    validation_xml = io.StringIO("""
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
    </form-validation>
    """)
class RequiredValidator:
    @staticmethod
    def validate(bean, field, results, validator, form):
        # Just a dummy validation function for test
        return True
    
def test_digester_validator_actions(digester):
    digester, resources = digester
    validation_xml = io.StringIO(
        """<?xml version="1.0"?>
        <form-validation>
            <validator name="required" classname="src.test.util.test_digester.RequiredValidator">
                <javascript/>
            </validator>
        </form-validation>
    """)
    digester.parse(validation_xml)

    assert "required" in resources._get_actions()
    action = resources._get_actions()["required"]
    assert action.name == "required"
    assert action.class_name == "src.test.util.test_digester.RequiredValidator"