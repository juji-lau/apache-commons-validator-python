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

import locale
from src.main.routines.big_decimal_validator import BigDecimalValidator
from typing import Final

class TestBigDecimalValidator:
    """"""

    def test_validator_methods(self):
        locale_us = "en_US"
        locale_de = "de_DE"
        pattern = r"\d,\d\d,\d.\d\d"
        us_val = "1234.56"
        de_val = "1234,56"
        neg_val = "-1234.56"
        pattern_val = "1,23,4.56"
        int_val = "1234"
        expected = 1234.56
        expected_neg = -1234.56
        expected_int = 1234

        # Test positive number
        assert BigDecimalValidator.get_instance().is_valid(us_val) is True, f"FAILED: is_valid('{us_val}') expected True but got False"
        assert BigDecimalValidator.get_instance().validate(us_val) == expected, f"FAILED: validate('{us_val}') expected {expected} but got {BigDecimalValidator.get_instance().validate(us_val)}"

        # Test negative number
        assert BigDecimalValidator.get_instance().is_valid(neg_val) is True, f"FAILED: is_valid('{neg_val}') expected True but got False"
        assert BigDecimalValidator.get_instance().validate(neg_val) == expected_neg, f"FAILED: validate('{neg_val}') expected {expected_neg} but got {BigDecimalValidator.get_instance().validate(neg_val)}"

        # Test integer value
        assert BigDecimalValidator.get_instance().is_valid(int_val) is True, f"FAILED: is_valid('{int_val}') expected True but got False"
        assert BigDecimalValidator.get_instance().validate(int_val) == expected_int, f"FAILED: validate('{int_val}') expected {expected_int} but got {BigDecimalValidator.get_instance().validate(int_val)}"

        # Test pattern
        assert BigDecimalValidator.get_instance().is_valid(pattern_val, pattern=pattern) is True, f"FAILED: is_valid('{pattern_val}', pattern='{pattern}') expected True but got False"
        assert BigDecimalValidator.get_instance().validate(pattern_val, pattern=pattern) == expected, f"FAILED: validator('{pattern_val}', pattern='{pattern}') expected {expected} but got {BigDecimalValidator.get_instance().validate(pattern_val, pattern=pattern)}"

        # Test locales
        assert BigDecimalValidator.get_instance().is_valid(us_val, locale=locale_us) is True, f"FAILED: is_valid('{us_val}', locale='{locale_us}') expected True but got False"
        assert BigDecimalValidator.get_instance().validate(us_val, locale=locale_us) == expected, f"FAILED: valididate('{us_val}', locale='{locale_us}') expected {expected} but got {BigDecimalValidator.get_instance().validate(us_val, locale=locale_us)}"
        assert BigDecimalValidator.get_instance().is_valid(de_val, locale=locale_de) is True, f"FAILED: is_valid('{us_val}', locale='{locale_de}') expected True but got False"
        assert BigDecimalValidator.get_instance().validate(de_val, locale=locale_de) == expected, f"FAILED: valididate('{de_val}', locale='{locale_de}') expected {expected} but got {BigDecimalValidator.get_instance().validate(de_val, locale=locale_de)}"

        # Test pattern + locale
        assert BigDecimalValidator.get_instance().is_valid(pattern_val, pattern=pattern, locale=locale_us) is True, f"FAILED: is_valid('{us_val}', pattern='{pattern}', locale='{locale_us}') expected True but got False"
        assert BigDecimalValidator.get_instance().validate(pattern_val, pattern=pattern, locale=locale_us) == expected, f"FAILED: valididate('{us_val}', pattern='{pattern}', locale='{locale_us}') expected {expected} but got {BigDecimalValidator.get_instance().validate(pattern_val, pattern=pattern, locale=locale_us)}"
