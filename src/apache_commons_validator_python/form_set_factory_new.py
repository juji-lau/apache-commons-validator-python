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

import logging
from typing import Optional

from .form_set_new import FormSet

class FormSetFactory:
    """Factory class used to create FormSet instances."""

    def __init__(self):
        """Initializes a FormSetFactory instance with a logger."""

        self.__log: Optional[logging.Logger] = logging.getLogger(__name__)
        #: Logging

    def create_form_set(
        self,
        resources: "ValidatorResources",
        language: Optional[str],
        country: Optional[str],
        variant: Optional[str],
    ) -> "FormSet":
        """Creates or retrieves a FormSet based on the locale attributes.

        Args:
            resources (ValidatorResources): The validator resources containing form sets.
            language (Optional[str]): The locale's language.
            country (Optional[str]): The locale's country.
            variant (Optional[str]): The locale's variant.

        Returns:
            FormSet: The FormSet instance for the given locale.
        """

        # Retrieve existing FormSet for the given locale
        key = resources.build_locale(language, country, variant)
        form_set = resources._get_form_sets().get(key)
        if form_set:
            if self.__get_log().isEnabledFor(logging.DEBUG):
                self.__get_log().debug(f"FormSet[{form_set.display_key()}] found - merging.")
            return form_set

        # from ..form_set_new import FormSet
        from .form_set_new import FormSet
        # Create a new FormSet instance
        if form_set is None:
            form_set = FormSet()
            form_set.language = language
            form_set.country = country
            form_set.variant = variant
            resources._get_form_sets()[key] = form_set

        # Add the new FormSet to the resources
        resources.add_form_set(form_set)

        if self.__get_log().isEnabledFor(logging.DEBUG):
            self.__get_log().debug(f"FormSet[{form_set.display_key()}] created.")

        return form_set

    def create_object(
        self, attributes, resources: "ValidatorResources"
    ) -> "FormSet":
        """Creates or retrieves a FormSet based on XML attributes.

        Args:
            attributes (Attributes): The SAX attributes for the FormSet element.
            resources (ValidatorResources): The validator resources.

        Returns:
            FormSet: The created or retrieved FormSet instance.
        """
        language = attributes.get("language")
        country = attributes.get("country")
        variant = attributes.get("variant")

        return self.create_form_set(resources, language, country, variant)

    def __get_log(self) -> logging.Logger:
        """Returns the logger."""
        if self.__log is None:
            self.__log = logging.getLogger(__name__)
        return self.__log