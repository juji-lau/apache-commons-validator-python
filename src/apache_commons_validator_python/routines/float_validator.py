"""
Module Name: float_validator.py

Description: Translates apache.commons.validator.routines.FloatValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/FloatValidator.java

Author: Jessica Breuhaus

License (Taken from apache.commons.validator.routines.FloatValidator.java):
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

from typing import Final, override
from ..routines.abstract_number_validator import AbstractNumberValidator

class FloatValidator(AbstractNumberValidator):
    """Float Validation and Conversion routines.

    This validator provides a number of methods for validating/converting a string value
    to a float to parse either:
        - using the default format for the default locale.
        - using a specified pattern with the default locale.
        - using the default format for a specified locale.
        - using a specified pattern with a specified locale.

    Use the is_valid() method to just validate or one of the validate() methods to
    validate and receive a converted float value.

    So that the same mechanism used for parsing an input value for validation can be used to format output,
    corresponding format() methods are also provided. That is you can format either:
        - using the default format for the default locale.
        - using a specified pattern with the default locale.
        - using the default format for a specified locale.
        - using a specified pattern with a specified locale.
    
    Attributes:
        FLOAT_MIN: The minimum value of a float.
        FLOAT_MAX: The maximum value of a float.
    """

    _VALIDATOR = None
    FLOAT_MIN: Final[float] = 1.175494351E-38 # 32 bit floating point min value
    FLOAT_MAX: Final[float] = 3.402823466E+38 # 32 bit floating point max value

    def __init__(self, strict: bool=True, format_type: int=0):
        """Construct an instance with the specified strict setting and format type or a
        strict instance by default.

        The format_type specifies what type of number format is created. Valid types are:
            - AbstractNumberValidator.STANDARD_FORMAT: to create standard number formats (the default).
            - AbstractNumberValidator.CURRENCY_FORMAT: to create currency number formats.
            - AbstractNumberValidator.PERCENT_FORMAT: to create percent number formats.

        Args:
            strict (bool): `True` if strict parsing should be used, default is `True`.
            format_type (int): The format type to create for validation,
                default is `STANDARD_FORMAT`.
        """
        super().__init__(strict, format_type, True)
    
    @classmethod
    def get_instance(cls):
        """Gets the singleton instance of this validator.

        Returns:
            A singleton instance of the validator.
        """
        if cls._VALIDATOR is None:
            cls._VALIDATOR = FloatValidator()
        return cls._VALIDATOR
    
    @override
    def _process_parsed_value(self, value: str, formatter):
        """Process the parsed value, performing any further validation and type
        conversion required.

        Args:
            value (str): The value validation is being performed on.
            formatter: The format (as a function) used to parse the value.

        Returns:
            The parsed value converted to the appropriate type if valid or `None` if invalid.
        """
        try:
            val = float(formatter(value))
            if val == 0:
                return val
            pos_val = val * -1 if val < 0 else val
            if self.is_in_range(pos_val, self.FLOAT_MIN, self.FLOAT_MAX):
                return val
        except ValueError:
            return None
        
    def validate(self, value: str, pattern: str=None, locale=None):
        """Validate/convert a float using the optional pattern and/or locale.

        Args:
            value (str): The value validation is being performed on.
            pattern (str): The (optional) regex pattern used to validate the value against,
                or the default for the locale if `None`.
            locale (str): The (optional) locale to use for the format, defaults to the system default.
        
        Returns:
            The parsed float if valid or `None` if invalid.
        """
        val = self._parse(value, pattern, locale)
        
        if val is None:
            return val
        
        scale = self._determine_scale(pattern, locale)
        if scale >= 0:
            val = round(val, scale)

        return val
