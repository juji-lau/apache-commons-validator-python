import pytest
import io
import xml.sax
from src.main.util.digester import Digester  # Import the Digester class
from src.main.FormSet import FormSet
from src.main.Form import Form
from src.main.Field import Field
from src.main.Var import Var
from src.main.Msg import Msg


@pytest.fixture
def digester():
    """
    Initializes the Digester instance and loads rules from a mock digester-rules.xml.
    """
    digester = Digester()

    # Mock digester-rules.xml as an in-memory string
    rules_xml = io.StringIO(
        """<?xml version="1.0"?>
    <digester-rules>

        <pattern value="form-validation">
            <object-create-rule classname="FormSet" />
            <set-properties-rule/>
        </pattern>

        <pattern value="form-validation/global">
            
            <pattern value="constant">
                <call-method-rule methodname="add_constant" paramcount="2" />
                <call-param-rule pattern="constant-name" paramnumber="0" />
                <call-param-rule pattern="constant-value" paramnumber="1" />
            </pattern>
            
            <pattern value="validator">
                <object-create-rule classname="ValidatorAction" />
                <set-properties-rule/>
                <set-next-rule methodname="add_validator_action" paramtype="src.main.ValidatorAction.ValidatorAction" />
                <call-method-rule pattern="javascript" methodname="setJavascript" paramcount="0" />
            </pattern>
            
        </pattern>
        
        
        <pattern value="form-validation/formset">

            <factory-create-rule classname="FormSetFactory" />
            
            <pattern value="constant">
                <call-method-rule methodname="add_constant" paramcount="2" />
                <call-param-rule pattern="constant-name" paramnumber="0" />
                <call-param-rule pattern="constant-value" paramnumber="1" />
            </pattern>
            
            <pattern value="form">
                <object-create-rule classname="Form" />
                <set-properties-rule/>
                <set-next-rule methodname="add_form" paramtype="Form" />
                
                <pattern value="field">
                    <object-create-rule classname="Field" />
                    <set-properties-rule/>
                    <set-next-rule methodname="add_field" paramtype="Field" />
                    
                    <pattern value="var">
                        <object-create-rule classname="Var" />
                        <set-properties-rule/>
                        <pattern value="var-name">
                            <call-method-rule methodname="name" paramcount="0" />
                        </pattern>
                        <pattern value="var-value">
                            <call-method-rule methodname="value" paramcount="0" />
                        </pattern>
                        <pattern value="var-jstype">
                            <call-method-rule methodname="js_type" paramcount="0" />
                        </pattern>
                        <set-next-rule methodname="add_var" paramtype="Var" />
                    </pattern>
                    
                    <pattern value="msg">
                        <object-create-rule classname="Msg" />
                        <set-properties-rule/>
                        <set-next-rule methodname="add_msg" paramtype="Msg" />
                    </pattern>
                    
                    <pattern value="arg">
                        <object-create-rule classname="Arg" />
                        <set-properties-rule/>
                        <set-next-rule methodname="add_arg" paramtype="Arg" />
                    </pattern>
                
                </pattern>
                
            </pattern>
            
        </pattern>
    </digester-rules>
    """
    )

    # Load rules
    digester.load_rules(rules_xml)

    import pprint

    # Print the rules dictionary to verify correctness
    pprint.pprint(digester.rules)

    return digester


def test_digester_parse_validation_xml(digester):
    """
    Tests that validation.xml is correctly parsed into FormSet, Form, Field, Var, and Msg objects.
    """
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
    """
    )

    parsed_form_set = digester.parse(validation_xml)

    assert isinstance(parsed_form_set, FormSet)
    assert len(parsed_form_set.forms) == 1

    form = list(parsed_form_set.forms.values())[0]

    assert isinstance(form, Form)
    assert form.name == "userForm"

    assert len(form.fields) == 1

    field = form.fields[0]
    assert isinstance(field, Field)
    assert field.field_property == "username"
    assert field.depends == "required"

    assert len(field.vars) == 1
    var = list(field.vars.values())[0]
    assert isinstance(var, Var)
    assert var.name == "maxLength"
    assert var.value == "50"

    assert len(field.msgs) == 1
    msg = list(field.msgs.values())[0]
    assert isinstance(msg, Msg)
    assert msg.name == "error"
    assert msg.key == "username.required"


def test_digester_empty_validation_xml(digester):
    """
    Tests parsing of an empty XML structure.
    """
    empty_xml = io.StringIO("<?xml version='1.0'?><form-validation></form-validation>")
    parsed_form_set = digester.parse(empty_xml)

    assert isinstance(parsed_form_set, FormSet)
    assert len(parsed_form_set.forms) == 0


def test_digester_multiple_forms(digester):
    """
    Tests parsing XML with multiple forms.
    """
    validation_xml = io.StringIO(
        """<?xml version="1.0"?>
    <form-validation>
        <formset>
            <form name="userForm1">
                <field field_property="username" depends="required">
                    <var name="maxLength" value="50"/>
                    <msg name="error" key="username.required"/>
                </field>
            </form>
            <form name="userForm2">
                <field field_property="email" depends="required">
                    <var name="maxLength" value="100"/>
                    <msg name="error" key="email.required"/>
                </field>
            </form>
        </formset>
    </form-validation>
    """
    )

    parsed_form_set = digester.parse(validation_xml)

    assert len(parsed_form_set.forms) == 2

    form1, form2 = list(parsed_form_set.forms.values())

    assert form1.name == "userForm1"
    assert form2.name == "userForm2"

    assert form1.fields[0].field_property == "username"
    assert form2.fields[0].field_property == "email"

    assert list(form1.fields[0].vars.values())[0].value == "50"
    assert list(form2.fields[0].vars.values())[0].value == "100"


def test_digester_invalid_xml(digester):
    """
    Tests handling of invalid XML.
    """
    invalid_xml = io.StringIO(
        "<form-validation><formset><form name='userForm'></formset></form-validation>"
    )

    with pytest.raises(xml.sax.SAXParseException):
        digester.parse(invalid_xml)
