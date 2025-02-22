""" 
  Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at
 
       http://www.apache.org/licenses/LICENSE-2.0
 
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
 """
from collections import OrderedDict  # If strict order is required
from typing import List, Dict

class Form:
    def __init__(self):
        self._name: str = None
        self._lFields: List['Field'] = []  # List of Field objects
        self._hFields: Dict[str, 'Field'] = OrderedDict()  # Replacing FastHashMap with OrderedDict
        self._inherit: str = None
        self._processed: bool = False
        self.serializable = True

    # Getter and setter for name
    @property
    def name(self) -> str:
        """
        Gets the name of the form.
        :return: The name of the form.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        Sets the name of the form.
        :param value: The name of the form to be set.
        """
        self._name = value

    # Getter and setter for lFields (list of fields)
    @property
    def lFields(self) -> List['Field']:
        """
        Gets the list of Field objects associated with the form.
        :return: The list of Field objects.
        """
        return self._lFields

    @lFields.setter
    def lFields(self, value: List['Field']) -> None:
        """
        Sets the list of Field objects for the form.
        :param value: The list of Field objects to be set.
        """
        self._lFields = value

    # Getter and setter for hFields (dictionary of fields by key)
    @property
    def hFields(self) -> Dict[str, 'Field']:
        """
        Gets the dictionary of Field objects associated with the form, keyed by their unique identifier.
        :return: The dictionary of fields.
        """
        return self._hFields

    @hFields.setter
    def hFields(self, value: Dict[str, 'Field']) -> None:
        """
        Sets the dictionary of Field objects for the form.
        :param value: The dictionary of Field objects to be set.
        """
        self._hFields = value

    # Getter and setter for inherit (parent form's key)
    @property
    def inherit(self) -> str:
        """
        Gets the key/name of the parent form that this form is extending.
        :return: The key/name of the parent form, if any.
        """
        return self._inherit

    @inherit.setter
    def inherit(self, value: str) -> None:
        """
        Sets the parent form that this form will inherit from.
        :param value: The key/name of the parent form to be set.
        """
        self._inherit = value

    # Getter and setter for processed (whether the form has been processed)
    @property
    def processed(self) -> bool:
        """
        Checks whether the form has been processed.
        :return: True if the form has been processed, False otherwise.
        """
        return self._processed

    @processed.setter
    def processed(self, value: bool) -> None:
        """
        Sets the processed status of the form.
        :param value: True if the form has been processed, False otherwise.
        """
        self._processed = value

    def add_field(self, field: 'Field') -> None:
        self._lFields.append(field)
        self._hFields[field.get_key()] = field  # Store the Field by its key in hFields

    def contains_field(self, field_name: str) -> bool:
        return field_name in self._hFields

    def get_extends(self) -> str:
        return self._inherit

    def get_field(self, field_name: str) -> 'Field':
        return self._hFields.get(field_name)

    def get_field_map(self) -> Dict[str, 'Field']:
        return self._hFields

    def get_fields(self) -> List['Field']:
        return self._lFields

    def get_name(self) -> str:
        return self._name

    def is_extending(self) -> bool:
        return self._inherit is not None

    def is_processed(self) -> bool:
        return self._processed

    # Protected method to merge fields from another form
    def _merge(self, depends: 'Form') -> None:
        templFields = []
        temphFields = OrderedDict()
        for default_field in depends.get_fields():
            if default_field is not None:
                field_key = default_field.get_key()
                if not self.contains_field(field_key):
                    templFields.append(default_field)
                    temphFields[field_key] = default_field
                else:
                    old = self.get_field(field_key)
                    self._hFields.pop(field_key, None)
                    self._lFields.remove(old)
                    templFields.append(old)
                    temphFields[field_key] = old
        self._lFields = templFields + self._lFields
        self._hFields.update(temphFields)

    # Protected method to process the form
    def _process(self, global_constants: dict, constants: dict, forms: Dict[str, 'Form']) -> None:
        """
        Processes the form by handling inheritance and field processing.
        Marks the form as processed once complete.
        :param global_constants: A dictionary of global constants.
        :param constants: A dictionary of local constants.
        :param forms: A dictionary of all forms.
        """
        if self.is_processed():
            return
        n = 0
        if self.is_extending():
            parent = forms.get(self._inherit)
            if parent:
                if not parent.is_processed():
                    parent._process(constants, global_constants, forms)
                for f in parent.get_fields():
                    if f.get_key() not in self._hFields:
                        self._lFields.insert(n, f)
                        self._hFields[f.get_key()] = f
                        n += 1
        for field in self._lFields[n:]:
            field.process(global_constants, constants)

        self._processed = True

    def set_extends(self, inherit: str) -> None:
        self._inherit = inherit

    def set_name(self, name: str) -> None:
        self._name = name

    def __str__(self) -> str:
        results = f"Form: {self._name}\n"
        for field in self._lFields:
            results += f"\tField: {field}\n"
        return results

    def validate(self, params: dict, actions: dict, page: int, field_name: str = None) -> 'ValidatorResults':
        """
        Validates the fields of the form and returns the validation results.

        This method iterates through the form's fields and validates them based on the provided 
        `params`, `actions`, and `page` parameters. If a `field_name` is provided, it validates 
        only that specific field. Otherwise, it validates all fields in the form that are 
        relevant for the given page.

        Parameters:
        - params (dict): A dictionary containing parameters required for validation.
        - actions (dict): A dictionary of actions associated with the validation process.
        - page (int): The current page number used for validating fields relevant to this page.
        - field_name (str, optional): The specific field to validate. If not provided, all fields 
        on the current page are validated.

        Returns:
        - ValidatorResults: An object containing the result of the validation process.

        Raises:
        - ValidatorException: If the specified `field_name` does not correspond to a valid field 
        in the form.
        """
        results = ValidatorResults()
        params[Validator.VALIDATOR_RESULTS_PARAM] = results

        if field_name:
            field = self.get_field(field_name)
            if not field:
                raise ValidatorException(f"Unknown field {field_name} in form {self._name}")
            params[Validator.FIELD_PARAM] = field
            if field.get_page() <= page:
                results.merge(field.validate(params, actions))
        else:
            for field in self._lFields:
                params[Validator.FIELD_PARAM] = field
                if field.get_page() <= page:
                    results.merge(field.validate(params, actions))

        return results
