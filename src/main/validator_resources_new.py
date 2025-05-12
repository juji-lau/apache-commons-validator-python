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

from __future__ import annotations
import logging
from urllib.request import urlopen
import locale
from typing import IO, Dict, List, Optional, Final, Union

class ValidatorResources:
    """
    General purpose class for storing FormSet objects based on their associated locale.
    """

    __VALIDATOR_RULES: Final[str] = (
        "src/resources/digester-rules.xml"  #: Path to the XML rules file used by the digester.
    )

    __REGISTRATIONS: Final[Dict[str, str]] = {
        "-//Apache Software Foundation//DTD Commons Validator Rules Configuration 1.0//EN": "/org/apache/commons/validator/resources/validator_1_0.dtd",
        "-//Apache Software Foundation//DTD Commons Validator Rules Configuration 1.0.1//EN": "/org/apache/commons/validator/resources/validator_1_0_1.dtd",
        "-//Apache Software Foundation//DTD Commons Validator Rules Configuration 1.1//EN": "/org/apache/commons/validator/resources/validator_1_1.dtd",
        "-//Apache Software Foundation//DTD Commons Validator Rules Configuration 1.1.3//EN": "/org/apache/commons/validator/resources/validator_1_1_3.dtd",
        "-//Apache Software Foundation//DTD Commons Validator Rules Configuration 1.2.0//EN": "/org/apache/commons/validator/resources/validator_1_2_0.dtd",
        "-//Apache Software Foundation//DTD Commons Validator Rules Configuration 1.3.0//EN": "/org/apache/commons/validator/resources/validator_1_3_0.dtd",
        "-//Apache Software Foundation//DTD Commons Validator Rules Configuration 1.4.0//EN": "/org/apache/commons/validator/resources/validator_1_4_0.dtd",
    }  #: Mapping of DTD public identifiers to resource paths.

    _DEFAULT_LOCALE: str = (
        locale.getlocale()[0] or "en_US"
    )  #: Default locale based on system settings.

    serializable = True
    cloneable = False
    
    def __init__(self, sources: Optional[Union[List[Union[str, IO, object]], Union[str, IO, object]]] = None):
        self.__logger = logging.getLogger(__name__)
        self._h_form_sets: Dict[str, 'FormSet'] = {}
        self._h_constants: Dict[str, str] = {}
        self._h_actions: Dict[str, 'ValidatorAction'] = {}
        self._default_form_set: Optional['FormSet'] = None

        if sources:
            if not isinstance(sources, list):
                sources = [sources]

            from src.main.util.digester import Digester
            digester = Digester(root_object=self)
            digester.load_rules(self.__VALIDATOR_RULES)

            for source in sources:
                if isinstance(source, str):
                    digester.parse(source)
                elif hasattr(source, "read"):
                    digester.parse(source)
                elif hasattr(source, 'geturl'):
                    with urlopen(source.geturl()) as f:
                        digester.parse(f)
                else:
                    raise ValueError(f"Unsupported source type: {type(source)}")

            self.process()

    def _get_form_sets(self):
        """Returns a Dictionary of FormSet objects indexed by locale keys."""
        return self._h_form_sets

    def _get_actions(self):
        """Dictionary of ValidatorAction objects indexed by name."""
        return self._h_actions

    def _get_constants(self):
        """Dictionary of global constants."""
        return self._h_constants

    def add_constant(self, name: str, value: str):
        """Add a global constant to the resource."""
        self.__logger.debug(f"Adding Global Constant: {name}, {value}")
        self._h_constants[name] = value

    def add_form_set(self, form_set: 'FormSet'):
        """Add a FormSet to this ValidatorResources object."""
        key = self._build_key(form_set)
        if not key:  # default FormSet
            if self._default_form_set != None:
                self.__logger.debug("Overriding default FormSet definition.")
            self._default_form_set = form_set
        else:
            if self._h_form_sets == None:
                self.__logger.debug(f"Adding FormSet '{form_set}'.")
            else:
                self.__logger.debug(
                    f"Overriding FormSet definition. Duplicate for locale {key}."
                )
            self._h_form_sets[key] = form_set

    def get_form(self, *args):
        """Gets a Form based on either on language, country, variant and formkey or locale and form key"""
        if len(args) == 4:  # language, country, variant, form_key
            return self._get_form_with_locale(*args)
        elif len(args) == 2:  # Locale object, form_key
            return self._get_form_with_locale_obj(*args)
        raise ValueError("Invalid arguments")

    def _get_form_with_locale(self, language, country, variant, form_key):
        """Gets a Form based on language, country, variant, and form key."""
        form = None

        # Try language/country/variant
        key = self.build_locale(language, country, variant)
        if key is not None and key in self._h_form_sets:
            form_set = self._h_form_sets[key]
            if form_set is not None:
                form = form_set.get_form(form_key)
        locale_key: Final[str] = key

        # Try language/country
        if form is None:
            key = self.build_locale(language, country, None)
            if key is not None and key in self._h_form_sets:
                form_set: Final['FormSet'] = self._h_form_sets[key]
                if form_set is not None:
                    form = form_set.get_form(form_key)

        # Try language
        if form is None:
            key = self.build_locale(language, None, None)
            if key is not None and key in self._h_form_sets:
                form_set: Final['FormSet'] = self._h_form_sets[key]
                if form_set is None:
                    form = form_set.get_form(form_key)

        # Try default formset
        if form is None:
            try:
                form = self._default_form_set.get_form(form_key)
                key = "default"
            except:
                pass

        if form is None:
            self.__logger.debug(f"Form '{form_key}' is not found for locale '{locale_key}'.")
        else:
            self.__logger.debug(
                f"Form '{form_key}' found in formset '{key}' for locale '{locale_key}'"
            )

        return form

    def _get_form_with_locale_obj(self, locale_obj, form_key):
        """Gets a Form based on locale and form key."""
        return self._get_form_with_locale(
            locale_obj.language, locale_obj.country, locale_obj.variant, form_key
        )

    def _build_key(self, form_set: 'FormSet') -> str:
        return self.build_locale(form_set.language, form_set.country, form_set.variant)

    def build_locale(self, lang: str, country: str, variant: str) -> str:
        """Assembles a locale code from given parts."""
        return "_".join(filter(None, [lang, country, variant]))

    def add_validator_action(self, validator_action: 'ValidatorAction'):
        """Add a ValidatorAction to the resource."""
        validator_action.init()
        self._h_actions[validator_action.name] = validator_action
        self.__logger.debug(
            f"Add ValidatorAction: {validator_action.name},{validator_action.class_name}"
        )

    def get_validator_action(self, key: str) -> Optional['ValidatorAction']:
        return self._h_actions.get(key)

    def get_validator_actions(self) -> Dict[str, 'ValidatorAction']:
        return dict(self._h_actions)  # Return a copy to prevent modification

    def process(self):
        """Processes the ValidatorResources object."""
        self.__logger.debug("Processing ValidatorResources")
        if self._default_form_set:
            self._default_form_set.process(self._h_constants)
        for form_set in self._h_form_sets.values():
            form_set.process(self._h_constants)