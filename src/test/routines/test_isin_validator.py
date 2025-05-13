"""
Module Name: test_isin_validator.py
Description:
    This file contains:
        Test cases from test.java.org.apache.commons.validator.routines.ISINValidatorTest.java
            Link: https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/ISINValidatorTest.java

Authors: Alicia Chu

License (Taken from apache.commons.validator.routines.ISINValidatorTest):
    Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements.
    See the NOTICE file distributed with this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software distributed under the License is
    distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and limitations under the License.

Changes:
"""
import pytest
from typing import Final, Optional
from src.apache_commons_validator_python.routines.isin_validator import ISINValidator

class TestISINValidator:
    """
    Unit test class for ISINValidator.

    Attributes:
        _VALIDATOR_TRUE (ISINValidator): Validator with country code checking enabled.
        _VALIDATOR_FALSE (ISINValidator): Validator with country code checking disabled.
        _valid_format (list[str]): List of valid ISIN codes.
        _invalid_format (list[str]): List of syntactically invalid ISIN codes.
        _invalid_format_true (list[str]): List of codes invalid due to incorrect country codes.
    """

    _VALIDATOR_TRUE: Final[ISINValidator] = ISINValidator.get_instance(True)
    _VALIDATOR_FALSE: Final[ISINValidator] = ISINValidator.get_instance(False)

    _valid_format: Final[list[str]] = [
        "US0378331005", "BMG8571G1096", "AU0000XVGZA3", "GB0002634946", "FR0004026250",
        "DK0009763344", "GB00B03MLX29", "US7562071065", "US56845T3059", "LU0327357389",
        "US032511BN64", "INE112A01023", "EZ0000000003", "EU000A0VUCF1", "XA2053913989",
        "XB0000000008", "XC0009698371", "XD0000000006", "XF0000000004", "QS0000000008",
        "QT0000000007", "QW0000000002", "XS0000000009", "EU0009652783", "XAC8614YAB92",
        "XC0001458477", "XD0209061296", "AN8068571086"
    ]

    _invalid_format: Final[list[Optional[str]]] = [
        None, "", "   ", #empty
        "US037833100O", "BMG8571G109D", "AU0000XVGZAD",
        "GB000263494I", "FR000402625C", "DK000976334H",
        "3133EHHF3", #see VALIDATOR-422 Valid check-digit, but not valid ISIN
        "AU0000xvgzA3", # disallow lower case NSIN
        "gb0002634946" # disallow lower case ISO code
    ]

    # Invalid codes if country checking is enabled
    _invalid_format_true: Final[list[str]] = [
        "AB0000000006"  # Invalid country code
    ]

    def test_invalid_false(self) -> None:
        """
        Test invalid ISINs with country code validation disabled.

        Asserts:
            Each code in _invalid_format should return False.
        """
        for code in self._invalid_format:
            assert not self._VALIDATOR_FALSE.is_valid(code), f"Expected invalid: {code}"

    def test_invalid_true(self) -> None:
        """
        Test invalid ISINs with country code validation enabled.

        Each code in _invalid_format and _invalid_format_true should return False.
        """
        for code in self._invalid_format:
            assert not self._VALIDATOR_TRUE.is_valid(code), f"Expected invalid: {code}"
        for code in self._invalid_format_true:
            assert not self._VALIDATOR_TRUE.is_valid(code), f"Invalid country code: {code}"

    def test_is_valid_false(self) -> None:
        """
        Test valid ISINs with country code checking disabled.

        Asserts:
            Each code in _valid_format should return True.
        """
        for code in self._valid_format:
            assert self._VALIDATOR_FALSE.is_valid(code), f"Expected valid: {code}"

    def test_is_valid_true(self) -> None:
        """
        Test valid ISINs with country code checking enabled.

        Asserts:
            Each code in _valid_format should return True.
        """
        for code in self._valid_format:
            assert self._VALIDATOR_TRUE.is_valid(code), f"Expected valid: {code}"