"""
Module Name: abstract_format_validator.py

Description: Translates apache.commons.validator.routines.AbstractFormatValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/AbstractFormatValidator.java

Author: Jessica Breuhaus

License (Taken from apache.commons.validator.routines.AbstractFormatValidator.java):
    Licensed to the Apache Software Foundation (ASF) under one or more
    contributor license agreements.  See the NOTICE file distributed with
    this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0
    (the "License"); you may not use this file except in compliance with
    the License.  You may obtain a copy of the License at

        http:#www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from abc import ABC
from decimal import InvalidOperation

class AbstractFormatValidator(ABC):
    """Abstract class for format based Validation.

    This is a base class for building Date and Number Validators using format parsing.
    """
    serializable = True
    cloneable = True

    def __init__(self, strict: bool):
        """Constructs an instance with the specified strict setting.

        Args:
            strict (bool): `True` if strict parsing will be used.
        """
        self.__strict = strict

    def format(self, value, pattern: str=None, locale: str=None):
        """Format an object into a string using the specified pattern or locale.

        Args:
            value (int or float): The value to format into a string.
            pattern (str): The (optional) string format to use to format the string.
            locale (str): The (optional) locale to use to format the string.
        
        Returns:
            The value formatted as a str.
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def _get_format(self, pattern: str=None, locale: str=None):
        """Returns a format for the specified pattern and/or locale.

        Args:
            pattern (str): The (optional) regex pattern used to validate the value against or `None`
                to use the default for the locale.
            locale (str): The (optional) locale used to validate the value against or `None`
                to use the system default.
        
        Returns:
            The function to use for formatting.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @property
    def strict(self):
        """Indicates whether validated values should adhere strictly to the format used.

        Returns:
            `True` if strict parsing will be used.
        """
        return self.__strict
    
    def is_valid(self, value: str, pattern: str=None, locale: str=None):
        """Validate using the specified pattern and/or locale or the default if no
        pattern and/or locale is given.

        Args:
            value (str): The value validation is being performed on.
            pattern (str): The (optional) regex pattern used to validate the value against.
            locale (str): The (optional) locale to use for the format,
                defaults to the system default.
            
        Returns:
            `True` if the value is valid.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def _parse(self, value: str, formatter):
        """Parse the value with the specified format.

        Args:
            value (str): The value to be parsed.
            formatter: The format (as a function) used to parse the value.
        
        Return:
            The parsed value if valid or `None` if invalid.
        """
        if formatter is None:
            return None

        try:
            parsed_value = formatter(value)
        except InvalidOperation:
            return None
        
        if parsed_value is not None:
            parsed_value = self._process_parsed_value(value, formatter)

        return parsed_value
    
    def _process_parsed_value(self, value: str, formatter):
        """Process the parsed value, performing any further validation and type
        conversion required.

        Args:
            value (str): The value validation is being performed on.
            formatter: The format (as a function) used to parse the value.

        Returns:
            The parsed value converted to the appropriate type if valid or `None` if invalid.
        """
        raise NotImplementedError("Subclasses must implement this method")
