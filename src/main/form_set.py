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
from typing import Dict, Optional, Final
from src.main.form import Form


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
    _GLOBAL_FORMSET: Final[int] = 1
    #: The type of formset when no locale is specified.

    _LANGUAGE_FORMSET: Final[int] = 2
    #: The type of formset when where only language locale is specified.

    _COUNTRY_FORMSET: Final[int] = 3
    #: The type of formset where only language and country locla are specified.

    _VARIANT_FORMSET: Final[int] = 4
    #: THe type of formset where full locale has been set.

    serializable = True
    #: Class is serializable

    cloneable = False
    #: Class is not cloneable

    def __init__(self):
        """
        Initializes a new FormSet instance with default values.
        """
        self.__log: Optional[logging.Logger] = None
        #: Logger for logging errors

        self.__processed: bool = False
        #: Indicates if the FormSet has been processed

        self.__language: Optional[str] = None
        #: Language component

        self.__country: Optional[str] = None
        #: Country component

        self.__variant: Optional[str] = None
        #: Variant component

        self.__forms: Final[Dict[str, Form]] = {}
        #: Map of forms by their names

        self.__constants: Final[Dict[str, str]] = {}
        #: Map of constants by their names as keys

        self.__merged: bool = False
        #: Flag indicating if FormSet has been merged

    def add_constant(self, name: str, value: str) -> None:
        """
        Adds a Constant to the FormSet.

        Args:
            name (str): The constant name.
            value (str): The constant value.
        """
        if name in self.__constants:
            self._get_log().error(
                "Constant %s already exists in FormSet - ignoring.", name
            )
        else:
            self.__constants[name] = value

    def add_form(self, f: Form) -> None:
        """
        Adds a Form to the FormSet.

        Args:
            f (Form): The Form to be added.
        """
        form_name = f.name
        if form_name in self.__forms:
            self._get_log().error(
                "Form %s already exists in FormSet - ignoring.", form_name
            )
        else:
            self.__forms[form_name] = f

    def display_key(self) -> str:
        """
        Returns a string representation of the FormSet key based on its Locale components.

        Returns:
            str: A string representation of the key.
        """
        results = []
        if self.language:
            results.append(f"language={self.language}")
        if self.country:
            results.append(f"country={self.country}")
        if self.variant:
            results.append(f"variant={self.variant}")
        if not results:
            results.append("default")
        return ", ".join(results)

    @property
    def country(self) -> Optional[str]:
        """Returns the country component of the Locale."""
        return self.__country
    

    def get_form(self, form_name: str) -> Optional[Form]:
        """
        Retrieves a Form from the FormSet by its name.

        Args:
            form_name (str): The name of the form to retrieve.

        Returns:
            Form: The requested Form, or None if not found.
        """
        return self.__forms.get(form_name)
    
    def get_forms(self) -> Dict[str, Form]:
        """
        A dict of forms is returned as an unmodifiable dict with the key
        based on the for name.
        (translation of getForms())
        """
        # TODO make this unmodifiable
        return self.__forms

    @property
    def language(self) -> Optional[str]:
        """Returns the language component of the Locale."""
        return self.__language


    def _get_log(self) -> logging.Logger:
        """
        Returns the logger for logging errors. Initializes the logger if necessary.

        Returns:
            logging.Logger: The Logger instance.
        """
        if self.__log is None:
            self.__log = logging.getLogger(__name__)
        return self.__log
    
    def _get_type(self) -> int:
        """
        Returns the type of the FormSet based on its Locale components.

        Returns:
            int: The FormSet type (GLOBAL_FORMSET, LANGUAGE_FORMSET, COUNTRY_FORMSET, VARIANT_FORMSET).
        """
        if self.variant:
            if not self.language or not self.country:
                raise ValueError(
                    "When variant is specified, country and language must be specified."
                )
            return self._VARIANT_FORMSET
        if self.country:
            if not self.language:
                raise ValueError(
                    "When country is specified, language must be specified."
                )
            return self._COUNTRY_FORMSET
        if self.language:
            return self._LANGUAGE_FORMSET
        return self._GLOBAL_FORMSET
    
    @property
    def variant(self) -> Optional[str]:
        """Returns the variant component of the Locale."""
        return self.__variant
    
    @property
    def merged(self) -> bool:
        """Returns whether the FormSet has been merged."""
        return self.__merged

    @property
    def processed(self) -> bool:
        """Returns whether the FormSet has been processed."""
        return self.__processed
    
    def _merge(self, depends: "FormSet") -> None:
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
        self.__merged = True

    def process(self, global_constants: Dict[str, str]) -> None:
        """
        Processes all Forms in the FormSet.

        Args:
            global_constants (Dict[str, str]): Global constants to be used during processing.
        """
        for f in self.__forms.values():
            f.process(global_constants, self.__constants, self.__forms)
        self.__processed = True

    @country.setter
    def country(self, value: Optional[str]) -> None:
        """
        Sets the country component of the Locale.
        (translation of setCountry())
        """
        self.__country = value

    @language.setter
    def language(self, value: Optional[str]) -> None:
        """
        Sets the language component of the Locale.
        (translation of setLanguage())
        """
        self.__language = value

    @variant.setter
    def variant(self, value: Optional[str]) -> None:
        """
        Sets the variant component of the Locale.
        (translation of setVariant()
        """
        self.__variant = value

    def __str__(self) -> str:
        """
        Returns a string representation of the FormSet.

        Returns:
            str: A string representation of the FormSet.
        """
        results = [
            f"FormSet: language={self.language}  country={self.country}  variant={self.variant}\n"
        ]
        for form in self.get_forms().values():
            results.append(f"   {form}\n")
        return "".join(results)