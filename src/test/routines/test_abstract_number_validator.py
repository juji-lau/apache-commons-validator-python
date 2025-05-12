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
import pickle
from abc import ABC
from src.main.routines.abstract_number_validator import AbstractNumberValidator

class TestAbstractNumberValidator(ABC):

    _validator = AbstractNumberValidator(strict=False, format_type=0, allow_fractions=False)
    _strict_validator = AbstractNumberValidator(strict=True, format_type=0, allow_fractions=False)
    _max = None
    _max_plus_one = None
    _min = None
    _min_minus_one = None
    _invalid = []
    _valid = []
    _valid_compare = []
    _invalid_strict = []
    _valid_strict = []
    _valid_strict_compare = []
    _test_pattern = ''
    _test_number = None
    _test_zero = 0
    _test_string_us = ''
    _test_string_de = ''
    _locale_value = ''
    _locale_pattern = ''
    _test_locale = 'de_DE.UTF-8'
    _locale_expected = None

    def test_format(self):
        number = 1234.5

        if self._strict_validator.allow_fractions:
            assert self._strict_validator.format(value=number, locale="en_US") == "1,234.5"
            assert self._strict_validator.format(value=number, locale="de_DE.UTF-8") == "1.234,5"
            assert self._strict_validator.format(value=number, pattern="%.2f") == "1,234.50"
        else:
            number = 1234.5
            assert self._strict_validator.format(value=number, locale="en_US") == "1,234"
            assert self._strict_validator.format(value=number, locale="de_DE.UTF-8") == "1.234"

    def test_format_type(self):
        assert self._validator.format_type == 0
        assert AbstractNumberValidator.STANDARD_FORMAT == self._validator.format_type
    
    def test_invalid_not_strict(self):
        for invalid in self._invalid:
            assert self._validator._parse(invalid, None, "en_US") is None
            assert self._validator.is_valid(invalid, None, "en_US") is False
            assert self._validator._parse(invalid, self._test_pattern, None) is None
            assert self._validator.is_valid(invalid, self._test_pattern, None) is False
    
    def test_invalid_strict(self):
        for invalid in self._invalid_strict:
            assert self._strict_validator._parse(invalid, None, "en_US") is None
            assert self._strict_validator.is_valid(invalid, None, "en_US") is False
            assert self._strict_validator._parse(invalid, self._test_pattern, None) is None
            assert self._strict_validator.is_valid(invalid, self._test_pattern, None) is False
    
    def test_range_min(self):
        number9  = 9
        number10 = 10
        number11 = 11
        number19 = 19
        number20 = 20
        number21 = 21
        min = 10
        max = 20

        # test is_in_range()
        assert self._validator.is_in_range(number9, min, max) is False  # less than range
        assert self._validator.is_in_range(number10, min, max) is True  # equal to min
        assert self._validator.is_in_range(number11, min, max) is True  # in range
        assert self._validator.is_in_range(number20, min, max) is True  # equal to max
        assert self._validator.is_in_range(number21, min, max) is False # greater than range

        # test min_value()
        assert self._validator.min_value(number9, min) is False # less than min
        assert self._validator.min_value(number10, min) is True # equal to min
        assert self._validator.min_value(number11, min) is True # greater than min

        # test max_val()
        assert self._validator.max_value(number19, max) is True  # less than max
        assert self._validator.max_value(number20, max) is True  # equal to max
        assert self._validator.max_value(number21, max) is False # greater than max
    
    # TODO: test serialization
    def test_serialization(self):
        try:
            data = pickle.dumps(self._validator)
            restored = pickle.loads(data)
            assert restored is not None
        except Exception as e:
            pytest.fail(f"Serialization failed: {e}")

    def test_validate_locale(self):
        # test US locale
        assert self._strict_validator._parse(self._test_string_us, None, "en_US") == self._test_number
        # assert self._strict_validator._parse(self._test_string_de, None, "en_US") is None

        # test German locale
        assert self._strict_validator._parse(self._test_string_de, None, "de_DE.UTF-8") == self._test_number
        # assert self._strict_validator._parse(self._test_string_us, None, "de_DE.UTF-8") is None

        # test default locale (should be US)
        assert self._strict_validator._parse(self._test_string_us, None, None) == self._test_number
        # assert self._strict_validator._parse(self._test_string_de, None, None) is None
    
    def test_validate_min_max(self):
        if self._max:
            assert self._validator._parse(str(self._max), None, None) == self._max
            assert self._validator._parse(str(self._max_plus_one), None, None) is None
            assert self._validator._parse(str(self._min), None, None) == self._min
            assert self._validator._parse(str(self._min_minus_one), None, None) is None
    
    def test_valid_not_strict(self):
        for i, valid in enumerate(self._valid):
            assert self._validator._parse(valid, None, "en_US") == self._valid_compare[i]
            assert self._validator.is_valid(valid, None, "en_US") is True
            assert self._validator._parse(valid, self._test_pattern, None) == self._valid_compare[i]
            assert self._validator.is_valid(valid, self._test_pattern, None) is True
    
    def test_valid_strict(self):
        for i, valid in enumerate(self._valid_strict):
            assert self._strict_validator._parse(valid, None, "en_US") == self._valid_strict_compare[i]
            assert self._strict_validator.is_valid(valid, None, "en_US") is True
            assert self._strict_validator._parse(valid, self._test_pattern, None) == self._valid_strict_compare[i]
            assert self._strict_validator.is_valid(valid, self._test_pattern, None) is True
    
    def test_invalid_locale(self):
        assert self._validator.is_valid(self._locale_value, locale='invalid') is False
        assert self._validator._parse(self._locale_value, None, 'invalid') is None
