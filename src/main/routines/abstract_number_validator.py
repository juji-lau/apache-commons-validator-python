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

from typing import Final, override
import locale as Locale
import re
from ..routines.abstract_format_validator import AbstractFormatValidator
# from ..GenericValidator import GenericValidator

class AbstractNumberValidator(AbstractFormatValidator):
    """
    Abstract base class for Number Validation.

    This is a base class for building Number Validators using format parsing.
    """

    STANDARD_FORMAT: Final[int] = 0 # Standard type
    CURRENCY_FORMAT: Final[int] = 1 # Currency type
    PERCENT_FORMAT:  Final[int] = 2 # Percent type

    def __init__(self, strict: bool, format_type: int, allow_fractions: bool):
        """
        Constructs an instance with specified strict and decimal parameters.
    
        :param strict: True if strict format parsing should be used.
        :param format_type: The format type to create for validation, default is STANDARD_FORMAT.
        :param allow_fractions: True if fractions are allowed or False if integers only.
        """
        super().__init__(strict)
        self.__format_type = format_type
        self.__allow_fractions = allow_fractions

    @override
    def format(self, value, pattern: str=None, locale: str=None):
        """
        Format an object into a string using the specified pattern or locale.
    
        :param value: The value validation is being performed on.
        :param pattern: The (optional) string format to use for the format.
        :param locale: The (optional) locale to use for the format.
        :return: The value formatted as a string.
        """
        try:
            locale = "" if locale is None else locale
            Locale.setlocale(Locale.LC_ALL, locale)
        except Locale.Error:
            return None
        
        if pattern is None:
        # if GenericValidator.is_blank_or_null(pattern):
            if self.format_type == self.PERCENT_FORMAT:
                pattern = "%.2f%" if self.allow_fractions else "%d%"
            elif self.format_type == self.STANDARD_FORMAT:
                pattern = "%.2f" if self.allow_fractions else "%d" # TODO: maybe change pattern to allow more decimal places
        
        if self.format_type == self.CURRENCY_FORMAT:
            return Locale.currency(value, grouping=True)
        elif self.format_type == self.PERCENT_FORMAT:
            return Locale.format_string(pattern, value*100, grouping=True)
        else:   # should be STANDARD_FORMAT
            return Locale.format_string(pattern, value, grouping=True)
        

    def _determine_scale(self, pattern: str, locale: str):
        """
        Returns the multiplier based on the regex pattern and locale.
    
        :param pattern: The pattern used to determine the number of decimal places.
        :param locale: The locale used to determine the number of decimal places.
        :return: The number of decimal places for the format.
        """
        if not self.strict:
            return -1
        if not self.allow_fractions:
            return 0
        
        try:
            locale = "" if locale is None else locale
            Locale.setlocale(Locale.LC_ALL, locale)
        except Locale.Error:
            return None
        
        locale_info = Locale.localeconv()
        
        if pattern is None:
            if self.format_type == self.CURRENCY_FORMAT:
                return locale_info['frac_digits']
            elif self.format_type == self.STANDARD_FORMAT:
                return -1
            else:
                return 2

        decimal_place = locale_info['decimal_point']
        return len(pattern.split(decimal_place)[1].replace('\\', '')) # TODO: support differren
    
    def _get_format_locale(self, locale: str): # UNUSED
        """
        Returns a function used to format for the specified locale.
    
        :param locale: The locale to use for the format, system default if None.
        :return: The function to use for formatting.
        """
        try:
            locale = "" if locale is None else locale
            Locale.setlocale(Locale.LC_NUMERIC, locale)
        except Locale.Error:
            return None

        if self.format_type == self.CURRENCY_FORMAT:
            return Locale.atof
        elif self.format_type == self.PERCENT_FORMAT:
            return Locale.atof if self.allow_fractions else Locale.atoi
        else:   # should be STANDARD_FORMAT
            return Locale.atof if self.allow_fractions else Locale.atoi
    
    @override
    def _get_format(self, pattern: str, locale: str):
        """
        Returns a function used to format for the specified locale.
    
        :param pattern: The regex pattern to use for the format.
        :param locale: The locale to use for the format, system default if None.
        :return: The function to use for formatting.
        """
        try:
            locale = "" if locale is None else locale
            Locale.setlocale(Locale.LC_NUMERIC, locale)
        except Locale.Error:
            return None
        
        Locale.atoi
    
    @property
    def format_type(self):
        """
        Indicates the type of format created by this validator instance.
        The three types are STANDARD_FORMAT, CURRENCY_FORMAT, and PERCENT_FORMAT.
    
        :return: The format type created.
        """
        return self.__format_type
    
    @property
    def allow_fractions(self):
        """
        Indicates whether the number being validated is a decimal or integer.
    
        :return: True if decimals are allowed or False if the number is an integer.
        """
        return self.__allow_fractions
    
    def is_in_range(self, value, min_val, max_val):
        """
        Check if the value is within a specified range.
    
        :param value: The value validation is being performed on.
        :param min_val: The minimum value of the range.
        :param max_val: The maximum value of the range.
        :return: True if the value is within the specified range.
        """
        return min_val <= value and value <= max_val
    
    @override
    def is_valid(self, value: str, pattern: str=None, locale: str=None):
        """
        Validate using the specified locale.
    
        :param value: The value validation is being performed on.
        :param pattern: The regex pattern used to validate the value against, or the default for the locale if None.
        :param locale: The locale to use for the format, system default if null.
        :return: True if the value is valid.
        """
        return self._parse(value, pattern, locale) is not None

    def max_value(self, value, max_val):
        """
        Check if the value is less than or equal to a maximum.
    
        :param value: The value validation is being performed on.
        :param max_val: The maximum value.
        :return: True if the value is less than or equal to the maximum.
        """
        return value <= max_val
    
    def min_value(self, value, min_val):
        """
        Check if the value is greater than or equal to a minimum.
    
        :param value: The value validation is being performed on.
        :param min_val: The minimum value.
        :return: True if the value is greater than or equal to the minimum.
        """
        return value >= min_val
    
    def _check_pattern(self, value: str, pattern: str, locale: str=None):
        """
        Check if the value follows the specified pattern.

        :param value: The value validation is being performed on.
        :param pattern: The regex pattern used to validate the value against.
        :param locale: The locale to use for the format.
        :return: True if the value follows the specified pattern.
        """
        match = re.search(pattern, value)
        if not bool(match):
            return None
        try:
            locale = "" if locale is None else locale
            Locale.setlocale(Locale.LC_NUMERIC, locale)
        except Locale.Error:
            return None
        
        # check that partial match is valid
        locale_info = Locale.localeconv()
        decimal_point = locale_info["decimal_point"]
        if len(match.group(0).split(decimal_point)[0]) == len(value.split(decimal_point)[0]):
            return value.replace(locale_info['thousands_sep'], '')
        return None
     
    def _parse(self, value: str, pattern: str, locale: str):
        """
        Parse the value with the specified pattern.
    
        :param value: The value to be parsed.
        :param pattern: The regex pattern used to validate the value against, or the default for the locale if None.
        :param locale: The locale to use for the format, system default if None.
        :return: The parsed value if valid or None if invalid.
        """
        value = value.strip() if value is not None else None
        if value is None or value == '':
        # if GenericValidator.is_blank_or_null(value):
            return None
        if pattern is not None and value != '':
        # if not GenericValidator.is_blank_or_null(pattern):
            value = self._check_pattern(value, pattern, locale)
            if value is None:
                return None
        formatter = self._get_format(pattern, locale)
        return super()._parse(value, formatter)
    
    @override
    def _process_parsed_value(self, value: str, formatter):
        """
        Process the parsed value, performing any further validation and type conversion required.
    
        :param value: The parsed object created.
        :param formatter: The format used to parse the value with.
        :return: The parsed value converted to the appropriate type if valid or None if invalid.
        """
        raise NotImplementedError("Subclasses must implement this method")
