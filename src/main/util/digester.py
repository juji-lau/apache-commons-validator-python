import xml.sax
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, Type
from src.main.form_set import FormSet
from src.main.form import Form
from src.main.field import Field
from src.main.var import Var
from src.main.msg import Msg
from src.main.arg import Arg
from src.main.form_set_factory import FormSetFactory
from src.main.validator_action import ValidatorAction


class Digester(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        self.rules: Dict[str, Dict[str, Any]] = {}  # Stores Digester rules
        self.object_stack: list[Any] = []  # Stack to maintain object hierarchy
        self.current_text: str = ""  # Stores text content
        self.root_object: Optional[Any] = None  # The top-level parsed object
        self.class_mapping: Dict[str, Type] = (
            {  # Maps XML class names to Python classes
                "FormSetFactory": FormSetFactory,
                "FormSet": FormSet,
                "Form": Form,
                "Field": Field,
                "Var": Var,
                "Msg": Msg,
                "ValidatorAction": ValidatorAction,
                "Arg": Arg,
            }
        )

    def load_rules(self, rules_file: str) -> None:
        """
        Loads the Digester rules from `digester-rules.xml`.
        """
        tree = ET.parse(rules_file)
        root = tree.getroot()

        for pattern in root.findall(".//pattern"):  # Ensure correct XPath
            pattern_value = pattern.get("value", "")
            self.rules[pattern_value] = {}

            # Object Creation Rule
            obj_create = pattern.find("object-create-rule")
            if obj_create is not None:
                class_name = obj_create.get("classname", "")
                if class_name in self.class_mapping:
                    self.rules[pattern_value]["object-create-rule"] = (
                        self.class_mapping[class_name]
                    )
                else:
                    print(f"WARNING: Class {class_name} not found in class_mapping")

            # Factory Create Rule (Added Support)
            factory_create = pattern.find("factory-create-rule")
            if factory_create is not None:
                class_name = factory_create.get("classname", "")
                if class_name in self.class_mapping:
                    self.rules[pattern_value]["object-create-rule"] = (
                        self.class_mapping[class_name]
                    )
                else:
                    print(
                        f"WARNING: Factory class {class_name} not found in class_mapping"
                    )

            # Set Properties Rule
            set_properties = pattern.find("set-properties-rule")
            if set_properties is not None:
                self.rules[pattern_value]["set-properties-rule"] = True

            # Set Next Rule
            set_next = pattern.find("set-next-rule")
            if set_next is not None:
                self.rules[pattern_value]["set-next-rule"] = {
                    "method": set_next.get("methodname", ""),
                    "paramtype": set_next.get("paramtype", ""),
                }

    def startElement(self, name: str, attrs: xml.sax.xmlreader.AttributesImpl) -> None:
        """
        Called when an XML start tag is encountered.
        """
        if name in self.rules:
            rule = self.rules[name]

            # **object-create-rule** → Instantiate a class
            if "object-create-rule" in rule:
                obj_class = rule["object-create-rule"]
                obj = obj_class()

                # **set-properties-rule** → Map attributes to object properties
                if "set-properties-rule" in rule:
                    for attr in attrs.keys():
                        setattr(obj, attr, attrs[attr])

                self.object_stack.append(obj)

    def endElement(self, name: str) -> None:
        """
        Called when an XML end tag is encountered.
        """
        if name in self.rules:
            rule = self.rules[name]
            obj = self.object_stack.pop()

            # **set-next-rule** → Attach object to parent
            if "set-next-rule" in rule:
                parent_obj = self.object_stack[-1]
                method_name = rule["set-next-rule"]["method"]
                if hasattr(parent_obj, method_name):
                    getattr(parent_obj, method_name)(obj)

            # Store top-level object if needed
            if len(self.object_stack) == 0:
                self.root_object = obj

    def characters(self, content: str) -> None:
        """
        Stores text content inside elements.
        """
        self.current_text += content.strip()

    def parse(self, xml_file: str) -> Optional[Any]:
        """
        Parses the XML file using the registered rules.
        """
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(xml_file)
        return self.root_object
