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
    def __init__(self, root_object: ['ValidatorResources']):
        super().__init__()
        self.rules: Dict[str, Dict[str, Any]] = {}
        self.object_stack: list[Any] = []
        self.current_path: list[str] = []
        self.root_object: 'ValidatorResources' = root_object
        self.class_mapping: Dict[str, Type] = {
            "FormSetFactory": FormSetFactory,
            "FormSet": FormSet,
            "Form": Form,
            "Field": Field,
            "Var": Var,
            "Msg": Msg,
            "ValidatorAction": ValidatorAction,
            "Arg": "Arg",
        }
        self.object_stack.append(self.root_object)
        self.current_params: list[str] = []
        self.text_buffer: str = ""

    def load_rules(self, rules_file: str) -> None:
        tree = ET.parse(rules_file)
        root = tree.getroot()

        def load_patterns(parent, parent_path=""):
            for pattern in parent.findall("pattern"):
                value = pattern.get("value", "")
                full_path = f"{parent_path}/{value}" if parent_path else value
                self.rules[full_path] = {}

                obj_create = pattern.find("object-create-rule")
                if obj_create is not None:
                    class_name = obj_create.get("classname", "")
                    if class_name in self.class_mapping:
                        self.rules[full_path]["object-create-rule"] = self.class_mapping[class_name]

                factory_create = pattern.find("factory-create-rule")
                if factory_create is not None:
                    class_name = factory_create.get("classname", "")
                    if class_name in self.class_mapping:
                        self.rules[full_path]["factory-create-rule"] = self.class_mapping[class_name]

                set_properties = pattern.find("set-properties-rule")
                if set_properties is not None:
                    self.rules[full_path]["set-properties-rule"] = True

                set_next = pattern.find("set-next-rule")
                if set_next is not None:
                    self.rules[full_path]["set-next-rule"] = {
                        "method": set_next.get("methodname", ""),
                        "paramtype": set_next.get("paramtype", ""),
                    }

                call_method = pattern.find("call-method-rule")
                if call_method is not None:
                    self.rules[full_path]["call-method-rule"] = {
                        "method": call_method.get("methodname", ""),
                        "paramcount": int(call_method.get("paramcount", "0")),
                    }

                call_params = pattern.findall("call-param-rule")
                if call_params:
                    self.rules[full_path]["call-param-rule"] = []
                    for cp in call_params:
                        self.rules[full_path]["call-param-rule"].append({
                            "pattern": f"{full_path}/{cp.get('pattern', '')}",
                            "paramnumber": int(cp.get("paramnumber", "0")),
                        })

                load_patterns(pattern, full_path)

        load_patterns(root)

    def startElement(self, name: str, attrs: xml.sax.xmlreader.AttributesImpl) -> None:
        self.current_path.append(name)
        path = "/".join(self.current_path)
        self.text_buffer = ""  # Reset text buffer
        # print(f"Start Element: {path}")

        if path in self.rules:
            rule = self.rules[path]
            if "factory-create-rule" in rule:
                factory_class = rule["factory-create-rule"]
                factory_instance = factory_class()
                obj = factory_instance.create_object(attrs, self.root_object)
                if "set-properties-rule" in rule:
                    for attr in attrs.keys():
                        mapped_attr = attr
                        if attr == "classname":
                            mapped_attr = "class_name"
                        setattr(obj, mapped_attr, attrs[attr])
                self.object_stack.append(obj)
            elif "object-create-rule" in rule:
                obj_class = rule["object-create-rule"]
                obj = obj_class()
                if "set-properties-rule" in rule:
                    for attr in attrs.keys():
                        mapped_attr = attr
                        if attr == "classname":
                            mapped_attr = "class_name"
                        setattr(obj, mapped_attr, attrs[attr])
                self.object_stack.append(obj)


    def endElement(self, name: str) -> None:
        path = "/".join(self.current_path)
        if self.text_buffer.strip():
            for rule_path, rule in self.rules.items():
                if "call-param-rule" in rule:
                    for param in rule["call-param-rule"]:
                        if param["pattern"] == path:
                            if len(self.current_params) <= param["paramnumber"]:
                                self.current_params.extend([None] * (param["paramnumber"] - len(self.current_params) + 1))
                            self.current_params[param["paramnumber"]] = self.text_buffer.strip()
        self.text_buffer = ""

        if path in self.rules:
            rule = self.rules[path]
            if "call-method-rule" in rule:
                method_name = rule["call-method-rule"]["method"]
                paramcount = rule["call-method-rule"]["paramcount"]
                if len(self.current_params) == paramcount:
                    method = getattr(self.root_object, method_name)
                    method(*self.current_params)
                self.current_params = []
            elif self.object_stack:
                obj = self.object_stack.pop()
                if "set-next-rule" in rule and self.object_stack:
                    parent_obj = self.object_stack[-1]
                    method_name = rule["set-next-rule"]["method"]
                    if hasattr(parent_obj, method_name):
                        getattr(parent_obj, method_name)(obj)
        self.current_path.pop()

    def characters(self, content: str) -> None:
        self.text_buffer += content

    def parse(self, xml_file: str) -> None:
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(xml_file)
        return self.object_stack[0] if self.object_stack else None
