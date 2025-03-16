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
from ..routines.abstract_format_validator import AbstractFormatValidator
# from ..GenericValidator import GenericValidator
# from ..util.Locale import Locale

class AbstractNumberValidator(AbstractFormatValidator):
    """
    Abstract base class for Number Validation.

    This is a base class for building Number Validators using format parsing.
    """

    STANDARD_FORMAT: Final[int] = 0 # Standard NumberFormat type
    CURRENCY_FORMAT: Final[int] = 1 # Currency NumberFormat type
    PERCENT_FORMAT:  Final[int] = 2 # Percent NumberFormat type

    def __init__(self, strict: bool, format_type: int, allow_fractions: bool):
        """
        Constructs an instance with specified strict and decimal parameters.
    
        :param strict: True if strict Format parsing should be used.
        :param format_type: The NumberFormat type to create for validation, default is STANDARD_FORMAT.
        :param allow_fractions: True if fractions are allowed or False if integers only.
        """
        super().__init__(strict)
        self._format_type = format_type
        self._allow_fractions = allow_fractions

    def _determine_scale(self): # TODO: need to finish this
        """
        Returns the multiplier of the NumberFormat.
    
        :param format: The NumberFormat to determine the multiplier of.
        :return: The multiplying factor for the format.
        """
        if not self.strict:
            return -1
        if not self.allow_fractions: # or format is integer only
            return 0
        # if minimum fraction != maximum fraction, return -1
    
    def _get_format_locale(self, locale):
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
            return Locale.atof                                          # TODO: this won't work as is
        elif self.format_type == self.PERCENT_FORMAT:
            return Locale.atof if self.allow_fractions else Locale.atoi # TODO: this won't work as is
        else:   # should be STANDARD_FORMAT
            return Locale.atof if self.allow_fractions else Locale.atoi
    
    @override
    def _get_format(self, pattern: str, locale):
        # use_pattern = not GenericValidator.is_blank_or_null(pattern)
        use_pattern = False
        if not use_pattern:
            return self._get_format_locale(locale)
        elif locale is None:
            return # TODO
        else:
            return # TODO
    
    @property
    def format_type(self):
        """
        Indicates the type of NumberFormat created by this validator instance.
    
        :return: The format type created.
        """
        return self._format_type
    
    @property
    def allow_fractions(self):
        """
        Indicates whether the number being validated is a decimal or integer.
    
        :return: True if decimals are allowed or False if the number is an integer.
        """
        return self._allow_fractions
    
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
    def is_valid(self, value: str, pattern: str=None, locale=None):
        """
        Validate using the specified locale.
    
        :param value: The value validation is being performed on.
        :param pattern: The pattern used to validate the value against, or the default for the locale if None.
        :param locale: The locale to use for the date format, system default if null.
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
    
    def _parse(self, value: str, pattern: str, locale):
        """
        Parse the value with the specified patter.
    
        :param value: The value to be parsed.
        :param pattern: The pattern used to validate the value against, or the default for the Locale if None.
        :param locale: The locale to use for the date format, system default if None.
        :return: The parsed value if valid or None if invalid.
        """
        value = value.strip() if value is not None else None
        if value is None or value == "":
        # if GenericValidator.is_blank_or_null(value):
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
