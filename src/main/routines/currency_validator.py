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

from typing import override
import locale as Locale
from ..routines.big_decimal_validator import BigDecimalValidator
from ..routines.abstract_number_validator import AbstractNumberValidator

class CurrencyValidator(BigDecimalValidator):
    """
    Currency Validation and Conversion routines.

    This is one implementation of a currency validator that has the following features:
        <li>It is lenient about the presence of the currency symbol</li>
        <li>It converts the currency to a float</li>

    Use the is_valid() method to just validate or one of the validate() methods to
    validate and receive a converted big decimal value.

    Fraction/decimal values are automatically trimmed to the appropriate length.

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

    def __init__(self, strict: bool=True):
        """
        Construct an instance with the specified strict setting and format type or a strict instance by default.
        The format_type specifies what type of number format is created - valid types are:
            <li>AbstractNumberValidator.STANDARD_FORMAT - to create standard number formats (the default).</li>
            <li>AbstractNumberValidator.CURRENCY_FORMAT - to create currency number formats.</li>
            <li>AbstractNumberValidator.PERCENT_FORMAT  - to create percent number formats.</li>

        :param strict: True if strict format parsing should be used.
        :param format_type: The number format type to create for validation, default is CURRENCY_FORMAT.
        """
        super().__init__(strict, AbstractNumberValidator.CURRENCY_FORMAT, True)
    
    @classmethod
    def get_instance(cls):
        """
        Gets the singleton instance of this validator.

        :return: A singleton instance of the validator.
        """
        if cls._VALIDATOR is None:
            cls._VALIDATOR = CurrencyValidator()
        return cls._VALIDATOR
    
    @override
    def _parse(self, value: str, pattern: str, locale: str):
        """
        Parse the value with the specified pattern.

        This implementation is lenient whether the currency symbol is present or not.
        The default behavior is for the parsing to "fail" if the currency symbol is present.
        This method re-parses with a format without the currency symbol if it fails initially.
    
        :param value: The value to be parsed.
        :param pattern: The regex pattern used to validate the value against, or the default for the locale if None.
        :param locale: The locale to use for the format, system default if None.
        :return: The parsed value if valid or None if invalid.
        """
        if value is None or value == '':
            return None
        
        # initial parse of the value
        parsed_value = super()._parse(value, pattern, locale)
        if parsed_value is not None:
            return parsed_value
        
        # get currency symbol
        try:
            locale = "" if locale is None else locale
            Locale.setlocale(Locale.LC_MONETARY, locale)
        except Locale.Error:
            return None
        
        locale_info = Locale.localeconv()
        currency_symbol = locale_info['currency_symbol']
        
        # reparse without the currency symbol
        if value.find(currency_symbol) >= 0:
            value = value.replace(currency_symbol, '').replace(' ', '')
            parsed_value = super()._parse(value, pattern, locale)

            if parsed_value is not None:
                return parsed_value
            
        return None
