"""
Module Name: abstract_number_validator.py

Description: Translates apache.commons.validator.routines.AbstractNumberValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/AbstractNumberValidator.java

Author: Jessica Breuhaus

License (Taken from apache.commons.validator.routines.AbstractNumberValidator.java):
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
from babel.numbers import format_decimal, format_currency, get_territory_currencies
from babel.core import Locale
import re
from decimal import Decimal
from ..routines.abstract_format_validator import AbstractFormatValidator
from ..generic_validator_new import GenericValidator
from ..util.decimal_places import max_decimal_places

class AbstractNumberValidator(AbstractFormatValidator):
    """Abstract base class for Number Validation.

    This is a base class for building Number Validators.

    Once a value has been successfully converted the following methods can be used
    to perform minimum, maximum and range checks:
        - min_value() checks whether the value is greater than or equal to a specified minimum.
        - max_value() checks whether the value is less than or equal to a specified maximum.
        - is_in_range() checks whether the value is within a specified range of values.

    Attributes:
        STANDARD_FORMAT (int): Used to indicate the standard format.
        CURRENCY_FORMAT (int): Used to indicate the currency format.
        PERCENT_FORMAT (int): Used to indicate the percent format.
    """

    STANDARD_FORMAT: Final[int] = 0 # Standard type
    CURRENCY_FORMAT: Final[int] = 1 # Currency type
    PERCENT_FORMAT:  Final[int] = 2 # Percent type

    def __init__(self, strict: bool, format_type: int, allow_fractions: bool):
        """Constructs an instance with specified strict and decimal parameters.

        Args:
            strict (bool): `True` if strict parsing should be used.
            format_type (int): The format type to create for validation,
                default is STANDARD_FORMAT.
            allow_fractions (bool): `True` if fractions are allowed or `False` if ints only.
        """
        super().__init__(strict)
        self.__format_type = format_type
        self.__allow_fractions = allow_fractions

    @override
    def format(self, value, pattern: str=None, locale: str=None):
        """Format an object into a string using the specified pattern or locale.

        Args:
            value (int or float): The value to format into a string.
            pattern (str): The (optional) string format to use to format the string.
            locale (str): The (optional) locale to use to format the string.
        
        Returns:
            The value formatted as a str.
        """
        try:
            locale = "en_US" if locale is None else locale
            Locale.parse(locale)
        except Exception:
            return None
        
        if GenericValidator.is_blank_or_null(pattern):
            if self.format_type == self.PERCENT_FORMAT:
                pattern = '#,##0.00%' if self.allow_fractions else '#,##0'
            elif self.format_type == self.STANDARD_FORMAT:
                pattern = '#,##0.0' if self.allow_fractions else '#,##0' # TODO: considering changing pattern to allow more decimal places?
        
        if self.format_type == self.CURRENCY_FORMAT:
            return format_currency(value, get_territory_currencies(locale), locale=locale)
        elif self.format_type == self.PERCENT_FORMAT:
            return format_decimal(value*100, format=pattern, locale=locale)
        else:   # should be STANDARD_FORMAT
            return format_decimal(value, format=pattern, locale=locale)
        

    def _determine_scale(self, pattern: str, locale: str):
        """Returns the multiplier based on the regex pattern and locale.

        Args:
            pattern (str): The regex pattern used to determine the number of decimal places.
            locale (str): The locale used to determine the number of decimal places.
        
        Returns:
            The number of decimal places for the fomat as an int.
        """
        if not self.strict:
            return -1
        if not self.allow_fractions:
            return 0
        
        if GenericValidator.is_blank_or_null(pattern):
            if self.format_type == self.CURRENCY_FORMAT:
                return 2
            elif self.format_type == self.STANDARD_FORMAT:
                return -1
            else:
                return 2
        
        return max_decimal_places(pattern)
    
    @override
    def _get_format(self, pattern: str, locale: str):
        """Returns a function used to format for the specified locale.

        Args:
            pattern (str): The (optional) regex pattern used to validate the value against or `None`
                to use the default for the locale.
            locale (str): The (optional) locale used to validate the value against or `None`
                to use the system default.
        
        Returns:
            The function to use for formatting.
        """
        return Decimal
    
    @property
    def format_type(self):
        """Indicates the type of format created by this validator instance. The three
        types are STANDARD_FORMAT, CURRENCY_FORMAT, and PERCENT_FORMAT.

        Returns:
            The format type created.
        """
        return self.__format_type
    
    @property
    def allow_fractions(self):
        """Indicates whether the number being validated is a decimal or integer.

        Returns:
            `True` if decimals are allowed or `False` if ints only.
        """
        return self.__allow_fractions
    
    def is_in_range(self, value, min_val, max_val):
        """Check if the value is within a specified range.

        Args:
            value (int or float): The value to check.
            min_val (int or float): The minimum value of the range.
            max_val (int or float): The maximum value of the range.
        
        Returns:
            `True` if the value is within the specified range.
        """
        return min_val <= value and value <= max_val
    
    @override
    def is_valid(self, value: str, pattern: str=None, locale: str=None):
        """Validate using the specified locale.

        Args:
            value (str): The value validation is being performed on.
            pattern (str): The (optional) regex pattern used to validate the value against.
            locale (str): The (optional) locale to use for the format,
                defaults to the system default.
            
        Returns:
            `True` if the value is valid.
        """
        return self._parse(value, pattern, locale) is not None

    def max_value(self, value, max_val):
        """Check if the value is less than or equal to a maximum.

        Args:
            value (int or float): The value to check.
            max_value (int or float): The maximum value.
        
        Returns:
            `True` if the value is less than or equal to the maximum.
        """
        return value <= max_val
    
    def min_value(self, value, min_val):
        """Check if the value is greater than or equal to a minimum.

        Args:
            value (int or float): The value to check.
            min_value (int or float): The minimum value.

        Returns:
            `True` if the value is greater than or equal to the minimum.
        """
        return value >= min_val
    
    def _check_pattern(self, value: str, pattern: str, locale: str=None):
        """Check if the value follows the specified pattern.

        Args:
            value (str): The value validation is being performed on.
            pattern (str): The regex pattern used to validate the value against.
            locale (str): The (optional) locale to use for the format,
                defaults to the system default.
        
        Returns:
            `True` if the value follows the specified pattern.
        """
        if self.strict and not re.fullmatch(pattern, value):
            return None
        
        match = re.search(pattern, value)
        if not bool(match):
            return None
        try:
            locale = "en_US" if locale is None else locale
            locale = Locale.parse(locale)
        except Exception:
            return None
        
        value = re.sub(r"[A-Za-z]", '', value)
        
        # check that partial match is valid
        decimal_point = locale.number_symbols.get('decimal')
        thousands_sep = locale.number_symbols.get('group')
        if len(match.group(0).split(decimal_point)[0]) == len(value.split(decimal_point)[0]):
            return value.replace(thousands_sep, '')
        return None
     
    def _parse(self, value: str, pattern: str, locale: str):
        """Parse the value with the specified pattern and locale.

        Args:
            value (str): The value validation is being performed on.
            pattern (str): The regex pattern used to validate the value against.
            locale (str): The locale to use for the format.

        Returns:
            The parsed value if valid or `None` if invalid.
        """
        value = value.strip() if value is not None else None
        if GenericValidator.is_blank_or_null(value):
            return None

        if value[-1].isalpha():
            if self.strict:
                return None
            else:
                value = value[0:-1]

        if not GenericValidator.is_blank_or_null(pattern):
            value = self._check_pattern(value, pattern, locale)
            if value is None:
                return None

        try:
            locale = "en_US" if locale is None else locale
            locale = Locale.parse(locale)
        except Exception:
            return None

        decimal_point = locale.number_symbols.get('decimal')
        thousands_sep = locale.number_symbols.get('group')

        if self.strict and (not self.allow_fractions) and value.count(decimal_point) > 0:
            return None
        
        value = value.replace(thousands_sep, '').replace(decimal_point, '.')
        formatter = self._get_format(pattern=pattern, locale=locale)
        return super()._parse(value, formatter)
    
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
        raise NotImplementedError("Subclasses must implement this method")
