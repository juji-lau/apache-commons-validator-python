"""Licensed to the Apache Software Foundation (ASF) under one or more contributor
license agreements.  See the NOTICE file distributed with this work for additional
information regarding copyright ownership. The ASF licenses this file to You under the
Apache License, Version 2.0 (the "License"); you may not use this file except in
compliance with the License.  You may obtain a copy of the License at.

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from collections import OrderedDict  # If strict order is required
from typing import List, Dict, Optional

class Form:
    """This contains a set of validation rules for a form. The information is contained
    in a list of `Field` objects. Instances of this class are configured with a <form>
    xml element.

    Taken from apache.commons.validator.Form;
    """

    serializable = True
    #: This class is serializable.

    cloneable = False
    #: This class is not cloneable.

    def __init__(self):
        self._name: str = None
        #: The name/key that the set of validation rules is stored under.

        self._l_fields: List["Field"] = []  # List of Field objects
        #: List of `Field`s. Used to maintain the order they were added in. Individual `Field`s can be retrieved using _h_fields

        self._h_fields: Dict[str, "Field"] = OrderedDict()
        #: Dict of `Field`s keyed on their property value. Use get_field_map() to access.

        self._inherit: str = None
        #: the name/key of the form which this form extends from.

        self._processed: bool = False
        #: Whether or not this `Form` was processed for replacing variables in strings with their values.

    def add_field(self, field: "Field") -> None:
        """Add a `Field` to the `Form`.

        Method Arguments:
            field (Field): the field
        """
        self._l_fields.append(field)
        self.get_field_map()[field.key] = field

    def contains_field(self, field_name: str) -> bool:
        """Returns true if this Form contains a Field with the given name.

        Method Arguments     field_name (str): the field name

        Return     True if this form contains the field by the given name.
        """
        return field_name in self.get_field_map()

    def get_extends(self) -> str:
        """Gets the name/key of the parent set of validation rules.

        Returns     the extends value
        """
        return self._inherit

    def get_field(self, field_name: str) -> Optional["Field"]:
        """Returns the Field with the given name or None if this Form has no such field.

        Method Arguments     field_name (str): the field name

        Returns     the field value
        """
        return self.get_field_map().get(field_name)

    def get_field_map(self) -> Dict[str, "Field"]:
        """Returns a dict of str field keys to Field objects.

        Returns     the field map value
        """
        return self._h_fields

    @property
    def fields(self) -> List["Field"]:
        """A copy of list of `Field`s is returned."""
        # TODO make sure the original map won't be modified
        return self._l_fields.copy()

    @property
    def name(self) -> str:
        """Gets the name of the form.

        :return: The name of the form.
        """
        return self._name

    def is_extending(self) -> bool:
        """Gets extends flag."""
        return self._inherit is not None

    @property
    def processed(self) -> bool:
        """Checks whether the form has been processed.

        (translation of isProcessed())
        :return: True if the form has been processed, False otherwise.
        """
        return self._processed

    def _merge(self, depends: "Form") -> None:
        """Merges the given form into this one. For any field in `depends` not present
        in this form, include it. `depends` has precedence in the way the fields are
        ordered.

        Method Arguments     depends (Form): the form we want to merge
        """
        temp_l_fields = []
        temp_h_fields = OrderedDict()
        for default_field in depends.fields:
            if default_field is not None:
                field_key = default_field.key
                if not self.contains_field(field_key):
                    temp_l_fields.append(default_field)
                    temp_h_fields[field_key] = default_field
                else:
                    old = self.get_field(field_key)
                    self.get_field_map().pop(field_key, None)
                    self._l_fields.remove(old)
                    temp_l_fields.append(old)
                    temp_h_fields[field_key] = old
        self._l_fields = temp_l_fields + self._l_fields
        self.get_field_map().update(temp_h_fields)

    def _process(
        self, global_constants: dict, constants: dict, forms: Dict[str, "Form"]
    ) -> None:
        """Processes the form by handling inheritance and field processing.

        Marks the form as processed once complete.
        :param global_constants: A dictionary of global constants.
        :param constants: A dictionary of local constants.
        :param forms: A dictionary of all forms.
        """
        if self.processed:
            return
        n = 0
        if self.is_extending():
            parent = forms.get(self._inherit)
            if parent:
                if not parent.processed:
                    parent._process(constants, global_constants, forms)
                for f in parent.fields:
                    if f.key not in self.get_field_map():
                        self._l_fields.insert(n, f)
                        self.get_field_map()[f.key] = f
                        n += 1
        for field in self._l_fields[n:]:
            field.process(global_constants, constants)

        self._processed = True

    def set_extends(self, inherit: str) -> None:
        """Sets the name/key of the parent set of validation rules.

        Method Arguments     the new extends value
        """
        self._inherit = inherit

    @name.setter
    def name(self, value: str) -> None:
        """Sets the name of the form.

        :param value: The name of the form to be set.
        """
        self._name = value

    def __str__(self) -> str:
        """Returns a string representation of the object."""
        results = f"Form: {self._name}\n"
        for field in self._l_fields:
            results += f"\tField: {field}\n"
        return results

    def validate(
        self, params: dict, actions: dict, page: int, field_name: str = None
    ) -> "ValidatorResults":
        """Validates the fields of the form and returns the validation results.

        This method iterates through the form's fields and validates them based on the provided
        `params`, `actions`, and `page` parameters. If a `field_name` is provided, it validates
        only that specific field. Otherwise, it validates all fields in the form that are
        relevant for the given page.

        Method Arguments:
            params (dict): A dictionary containing parameters required for validation.
            actions (dict): A dictionary of actions associated with the validation process.
            page (int): The current page number used for validating fields relevant to this page.
            field_name (str, optional): The specific field to validate. If not provided, all fields
                                        on the current page are validated.

        Returns:
            ValidatorResults: An object containing the result of the validation process.

        Raises:
            ValidatorException: If the specified `field_name` does not correspond to a valid field
                                in the form.
        """
        from src.apache_commons_validator_python.validator_results_new import ValidatorResults
        from src.apache_commons_validator_python.validator_new import Validator
        from src.apache_commons_validator_python.validator_exception_new import ValidatorException
        
        results = ValidatorResults()
        params[Validator.VALIDATOR_RESULTS_PARAM] = results

        if field_name:
            field = self.get_field(field_name)
            if not field:
                raise ValidatorException(
                    f"Unknown field {field_name} in form {self._name}"
                )
            params[Validator.FIELD_PARAM] = field
            if field.page <= page:
                results.merge(field.validate(params, actions))
        else:
            for field in self._l_fields:
                params[Validator.FIELD_PARAM] = field
                if field.page <= page:
                    results.merge(field.validate(params, actions))

        return results