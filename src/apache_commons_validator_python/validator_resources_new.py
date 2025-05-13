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

from __future__ import annotations
import logging
from urllib.request import urlopen
import locale
from typing import IO, Any, Dict, List, Optional, Final, Union

class ValidatorResources:
    """General purpose class for storing FormSet objects based on their associated
    locale.
    
    The xml files being passed in need to match the structure detailed below:
    <form-validation>
    ├── <global>
    │   ├── <validator>
    │   │   ├── name (attribute, required)
    │   │   ├── classname (attribute, required)
    │   │   ├── method (attribute, optional, defaults to 'validate')
    │   │   ├── methodParams (attribute, optional)
    │   │   ├── depends (attribute, optional)
    │   │   └── msg (attribute, optional; default error message key)
    │   ├── <constant>
    │   │   ├── <constant-name> (text, required)
    │   │   └── <constant-value> (text, required)
    │   └── ... (multiple <validator> and <constant> allowed)
    │
    ├── <formset>
    │   ├── language (attribute, optional)
    │   ├── country (attribute, optional)
    │   └── <form>
    │       ├── name (attribute, required)
    │       └── <field>
    │           ├── property (attribute, required)
    │           ├── depends (attribute, optional; comma-separated validator names)
    │           ├── page (attribute, optional; for multi-page forms)
    │           ├── indexedListProperty (attribute, optional)
    │           ├── indexedProperty (attribute, optional)
    │           ├── key (attribute, optional; alternate for message bundle)
    │           ├── <arg0> to <arg3> (optional; provides values for messages)
    │           │   ├── key (attribute, required)
    │           │   ├── name (attribute, optional)
    │           │   └── resource (attribute, optional, default true)
    │           ├── <msg> (optional; overrides default validator message)
    │           │   ├── name (attribute, required; matches a validator)
    │           │   └── key (attribute, required; message key)
    │           ├── <var> (optional; parameter to validator)
    │           │   ├── <var-name> (text, required)
    │           │   └── <var-value> (text, required)
    │           └── ... (multiple <arg>, <msg>, <var> allowed)
    │
    └── ... (multiple <formset> allowed, one per locale if needed)
    """

    __VALIDATOR_RULES: Final[List[str]] = [
        "src/apache_commons_validator_python/resources/digester-rules.xml",  #: Path to the XML rules file used by the digester. (local)
        "apache_commons_validator_python/resources/digester-rules.xml" #: path to the XML file by the digester. (package)
    ]

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
    #: Is the class serializable

    cloneable = False
    #: is the class cloneable

    def __init__(self, sources: Optional[List[str]] = None):
        """_summary_

        Args:
            sources (Optional[List[str]], optional): list of file paths. Defaults to None.

        Raises:
            ValueError
        """
        
        self.__logger = logging.getLogger(__name__)
        #: logger 

        self._h_form_sets: Dict[str, 'FormSet'] = {}
        #: All `FormSet` objects stored in this object.

        self._h_constants: Dict[str, str] = {}
        #: All constants stored in this object,

        self._h_actions: Dict[str, 'ValidatorAction'] = {}
        #: All `ValidatorAction`s stored in this object. 

        self._default_form_set: Optional['FormSet'] = None
        #: Default `FormSet`

        if sources:
            if not isinstance(sources, list):
                sources = [sources]

            # from ..util.digester import Digester
            from .util.digester import Digester
            digester = Digester(root_object=self)

            try:
                digester.load_rules(self.__VALIDATOR_RULES[0]) # local
            except:
                digester.load_rules(self.__VALIDATOR_RULES[1]) # package

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

    def _get_form_sets(self) -> Dict[str, Any]:
        """Returns a Dictionary of FormSet objects indexed by locale keys."""
        return self._h_form_sets

    def _get_actions(self) -> Dict[str, Any]:
        """Dictionary of ValidatorAction objects indexed by name."""
        return self._h_actions

    def _get_constants(self) -> Dict[str, str]:
        """Dictionary of global constants."""
        return self._h_constants

    def add_constant(self, name: str, value: str) -> None:
        """Add a global constant to the resource.

        Args:
            name (str): name of the global constant
            value (str): value of the global constant
        """
        self.__logger.debug(f"Adding Global Constant: {name}, {value}")
        self._h_constants[name] = value

    def add_form_set(self, form_set: 'FormSet') -> None:
        """Add a FormSet to this ValidatorResources object.

        Args:
            form_set (FormSet): FormSet to add 
        """
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

    def get_form(self, *args) -> "Form":
        """Gets a Form based on either on language, country, variant and formkey or
        locale and form key.

        Raises:
            ValueError: 

        Returns:
            form (Form)
        """
        if len(args) == 4:  # language, country, variant, form_key
            return self._get_form_with_locale(*args)
        elif len(args) == 2:  # Locale object, form_key
            return self._get_form_with_locale_obj(*args)
        raise ValueError("Invalid arguments")

    def _get_form_with_locale(self, language: str, country: str, variant: str, form_key: str) -> "Form":
        """Gets a Form based on language, country, variant, and form key.

        Args:
            language (str): 
            country (str)
            variant (str)
            form_key (str)

        Returns:
            form with locale or None.
        """
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

    def _get_form_with_locale_obj(self, locale_obj: "Locale", form_key: str) -> "Form":
        """Gets a Form based on locale and form key.

        Args:
            locale_obj (Locale)
            form_key (str)

        Returns:
            Form with locale object and form key.
        """
        return self._get_form_with_locale(
            locale_obj.language, locale_obj.country, locale_obj.variant, form_key
        )

    def _build_key(self, form_set: 'FormSet') -> str:
        """Build locale key using language, country, and variant from form_set

        Args:
            form_set (FormSet): FormSet from which to build locale key

        Returns:
            str: locale key 
        """
        return self.build_locale(form_set.language, form_set.country, form_set.variant)

    def build_locale(self, lang: str, country: str, variant: str) -> str:
        """Assembles a locale code from given parts.

        Args:
            lang (str): 
            country (str): 
            variant (str): 

        Returns:
            str
        """
        return "_".join(filter(None, [lang, country, variant]))

    def add_validator_action(self, validator_action: 'ValidatorAction') -> None:
        """Add a ValidatorAction to the resource.

        Args:
            validator_action (ValidatorAction): ValidatorAction to add to the resource.
        """
        validator_action.init()
        self._h_actions[validator_action.name] = validator_action
        self.__logger.debug(
            f"Add ValidatorAction: {validator_action.name},{validator_action.class_name}"
        )

    def get_validator_action(self, key: str) -> Optional['ValidatorAction']:
        """Gets the ValidatorAction associated with the key.

        Returns:
            ValidatorAction | None
        """
        return self._h_actions.get(key)

    def get_validator_actions(self) -> Dict[str, 'ValidatorAction']:
        """Returns a copy of the ValidatorActions in this resources."""
        return dict(self._h_actions)  # Return a copy to prevent modification

    def process(self):
        """Processes the ValidatorResources object."""
        self.__logger.debug("Processing ValidatorResources")
        if self._default_form_set:
            self._default_form_set.process(self._h_constants)
        for form_set in self._h_form_sets.values():
            form_set.process(self._h_constants)