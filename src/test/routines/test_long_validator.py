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
from src.main.routines.long_validator import LongValidator
from .test_abstract_number_validator import TestAbstractNumberValidator

class TestLongValidator(TestAbstractNumberValidator):
    LONG_MIN_VAL: Final[int] = LongValidator.LONG_MIN
    LONG_MAX_VAL: Final[int] = LongValidator.LONG_MAX
    LONG_MAX: Final[str] = "9223372036854775807"
    LONG_MAX_0: Final[str] = "9223372036854775807.99999999999999999999999"
    LONG_MAX_1: Final[str] = "9223372036854775808"
    LONG_MIN: Final[str] = "-9223372036854775808"
    LONG_MIN_0: Final[str] = "-9223372036854775808.99999999999999999999999"
    LONG_MIN_1: Final[str] = "-9223372036854775809"
    NINES: Final[str] = "9999999999999999999999999999999999999"

    @pytest.fixture(autouse=True)
    def set_up(self):
        self._validator = LongValidator(strict=False)
        self._strict_validator = LongValidator()
        self._test_pattern = r"^-?((\d{1,3}(,\d{3})+|\d+)(\.\d+)?$)$"
        self._max = None
        self._max_plus_one = None
        self._min = None
        self._min_minus_one = None
        self._invalid = [None, '', 'X', "X12", self.LONG_MAX_1, self.LONG_MIN_1, self.NINES]
        self._invalid_strict = [None, '', 'X', "X12", "12X", "1X2", "1.2", self.LONG_MAX_1, self.LONG_MIN_1, self.NINES]
        self._test_number = 1234
        self._test_zero = 0
        self._valid_strict = ['0', "1234", "1,234", self.LONG_MAX, self.LONG_MIN]
        self._valid_strict_compare = [self._test_zero, self._test_number, self._test_number, self.LONG_MAX_VAL, self.LONG_MIN_VAL]
        self._valid = ['0', "1234", "1,234", "1,234.5", "1234X", self.LONG_MAX, self.LONG_MIN, self.LONG_MAX_0, self.LONG_MIN_0]
        self._valid_compare = [self._test_zero, self._test_number, self._test_number, self._test_number, self._test_number, self.LONG_MAX_VAL, self.LONG_MIN_VAL, self.LONG_MAX_VAL, self.LONG_MIN_VAL]
        self._test_string_us = "1,234"
        self._test_string_de = "1.234"
        self._locale_value = self._test_string_de
        self._locale_pattern = r"\d.\d\d\d"
        self._test_locale = "de_DE.UTF-8"
        self._locale_expected = self._test_number

    def test_big_decimal_range_min_max(self):
        validator = LongValidator()

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

    def test_integer_validator_methods(self):
        locale = "de_DE.UTF-8"
        pattern = r"\d,\d\d,\d\d"
        pattern_val = "1,23,45"
        german_pattern_val = "1.23.45"
        locale_val = "12.345"
        default_val = "12,345"
        xxxx = "XXXX"
        expected = 12345
        
        assert LongValidator.get_instance().validate(default_val) == expected
        assert LongValidator.get_instance().validate(value=locale_val, locale=locale) == expected
        assert LongValidator.get_instance().validate(value=pattern_val, pattern=pattern) == expected
        # assert LongValidator.get_instance().validate(value=german_pattern_val, pattern=pattern, locale=locale) == expected

        assert LongValidator.get_instance().is_valid(default_val) is True
        assert LongValidator.get_instance().is_valid(value=locale_val, locale=locale) is True
        assert LongValidator.get_instance().is_valid(value=pattern_val, pattern=pattern) is True
        # assert LongValidator.get_instance().is_valid(value=german_pattern_val, pattern=pattern, locale=locale) is 
        
        assert LongValidator.get_instance().validate(xxxx) is None
        assert LongValidator.get_instance().validate(value=xxxx, locale=locale) is None
        assert LongValidator.get_instance().validate(value=xxxx, pattern=pattern) is None
        assert LongValidator.get_instance().validate(value=xxxx, pattern=pattern, locale=locale) is None

        assert LongValidator.get_instance().is_valid(xxxx) is False
        assert LongValidator.get_instance().is_valid(value=xxxx, locale=locale) is False
        assert LongValidator.get_instance().is_valid(value=xxxx, pattern=pattern) is False
        assert LongValidator.get_instance().is_valid(value=xxxx, pattern=pattern, locale=locale) is False
