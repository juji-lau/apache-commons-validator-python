"""
Module Name: currency_validator.py

Description: Translates apache.commons.validator.routines.CurrencyValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/CurrencyValidator.java

Author: Jessica Breuhaus

License (Taken from apache.commons.validator.routines.CurrencyValidator.java):
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

from typing import override
from babel.numbers import get_currency_symbol, get_territory_currencies
from babel.core import Locale
from ..routines.big_decimal_validator import BigDecimalValidator
from ..routines.abstract_number_validator import AbstractNumberValidator

class CurrencyValidator(BigDecimalValidator):
    """Currency Validation and Conversion routines.

    This is one implementation of a currency validator that has the following features:
        - It is lenient about the presence of the currency symbol.
        - It converts the currency to a float.

    Use the is_valid() method to just validate or one of the validate() methods to
    validate and receive a converted big decimal value.

    Fraction/decimal values are automatically rounded to the appropriate length.

    So that the same mechanism used for parsing an input value for validation can be used to format output,
    corresponding format() methods are also provided. That is you can format either:
        - using the default format for the default locale.
        - using a specified pattern with the default locale.
        - using the default format for a specified locale.
        - using a specified pattern with a specified locale.
    """

    _VALIDATOR = None

    def __init__(self, strict: bool=True, allow_fractions: bool=True):
        """Construct an instance with the specified strict setting or a
        strict instance by default.
        
        Args:
            strict (bool): `True` if strict parsing should be used, default is `True`.
            allow_fractions (bool): `True` if fractions are allowed or `False` if ints only,
                default is `True`.

        :param strict: True if strict format parsing should be used.
        :param allow_fractions: True if fractions are allowed or False if integers only.
        """
        super().__init__(strict, AbstractNumberValidator.CURRENCY_FORMAT, allow_fractions)
    
    @classmethod
    def get_instance(cls):
        """Gets the singleton instance of this validator.

        Returns:
            A singleton instance of the validator.
        """
        if cls._VALIDATOR is None:
            cls._VALIDATOR = CurrencyValidator()
        return cls._VALIDATOR
    
    @override
    def _parse(self, value: str, pattern: str, locale: str):
        """Parse the value with the specified pattern and locale.

        This implementation is lenient whether the currency symbol is present or not.
        The default behavior is for the parsing to "fail" if the currency symbol is
        present. This method re-parses with a format without the currency symbol if it
        fails initially.

        Args:
            value (str): The value validation is being performed on.
            pattern (str): The regex pattern used to validate the value against.
            locale (str): The locale to use for the format.

        Returns:
            The parsed value if valid or `None` if invalid.
        """
        if value is None or value == '':
            return None
        
        if value.startswith('[') and value.endswith(']'):
            value = '-' + value[1:-1]
        
        # initial parse of the value
        parsed_value = super()._parse(value, pattern, locale)
        if parsed_value is not None:
            return parsed_value
        
        # get currency symbol
        try:
            locale = "en_US" if locale is None else locale
            l = Locale.parse(locale)
        except Exception:
            return None
        
        currency_symbol = get_currency_symbol((get_territory_currencies(l.territory))[0], locale=locale)
        
        # reparse without the currency symbol
        if value.find(currency_symbol) >= 0:
            value = value.replace(currency_symbol, '').replace(' ', '')
            parsed_value = super()._parse(value, pattern, locale)

            if parsed_value is not None:
                return parsed_value
            
        return None
