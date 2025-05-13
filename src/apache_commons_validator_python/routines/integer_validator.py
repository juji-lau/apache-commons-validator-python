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

from typing import Final, override
from ..routines.abstract_number_validator import AbstractNumberValidator

class IntegerValidator(AbstractNumberValidator):
    """Integer Validation</strong> and Conversion routines ({@code java.lang.Integer}).

    This validator provides a number of methods for validating/converting a string value
    to an integer to parse either:
        <li>using the default format for the default locale</li>
        <li>using a specified pattern with the default locale</li>
        <li>using the default format for a specified locale</li>
        <li>using a specified pattern with a specified locale</li>

    Use the is_valid() method to just validate or one of the validate() methods to
    validate and receive a converted integer value.

    Once a value has been successfully converted the following methods can be used
    to perform minimum, maximum and range checks:
        <li>min_value() checks whether the value is greater than or equal to a specified minimum.</li>
        <li>max_value() checks whether the value is less than or equal to a specified maximum.</li>
        <li>is_in_range() checks whether the value is within a specified range of values.</li>

    So that the same mechanism used for parsing an input value for validation can be used to format output,
    corresponding format() methods are also provided. That is you can format either:
        <li>using the default format for the default locale</li>
        <li>using a specified pattern with the default locale</li>
        <li>using the default format for a specified locale</li>
        <li>using a specified pattern with a specified locale</li>
    """

    _VALIDATOR = None
    INT_MIN:   Final[int] = -2**31
    INT_MAX:   Final[int] = 2**31 - 1

    def __init__(self, strict: bool=True, format_type: int=0):
        """Construct an instance with the specified strict setting and format type or a
        strict instance by default.

        The format_type specifies what type of number format is created - valid types are:
            <li>AbstractNumberValidator.STANDARD_FORMAT - to create standard number formats (the default).</li>
            <li>AbstractNumberValidator.CURRENCY_FORMAT - to create currency number formats.</li>
            <li>AbstractNumberValidator.PERCENT_FORMAT  - to create percent number formats.</li>

        :param strict: True if strict format parsing should be used.
        :param format_type: The number format type to create for validation, default is STANDARD_FORMAT.
        """
        super().__init__(strict, format_type, False)

    @classmethod
    def get_instance(cls):
        """Gets the singleton instance of this validator.

        :return: A singleton instance of the validator.
        """
        if cls._VALIDATOR is None:
            cls._VALIDATOR = IntegerValidator()
        return cls._VALIDATOR
    
    def is_in_range(self, value: int, min_val: int, max_val: int):
        """Check if the value is within a specified range.

        :param value: The number value to check.
        :param min_val: The minimum value of the range.
        :param max_val: The maximum value of the range.
        :return: True if the value is within the specified range.
        """
        return min_val <= value and value <= max_val
    
    def max_value(self, value: int, max_val: int):
        """Check if the value is less than or equal to a maximum.

        :param value: The value validation is being performed on.
        :param max_val: The maximum value.
        :return: True if the value is less than or equal to the maximum.
        """
        return value <= max_val
    
    def min_value(self, value: int, min_val: int):
        """Check if the value is greater than or equal to a minimum.

        :param value: The value validation is being performed on.
        :param min_val: The minimum value.
        :return: True if the value is greater than or equal to the minimum.
        """
        return value >= min_val
    
    @override
    def _process_parsed_value(self, value: str, formatter):
        """Process the parsed value, performing any further validation and type
        conversion required.

        :param value: The value of the parsed object created.
        :param formatter: The format used to parse the value with.
        :return: The parsed value converted to the appropriate type if valid or None if
            invalid.
        """
        try:
            val = int(formatter(value))
            if self.is_in_range(val, self.INT_MIN, self.INT_MAX):
                return val
        except ValueError:
            return None
        
    def validate(self, value: str, pattern: str=None, locale=None):
        """Validate/convert an integer using the default locale.

        :param value: The value validation is being performed on.
        :param pattern: The (optional) regex pattern used to validate the value against,
            or the default for the locale if None.
        :param locale: The (optional) locale to use for the format, system default if
            None.
        :return: The parsed integer (as an int) if valid or None if invalid.
        """
        val = self._parse(value, pattern, locale)
        
        if val is None:
            return val
        
        return val
