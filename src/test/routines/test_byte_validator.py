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

from typing import Final
from src.main.routines.byte_validator import ByteValidator

class TestByteValidator:

    _BYTE_MIN_VAL: Final[int] = -128
    _BYTE_MAX_VAL: Final[int] = 127
    _BYTE_MAX: Final[str] = "127"
    _BYTE_MAX_1: Final[str] = "128"
    _BYTE_MIN: Final[str] = "-128"
    _BYTE_MIN_1: Final[str] = "-129"

    def test_format(self):
        validator = ByteValidator()
        expected = "123"
        pattern = "%d"
        
        assert validator.format(123) == expected
        assert validator.format(123, pattern=pattern) == expected
        assert validator.format(123, locale="en_US") == expected
        assert validator.format(123, pattern=pattern, locale="en_US") == expected

    def test_byte_range_min_max(self):
        """
        final byte min = (byte) 10;
        final byte max = (byte) 20;
        """

        validator = ByteValidator()

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
    
    def test_validate(self):
        locale = "de_DE"
        pattern = r"^\d,\d\d"
        default_val  = "123"
        neg_val = "-123"
        pattern_val = "1,23"
        xxxx = "XXXX"
        float_val = "12.3"
        expected = 123
        expected_neg = -123

        # Test positive number
        assert ByteValidator.get_instance().is_valid(default_val) is True
        assert ByteValidator.get_instance().validate(default_val) == expected
        assert ByteValidator.get_instance().is_valid(pattern_val, pattern=pattern) is True
        assert ByteValidator.get_instance().validate(pattern_val, pattern=pattern) == expected
        assert ByteValidator.get_instance().is_valid(default_val, locale=locale) is True
        assert ByteValidator.get_instance().validate(default_val, locale=locale) == expected

        # Test negative number
        assert ByteValidator.get_instance().is_valid(neg_val) is True
        assert ByteValidator.get_instance().validate(neg_val) == expected_neg
        assert ByteValidator.get_instance().is_valid(neg_val, locale=locale) is True
        assert ByteValidator.get_instance().validate(neg_val, locale=locale) == expected_neg

        # Test maximum and minimum values
        assert ByteValidator.get_instance().is_valid(self._BYTE_MAX) is True
        assert ByteValidator.get_instance().validate(self._BYTE_MAX) == self._BYTE_MAX_VAL
        assert ByteValidator.get_instance().is_valid(self._BYTE_MIN) is True
        assert ByteValidator.get_instance().validate(self._BYTE_MIN) == self._BYTE_MIN_VAL

        # Test one above maximum and one below minimum
        assert ByteValidator.get_instance().is_valid(self._BYTE_MAX_1) is False
        assert ByteValidator.get_instance().validate(self._BYTE_MAX_1) is None
        assert ByteValidator.get_instance().is_valid(self._BYTE_MIN_1) is False
        assert ByteValidator.get_instance().validate(self._BYTE_MIN_1) is None

        # Test non-numeric value
        assert ByteValidator.get_instance().is_valid(xxxx) is False
        assert ByteValidator.get_instance().validate(xxxx) is None

        # Test partially numeric value
        assert ByteValidator.get_instance().is_valid(xxxx + default_val) is False
        assert ByteValidator.get_instance().validate(xxxx + default_val) is None
        assert ByteValidator.get_instance().is_valid(default_val + xxxx) is False
        assert ByteValidator.get_instance().validate(default_val + xxxx) is None

        # Test float value
        assert ByteValidator.get_instance().is_valid(float_val) is False
        assert ByteValidator.get_instance().validate(float_val) is None

        # Test non-matching pattern
        assert ByteValidator.get_instance().validate(default_val, pattern=pattern) is None

        # Test non-existant locale
        assert ByteValidator.get_instance().validate(default_val, locale=xxxx) is None
