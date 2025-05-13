""" 
Module Name: test_isin_checkdigit.py
Description:
    This file tests the implementation of ISINCheckDigit.
    This file contains:
        Test cases from: 
            test.java.org.apache.commons.validator.routines.checkdigit.ISINCheckDigitTest.java
            (https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/checkdigit/ISINDigitTest.java)
Author: Alicia Chu
License (Taken from apache.commons.validator.routines.checkdigit.ISINCheckDigitTest.java):
    Licensed to the Apache Software Foundation (ASF) under one or more
    contributor license agreements. See the NOTICE file distributed with
    this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0
    (the "License"); you may not use this file except in compliance with
    the License. You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import pytest
from src.test.routines.checkdigit.test_abstract_checkdigit import AbstractCheckDigitTest
from src.apache_commons_validator_python.routines.checkdigit.isin_checkdigit import ISINCheckDigit


class TestISINCheckDigit(AbstractCheckDigitTest):
    """
    Unit tests for ISINCheckDigit using the AbstractCheckDigitTest base class.
    """

    def setup_method(self):
        """
        Sets up the ISINCheckDigit routine and valid/invalid test data.
        """
        self._routine = ISINCheckDigit._ISIN_CHECK_DIGIT  # Using the singleton instance
        self._valid = [
            "US0378331005",
            "BMG8571G1096",
            "AU0000XVGZA3",
            "GB0002634946",
            "FR0004026250",
            "3133EHHF3",          # Valid check digit but not valid ISIN
            "DK0009763344",
            "dk0009763344",       # TODO: lowercase is currently accepted, is this valid?
            "AU0000xvgza3",       # lowercase NSIN
            "EZ0000000003",       # Invented for internal testing
            "XS0000000009",
            "AA0000000006",
        ]
        self._invalid = ["0378#3100"]  # Invalid format


    def test_validator_345(self):
        """
        Tests ISINs with valid format but incorrect check digits.
        """
        invalid_check_digits = [
            "US037833100O",  # correct check digit is '5'
            "BMG8571G109D",  # correct is '6'
            "AU0000XVGZAD",  # correct is '3'
            "GB000263494I",  # correct is '6'
            "FR000402625C",  # correct is '0'
            "DK000976334H",  # correct is '4'
        ]
        for code in invalid_check_digits:
            assert not self._routine.is_valid(code), f"Should fail: {code}"
