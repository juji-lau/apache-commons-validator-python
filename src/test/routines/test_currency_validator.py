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

import pytest
import locale as Locale
from src.main.routines.currency_validator import CurrencyValidator
from src.main.routines.abstract_number_validator import AbstractNumberValidator

original = Locale.setlocale(Locale.LC_ALL, None)

class TestBigCurrencyValidator:

    Locale.setlocale(Locale.LC_MONETARY, "en_GB")
    locale_info = Locale.localeconv()
    uk_pound = locale_info['currency_symbol']
    Locale.setlocale(Locale.LC_MONETARY, "en_US")
    locale_info = Locale.localeconv()
    us_dollar = locale_info['currency_symbol']
    
    def test_format_type(self):
        assert CurrencyValidator.get_instance().format_type == 1
        assert CurrencyValidator.get_instance().format_type == AbstractNumberValidator.CURRENCY_FORMAT
    
    def test_integer_invalid(self):
        validator = CurrencyValidator(True, False)

        # Invalid UK - has decimals
        assert validator.is_valid(self.uk_pound + "1,234.56", locale="en_GB") is False, "UK positive"
        assert validator.is_valid('-' + self.uk_pound + "1,234.56", locale="en_GB") is False, "UK negative"

        # Invalid US - has decimals
        assert validator.is_valid(self.us_dollar + "1,234.56", locale="en_US") is False, "US positive"
        assert validator.is_valid('-' + self.us_dollar + "1,234.56", locale="en_US") is False, "US negative"
    
    def test_integer_valid(self):
        validator = CurrencyValidator()
        expected = 1234.00
        negative = -1234.00

        Locale.setlocale(Locale.LC_MONETARY, "en_GB")
        uk_plus = Locale.currency(expected, symbol=True, grouping=True)
        uk_minus = Locale.currency(negative, symbol=True, grouping=True)

        Locale.setlocale(Locale.LC_MONETARY, "en_US")
        us_plus = Locale.currency(expected, symbol=True, grouping=True)
        us_minus = Locale.currency(negative, symbol=True, grouping=True)

        assert validator.validate(us_plus) == expected

        assert validator.validate(uk_plus, locale="en_GB") == expected
        assert validator.validate(uk_minus, locale="en_GB") == negative

        assert validator.validate(us_plus, locale="en_US") == expected
        assert validator.validate(us_minus, locale="en_US") == negative
    
    def test_invalid(self):
        validator = CurrencyValidator.get_instance()

        Locale.setlocale(Locale.LC_MONETARY, "en_GB")
        uk_plus = Locale.currency(1234.56, symbol=True, grouping=True)
        uk_minus = Locale.currency(-1234.56, symbol=True, grouping=True)

        Locale.setlocale(Locale.LC_MONETARY, "en_US")
        us_plus = Locale.currency(1234.56, symbol=True, grouping=True)
        us_minus = Locale.currency(-1234.56, symbol=True, grouping=True)

        # Invalid Missing
        assert validator.is_valid(None) is False
        assert validator.is_valid('') is False
        assert validator.validate(None) is None
        assert validator.validate('') is None

        # Invalid UK
        assert validator.is_valid(us_plus, locale="en_GB") is False
        if uk_minus.startswith('-'):
            assert validator.is_valid('(' + self.uk_pound + "1,234.56)", locale="en_GB") is False
        else:
            assert validator.is_valid('-' + self.uk_pound + "1,234.56)", locale="en_GB") is False

        # Invalid US
        assert validator.is_valid(uk_plus, locale="en_US") is False
        if us_minus.startswith('-'):
            assert validator.is_valid('(' + self.us_dollar + "1,234.56)", locale="en_US") is False
        else:
            assert validator.is_valid('-' + self.us_dollar + "1,234.56)", locale="en_US") is False
    
    def test_pattern(self):
        validator = CurrencyValidator.get_instance()
        # If allowing brackets for negatives, be sure to also allowing a negative sign
        pattern = r"^(-?[£€$¥]?\d{1,3}(,\d{3})*\.\d{3}|\[[£€$¥]?\d{1,3}(,\d{3})*\.\d{3}\])$"
        expected = 1234.567
        negative = -1234.567

        # Test pattern
        assert validator.validate(self.us_dollar + "1,234.567", pattern=pattern) == expected
        assert validator.validate('[' + self.us_dollar + "1,234.567]", pattern=pattern) == negative
        assert validator.validate("1,234.567", pattern=pattern) == expected
        assert validator.validate("[1,234.567]", pattern=pattern) == negative

        # Test pattern & locale
        assert validator.validate(self.uk_pound + "1,234.567", pattern=pattern, locale="en_GB") == expected
        assert validator.validate('[' + self.uk_pound + "1,234.567]", pattern=pattern, locale="en_GB") == negative
        assert validator.validate("1,234.567", pattern=pattern, locale="en_GB") == expected
        assert validator.validate("[1,234.567]", pattern=pattern, locale="en_GB") == negative

        # Invalid
        assert validator.is_valid(self.us_dollar + "1,234.567", pattern=pattern, locale="en_GB") is False
        assert validator.is_valid(self.uk_pound + "1,234.567", pattern=pattern) is False

    def test_valid(self):
        validator = CurrencyValidator.get_instance()
        expected = 1234.56
        negative = -1234.56
        no_decimal = 1234.00
        one_decimal = 1234.50

        Locale.setlocale(Locale.LC_MONETARY, "en_GB")
        uk_plus = Locale.currency(1234.56, symbol=True, grouping=True)
        uk_plus_0decimal = Locale.currency(1234, symbol=True, grouping=True)
        uk_plus_1decimal = Locale.currency(1234.5, symbol=True, grouping=True)
        uk_plus_3decimal = Locale.currency(1234.567, symbol=True, grouping=True)
        uk_minus = Locale.currency(-1234.56, symbol=True, grouping=True)

        Locale.setlocale(Locale.LC_MONETARY, "en_US")
        us_plus = Locale.currency(1234.56, symbol=True, grouping=True)
        us_plus_0decimal = Locale.currency(1234, symbol=True, grouping=True)
        us_plus_1decimal = Locale.currency(1234.5, symbol=True, grouping=True)
        us_plus_3decimal = Locale.currency(1234.567, symbol=True, grouping=True)
        us_minus = Locale.currency(-1234.56, symbol=True, grouping=True)
        
        assert validator.validate(us_plus) == expected
        assert validator.validate(us_plus, locale="en_US") == expected
        assert validator.validate(us_minus, locale="en_US") == negative
        assert validator.validate(us_plus_0decimal, locale="en_US") == no_decimal
        assert validator.validate(us_plus_1decimal, locale="en_US") == one_decimal
        assert validator.validate(us_plus_3decimal, locale="en_US") == (expected + 0.01) # Will round if truncated unlike original
        assert validator.validate("1,234.56", locale="en_US") == expected

        assert validator.validate(uk_plus) is None
        assert validator.validate(uk_plus, locale="en_GB") == expected
        assert validator.validate(uk_minus, locale="en_GB") == negative
        assert validator.validate(uk_plus_0decimal, locale="en_GB") == no_decimal
        assert validator.validate(uk_plus_1decimal, locale="en_GB") == one_decimal
        assert validator.validate(uk_plus_3decimal, locale="en_GB") == (expected + 0.01) # Will round if truncated unlike original
        assert validator.validate("1,234.56", locale="en_GB") == expected
    
    def test_change_locale_to_default(self):
        Locale.setlocale(Locale.LC_ALL, original)
