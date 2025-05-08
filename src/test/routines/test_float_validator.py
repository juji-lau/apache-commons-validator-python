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
from typing import Final
from src.main.routines.float_validator import FloatValidator
from .test_abstract_number_validator import TestAbstractNumberValidator

class TestFloatValidator(TestAbstractNumberValidator):

    _FLOAT_MAX: Final[float] = 3.402823466E+38     # 32 bit floating point max value
    _FLOAT_MIN: Final[float] = 1.175494351E-38     # 32 bit floating point max value

    @pytest.fixture(autouse=True)
    def set_up(self):
        self._validator = FloatValidator(strict=False)
        self._strict_validator = FloatValidator()
        self._test_pattern = r"^((\d{1,3}(,\d{3})+)|\d+)?(\.\d+)?$" # TODO ???
        self._max = self._FLOAT_MAX
        self._max_plus_one = self._FLOAT_MAX * 10
        self._min = self._FLOAT_MAX * -1
        self._min_minus_one = self._FLOAT_MAX * -10
        self._invalid = [None, '', 'X', "X12"]
        self._invalid_strict = [None, '', 'X', "X12", "12X", "1X2"]
        self._test_number = 1234.5
        self._test_zero = 0
        self._valid_strict = ['0', "1234.5", "1,234.5"]
        self._valid_strict_compare = [self._test_zero, self._test_number, self._test_number]
        # self._valid = ['0', "1234.5", "1,234.5", "1,234.5", "1234.5X"]
        self._valid = ['0', "1234.5", "1,234.5", "1,234.5"]
        self._valid_compare = [self._test_zero, self._test_number, self._test_number, self._test_number, self._test_number]
        self._test_string_us = "1,234.5"
        self._test_string_de = "1.234,5"
        self._locale_value = self._test_string_de
        self._locale_pattern = r"\d.\d\d\d,\d"
        self._test_locale = "de_DE"
        self._locale_expected = self._test_number

    def test_float_range_min_max(self):
        validator = FloatValidator(strict=False)

        number9  = validator.validate("9")
        number10 = validator.validate("10")
        number11 = validator.validate("11")
        number19 = validator.validate("19")
        number20 = validator.validate("20")
        number21 = validator.validate("21")
        min = 10
        max = 20

         # test is_in_range()
        assert validator.is_in_range(number9, min, max) is False  # less than range
        assert validator.is_in_range(number10, min, max) is True  # equal to min
        assert validator.is_in_range(number11, min, max) is True  # in range
        assert validator.is_in_range(number20, min, max) is True  # equal to max
        assert validator.is_in_range(number21, min, max) is False # greater than range

        # test min_val()
        assert validator.min_value(number9, min) is False # less than min
        assert validator.min_value(number10, min) is True # equal to min
        assert validator.min_value(number11, min) is True # greater than min

        # test max_val()
        assert validator.max_value(number19, max) is True  # less than max
        assert validator.max_value(number20, max) is True  # equal to max
        assert validator.max_value(number21, max) is False # greater than max

    def test_float_smallest_values(self):
        # validate smallest +ve float value
        smallest_pos = self._FLOAT_MIN
        str_smallest_value = str(smallest_pos)
        assert smallest_pos == FloatValidator.get_instance().validate(str_smallest_value)

        # validate smallest -ve float value
        smallest_neg = self._FLOAT_MIN * -1
        str_smallest_value = str(smallest_neg)
        assert smallest_neg == FloatValidator.get_instance().validate(str_smallest_value)

        # validate too small +ve float value
        too_small_value = self._FLOAT_MIN / 10
        str_too_small_value = str(too_small_value)
        assert FloatValidator.get_instance().is_valid(str_too_small_value) is False

        # validate too small -ve float value
        too_small_value = (self._FLOAT_MIN * -1) / 10
        str_too_small_value = str(too_small_value)
        assert FloatValidator.get_instance().is_valid(str_too_small_value) is False
    
    def test_float_largest_values(self):
        # validate largest +ve float value
        largest_value = self._FLOAT_MAX
        str_largest_value = str(largest_value)
        assert largest_value == FloatValidator.get_instance().validate(str_largest_value)

        # validate largest -ve float value
        largest_value = self._FLOAT_MAX * -1
        str_largest_value = str(largest_value)
        assert largest_value == FloatValidator.get_instance().validate(str_largest_value)

        # validate too large +ve float value
        too_large_value = self._FLOAT_MAX * 10
        str_too_large_value = str(too_large_value)
        assert FloatValidator.get_instance().is_valid(str_too_large_value) is False

        # validate too large -ve float value
        too_large_value = self._FLOAT_MAX * -10
        str_too_large_value = str(too_large_value)
        assert FloatValidator.get_instance().is_valid(str_too_large_value) is False

    def test_float_validator_methods(self):
        locale_us = "en_US"
        locale_de = "de_DE"
        locale_fr = "fr_FR"
        pattern = r"\d,\d\d.\d\d"
        partial_pattern = r"\d,\d\d.\d"
        us_val = "123.45"
        de_val = "123,45"
        fr_val = "123,45"
        neg_val = "-123.45"
        pattern_val = "1,23.45"
        expected = 123.45
        expected_neg = -123.45

        # Test positive number
        assert FloatValidator.get_instance().is_valid(us_val) is True
        assert FloatValidator.get_instance().validate(us_val) == expected

        # Test negative number
        assert FloatValidator.get_instance().is_valid(neg_val) is True
        assert FloatValidator.get_instance().validate(neg_val) == expected_neg

        # Test pattern
        assert FloatValidator.get_instance().is_valid(pattern_val, pattern=pattern) is True
        assert FloatValidator.get_instance().validate(pattern_val, pattern=pattern) == expected
        assert FloatValidator.get_instance().is_valid(pattern_val, pattern=partial_pattern) is False

        # Test different locales
        assert FloatValidator.get_instance().validate(us_val, locale=locale_us) == expected
        assert FloatValidator.get_instance().validate(de_val, locale=locale_de) == expected
        assert FloatValidator.get_instance().validate(fr_val, locale=locale_fr) == expected

        us_val = "1234.567"
        expected = 1234.567

        # Test thousands with no separator
        assert FloatValidator.get_instance().is_valid(us_val) is True
        assert FloatValidator.get_instance().validate(us_val) == expected

        us_val = FloatValidator.get_instance().format(1234.567, pattern="%.3f", locale='en_US')
        de_val = FloatValidator.get_instance().format(1234.567, pattern="%.3f", locale='de_DE')
        fr_val = FloatValidator.get_instance().format(1234.567, pattern="%.3f", locale='fr_FR')
        validator = FloatValidator(strict=False)

        # Test with thousands separator
        assert validator.validate(us_val, locale=locale_us) == expected
        assert validator.validate(de_val, locale=locale_de) == expected
        assert validator.validate(fr_val, locale=locale_fr) == expected

        pattern = r"\d,\d\d\d.\d\d\d"
        pattern_val = "1,234.567"

        # Test thousands with pattern
        assert validator.validate(pattern_val, pattern=pattern) == expected
        assert validator.validate(pattern_val, pattern=pattern, locale=locale_us) == expected

        locale = "de_DE"
        pattern = pattern = r"\d,\d\d,\d\d"
        pattern_val = "1,23,45"
        locale_val = "12.345"
        german_pattern_val = "1.23.45"
        default_val = "12,345"
        xxxx = "XXXX"
        expected = 12345

        assert FloatValidator.get_instance().validate(default_val) == expected
        assert FloatValidator.get_instance().validate(value=locale_val, locale=locale) == expected
        assert FloatValidator.get_instance().validate(value=pattern_val, pattern=pattern) == expected
        # assert FloatValidator.get_instance().validate(value=german_pattern_val, pattern=pattern, locale=locale) == expected

        assert FloatValidator.get_instance().is_valid(default_val) is True
        assert FloatValidator.get_instance().is_valid(value=locale_val, locale=locale) is True
        assert FloatValidator.get_instance().is_valid(value=pattern_val, pattern=pattern) is True
        # assert FloatValidator.get_instance().is_valid(value=german_pattern_val, pattern=pattern, locale=locale) is 
        
        assert FloatValidator.get_instance().validate(xxxx) is None
        assert FloatValidator.get_instance().validate(value=xxxx, locale=locale) is None
        assert FloatValidator.get_instance().validate(value=xxxx, pattern=pattern) is None
        assert FloatValidator.get_instance().validate(value=xxxx, pattern=pattern, locale=locale) is None

        assert FloatValidator.get_instance().is_valid(xxxx) is False
        assert FloatValidator.get_instance().is_valid(value=xxxx, locale=locale) is False
        assert FloatValidator.get_instance().is_valid(value=xxxx, pattern=pattern) is False
        assert FloatValidator.get_instance().is_valid(value=xxxx, pattern=pattern, locale=locale) is False
