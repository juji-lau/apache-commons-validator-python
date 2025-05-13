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
from src.apache_commons_validator_python.routines.big_integer_validator import BigIntegerValidator
from .test_abstract_number_validator import TestAbstractNumberValidator

class TestBigInetegerValue(TestAbstractNumberValidator):
    # Not allowing: Mismatched thousands/decimal separator in pattern and val

    @pytest.fixture(autouse=True)
    def set_up(self):
        self._validator = BigIntegerValidator(strict=False, format_type=0)
        self._strict_validator = BigIntegerValidator()
        self._test_pattern = r"^((\d{1,3}(,\d{3})+|\d+)(\.\d+)?$)"
        self._max = None
        self._max_plus_one = None
        self._min = None
        self._min_minus_one = None
        self._invalid = [None, '', 'X', "X12"]
        self._invalid_strict = [None, '', 'X', "X12", "12X", "1X2", "1.2"]
        self._test_number = 1234
        self._test_zero = 0
        self._valid_strict = ['0', "1234", "1,234"]
        self._valid_strict_compare = [self._test_zero, self._test_number, self._test_number]
        self._valid = ['0', "1234", "1,234", "1,234.5", "1234X"]
        self._valid_compare = [self._test_zero, self._test_number, self._test_number, self._test_number, self._test_number]
        self._test_string_us = "1,234"
        self._test_string_de = "1.234"
        self._locale_value = self._test_string_de
        self._locale_pattern = r"\d.\d\d\d"
        self._test_locale = "de_DE.UTF-8"
        self._locale_expected = self._test_number
        

    def test_big_integer_range_min_max(self):
        validator = BigIntegerValidator()

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

        # test min_value()
        assert validator.min_value(number9, min) is False # less than min
        assert validator.min_value(number10, min) is True # equal to min
        assert validator.min_value(number11, min) is True # greater than min

        # test max_val()
        assert validator.max_value(number19, max) is True  # less than max
        assert validator.max_value(number20, max) is True  # equal to max
        assert validator.max_value(number21, max) is False # greater than max

    def test_big_integer_validator_methods(self):
        locale = "de_DE.UTF-8"
        pattern = r"^\d,\d\d,\d\d"
        pattern_val = "1,23,45"
        german_pattern_val = "1.23.45"
        locale_val = "12.345"
        default_val = "12,345"
        xxxx = "XXXX"
        expected = 12345

        assert BigIntegerValidator.get_instance().validate(default_val) == expected
        assert BigIntegerValidator.get_instance().validate(value=locale_val, locale=locale) == expected
        assert BigIntegerValidator.get_instance().validate(value=pattern_val, pattern=pattern) == expected
        # assert BigIntegerValidator.get_instance().validate(value=german_pattern_val, pattern=pattern, locale=locale) == expected

        assert BigIntegerValidator.get_instance().is_valid(default_val) is True
        assert BigIntegerValidator.get_instance().is_valid(value=locale_val, locale=locale) is True
        assert BigIntegerValidator.get_instance().is_valid(value=pattern_val, pattern=pattern) is True
        # assert BigIntegerValidator.get_instance().is_valid(value=german_pattern_val, pattern=pattern, locale=locale) is True

        assert BigIntegerValidator.get_instance().validate(xxxx) is None
        assert BigIntegerValidator.get_instance().validate(value=xxxx, locale=locale) is None
        assert BigIntegerValidator.get_instance().validate(value=xxxx, locale=pattern) is None
        assert BigIntegerValidator.get_instance().validate(value=pattern_val, pattern=pattern, locale=locale) is None

        assert BigIntegerValidator.get_instance().is_valid(xxxx) is False
        assert BigIntegerValidator.get_instance().is_valid(value=xxxx, locale=locale) is False
        assert BigIntegerValidator.get_instance().is_valid(value=xxxx, locale=pattern) is False
        assert BigIntegerValidator.get_instance().is_valid(value=pattern_val, pattern=pattern, locale=locale) is False
