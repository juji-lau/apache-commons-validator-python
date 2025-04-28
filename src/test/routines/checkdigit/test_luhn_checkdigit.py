""" 
Module Name: test_luhn_checkdigit.py
Description:
    This file tests the implementation of LuhnCheckDigit.
    This file contains:
        Test cases from: 
            test.java.org.apache.commons.validator.routines.checkdigit.LuhnCheckDigitTest.java
            (https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/checkdigit/LuhnCheckDigitTest.java)
Author: Alicia Chu
License (Taken from apache.commons.validator.routines.checkdigit.LuhnCheckDigitTest.java):
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

from src.main.routines.checkdigit.luhn_checkdigit import LuhnCheckDigit
from src.test.routines.checkdigit.test_abstract_checkdigit import AbstractCheckDigitTest


class TestLuhnCheckDigit(AbstractCheckDigitTest):
    """Luhn Check Digit Test."""
    def setup_method(self):
        self._routine = LuhnCheckDigit.LUHN_CHECK_DIGIT
        self._valid = [
            "4417123456789113",   # VALID_VISA
            "4222222222222",      # VALID_SHORT_VISA
            "378282246310005",    # VALID_AMEX
            "5105105105105100",   # VALID_MASTERCARD
            "6011000990139424",   # VALID_DISCOVER
            "30569309025904"      # VALID_DINERS
        ]