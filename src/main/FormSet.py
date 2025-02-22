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

import logging
from typing import Dict, Optional


class FormSet:
    """
    This class contains a set of Forms associated with a specific Locale.
    It supports operations for managing Forms, Constants, and Locale components 
    (language, country, variant). It also provides methods for processing Forms,
    merging FormSets, and managing their states.

    Attributes:
        serializable (bool): Indicates if the object is serializable.
        cloneable (bool): Indicates if the object can be cloned.
        language (Optional[str]): The language component of the Locale.
        country (Optional[str]): The country component of the Locale.
        variant (Optional[str]): The variant component of the Locale.
        processed (bool): Indicates if the FormSet has been processed.
        merged (bool): Indicates if the FormSet has been merged with a parent.
        forms (Dict[str, 'Form']): A dictionary of Forms in the FormSet.
        constants (Dict[str, str]): A dictionary of Constants in the FormSet.
    """
    # FormSet types constants
    GLOBAL_FORMSET = 1
    LANGUAGE_FORMSET = 2
    COUNTRY_FORMSET = 3
    VARIANT_FORMSET = 4

    def __init__(self):
        """
        Initializes a new FormSet instance with default values.
        """
        self._log: Optional[logging.Logger] = None  # Logger for logging errors
        self._processed: bool = False  # Indicates if the FormSet has been processed
        self._language: Optional[str] = None  # Language component
        self._country: Optional[str] = None  # Country component
        self._variant: Optional[str] = None  # Variant component
        self._forms: Dict[str, 'Form'] = {}  # Map of forms by their names
        self._constants: Dict[str, str] = {}  # Map of constants by their names
        self._merged: bool = False  # Flag indicating if FormSet has been merged

        self.serializable = True  # Object is serializable
        self.cloneable = False  

    @property
    def language(self) -> Optional[str]:
        """Returns the language component of the Locale."""
        return self._language

    @language.setter
    def language(self, value: Optional[str]) -> None:
        """Sets the language component of the Locale."""
        self._language = value

    @property
    def country(self) -> Optional[str]:
        """Returns the country component of the Locale."""
        return self._country

    @country.setter
    def country(self, value: Optional[str]) -> None:
        """Sets the country component of the Locale."""
        self._country = value

    @property
    def variant(self) -> Optional[str]:
        """Returns the variant component of the Locale."""
        return self._variant

    @variant.setter
    def variant(self, value: Optional[str]) -> None:
        """Sets the variant component of the Locale."""
        self._variant = value

    @property
    def processed(self) -> bool:
        """Returns whether the FormSet has been processed."""
        return self._processed

    @processed.setter
    def processed(self, value: bool) -> None:
        """Sets the processed state of the FormSet."""
        self._processed = value

    @property
    def merged(self) -> bool:
        """Returns whether the FormSet has been merged."""
        return self._merged

    @merged.setter
    def merged(self, value: bool) -> None:
        """Sets the merged state of the FormSet."""
        self._merged = value

    @property
    def forms(self) -> Dict[str, 'Form']:
        """Returns the dictionary of Forms in the FormSet."""
        return self._forms

    @property
    def constants(self) -> Dict[str, str]:
        """Returns the dictionary of Constants in the FormSet."""
        return self._constants

    def add_constant(self, name: str, value: str) -> None:
        """
        Adds a Constant to the FormSet.

        Args:
            name (str): The constant name.
            value (str): The constant value.
        """
        if name in self._constants:
            self.get_log().error(f"Constant '{name}' already exists in FormSet - ignoring.")
        else:
            self._constants[name] = value

    def add_form(self, f: 'Form') -> None:
        """
        Adds a Form to the FormSet.

        Args:
            f (Form): The Form to be added.
        """
        form_name = f.get_name()
        if form_name in self._forms:
            self.get_log().error(f"Form '{form_name}' already exists in FormSet - ignoring.")
        else:
            self._forms[form_name] = f

    def display_key(self) -> str:
        """
        Returns a string representation of the FormSet key based on its Locale components.

        Returns:
            str: A string representation of the key.
        """
        results = []
        if self._language:
            results.append(f"language={self._language}")
        if self._country:
            results.append(f"country={self._country}")
        if self._variant:
            results.append(f"variant={self._variant}")
        if not results:
            results.append("default")
        return ", ".join(results)

    def get_form(self, form_name: str) -> Optional['Form']:
        """
        Retrieves a Form from the FormSet by its name.

        Args:
            form_name (str): The name of the form to retrieve.

        Returns:
            Form: The requested Form, or None if not found.
        """
        return self._forms.get(form_name)

    def _get_log(self) -> logging.Logger:
        """
        Returns the logger for logging errors. Initializes the logger if necessary.

        Returns:
            logging.Logger: The Logger instance.
        """
        if self._log is None:
            self._log = logging.getLogger(__name__)
        return self._log

    def _get_type(self) -> int:
        """
        Returns the type of the FormSet based on its Locale components.

        Returns:
            int: The FormSet type (GLOBAL_FORMSET, LANGUAGE_FORMSET, COUNTRY_FORMSET, VARIANT_FORMSET).
        """
        if self._variant:
            if not self._language or not self._country:
                raise ValueError("When variant is specified, country and language must be specified.")
            return self.VARIANT_FORMSET
        if self._country:
            if not self._language:
                raise ValueError("When country is specified, language must be specified.")
            return self.COUNTRY_FORMSET
        if self._language:
            return self.LANGUAGE_FORMSET
        return self.GLOBAL_FORMSET

    def _merge(self, depends: 'FormSet') -> None:
        """
        Merges another FormSet into this one.

        Args:
            depends (FormSet): The FormSet to merge with this one.
        """
        if depends:
            p_forms = self.get_forms()
            d_forms = depends.get_forms()
            for key, form in d_forms.items():
                p_form = p_forms.get(key)
                if p_form:
                    p_form.merge(form)
                else:
                    self.add_form(form)
        self._merged = True

    def process(self, global_constants: Dict[str, str]) -> None:
        """
        Processes all Forms in the FormSet.

        Args:
            global_constants (Dict[str, str]): Global constants to be used during processing.
        """
        for f in self._forms.values():
            f.process(global_constants, self._constants, self._forms)
        self._processed = True

    def __str__(self) -> str:
        """
        Returns a string representation of the FormSet.

        Returns:
            str: A string representation of the FormSet.
        """
        results = [f"FormSet: language={self._language}  country={self._country}  variant={self._variant}\n"]
        for form in self.get_forms().values():
            results.append(f"   {form}\n")
        return ''.join(results)
