""" 
Module Name: test_code_validator.py
Description:
    To run:
        - Go to: apache-commons-validator-python/src/
        - In the terminal, type: pytest
    This file contains:
        - Test cases from test.java.org.apache.commons.validator.routines.RegexValidatorTest.java
            Link: https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/CodeValidatorTest.java
        - Additional test cases, supported by online ean13 validators
            Link: https://eancheck.com/
Author: Juji Lau
License (Taken from apache.commons.validator.routines.CodeValidatorTest.java):
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
from typing import Optional, Union
from src.apache_commons_validator_python.routines.code_validator import CodeValidator
from src.apache_commons_validator_python.routines.regex_validator import RegexValidator
from src.apache_commons_validator_python.routines.checkdigit.ean13_checkdigit import EAN13CheckDigit

# Checkdigit constructor
EAN13_CHECKDIGIT = EAN13CheckDigit.EAN13_CHECK_DIGIT

# Test CheckDigit is null
@pytest.mark.parametrize(
    "input, is_valid", 
    [
        # invalidEAN
        ("9781930110992", True), 
        # validEAN
        ("9781930110991", True),
    ]
)
def test_init_checkdigit_is_null(input:str, is_valid:bool):
    """Tests the CodeValidator when there is no CheckDigit."""
    validator = CodeValidator(regex=None, min_length=-1, max_length=-1, checkdigit=None)
    assert validator.checkdigit is None
    assert validator.validate(input) == input
    assert validator.is_valid(input) == is_valid


# Test CheckDigit is EAN13
@pytest.mark.parametrize(
    "input, is_valid, expected_validate", 
    [
        # invalidEAN
        ("9781930110992", False, None),
        # added
        ("9780201379625", False, None), 
        ("4006381333939", False, None), 
        ("5901234123450", False, None),
        # validEAN
        ("9781930110991", True, "9781930110991"),
        # added
        ("978020137962", True, "978020137962"),
        ("4006381333931", True, "4006381333931"),
        ("590123412342", True, "590123412342"),
        # exception
        ("978193011099X", False, None)
    ]
)
def test_init_checkdigit_ean13(input:str, is_valid:bool, expected_validate:Optional[str]):
    """Tests the CodeValidator when there is no CheckDigit."""
    validator = CodeValidator(regex=None, checkdigit=EAN13_CHECKDIGIT)
    assert validator.checkdigit is not None
    assert validator.is_valid(input) == is_valid
    assert validator.validate(input) == expected_validate


# Regex constructor
CONSTRUCTOR_REGEX_STR = "^[0-9]*$"
CONSTRUCTOR_REGEX = RegexValidator(CONSTRUCTOR_REGEX_STR)
@pytest.mark.parametrize(
    "regex, length, min_length, max_length, expected_min, expected_max",
    [
        (CONSTRUCTOR_REGEX, None, -1, -1, -1, -1),
        (CONSTRUCTOR_REGEX, 13, -1, -1, 13, 13),
        (CONSTRUCTOR_REGEX, None, 10, 20, 10, 20),
        (CONSTRUCTOR_REGEX_STR, None, -1, -1, -1, -1),
        (CONSTRUCTOR_REGEX_STR, 13, -1, -1, 13, 13,),
        (CONSTRUCTOR_REGEX_STR, None, 10, 20, 10, 20),
    ]
)
def test_init_regex(regex:Union[str, RegexValidator], length:int, min_length:int, max_length:int, expected_min:int, expected_max:int):
    """ Test regex with different constructors. """
    if isinstance(regex, RegexValidator):
        validator = CodeValidator(regex_validator=regex, length=length, min_length=min_length, max_length=max_length, checkdigit=EAN13_CHECKDIGIT)
        assert validator.regex_validator == CONSTRUCTOR_REGEX
    else:
        validator = CodeValidator(regex=regex, length=length, min_length=min_length, max_length=max_length, checkdigit=EAN13_CHECKDIGIT)
        assert str(validator.regex_validator) == "RegexValidator{^[0-9]*$}"
    assert validator.min_length == expected_min
    assert validator.max_length == expected_max
    assert validator.checkdigit == EAN13_CHECKDIGIT


# Test length validation
LEN_10 = "1234567890"
LEN_11 = "12345678901"
LEN_12 = "123456789012"
LEN_20 = "12345678901234567890"
LEN_21 = "123456789012345678901"
LEN_22 = "1234567890123456789012"
@pytest.mark.parametrize(
    "min_length, max_length, input, validate_not_none",
    [
        # Valid min and max lengths
        (-1, -1, LEN_10, True),
        (-1, -1, LEN_11, True),
        (-1, -1, LEN_12, True),
        (-1, -1, LEN_20, True),
        (-1, -1, LEN_21, True),
        (-1, -1, LEN_22, True),

        (11, -1, LEN_10, False), 
        (11, -1, LEN_11, True), 
        (11, -1, LEN_12, True),
        (11, -1, LEN_20, True),
        (11, -1, LEN_21, True),
        (11, -1, LEN_22, True),

        (-1, 21, LEN_10, True), 
        (-1, 21, LEN_11, True),
        (-1, 21, LEN_12, True),
        (-1, 21, LEN_20, True),
        (-1, 21, LEN_21, True),
        (-1, 21, LEN_22, False),

        (11, 21, LEN_10, False),
        (11, 21, LEN_11, True),
        (11, 21, LEN_12, True),
        (11, 21, LEN_20, True),
        (11, 21, LEN_21, True),
        (11, 21, LEN_22, False),

        (11, 11, LEN_10, False), 
        (11, 11, LEN_11, True), 
        (11, 11, LEN_12, False),

        # Invalid min and max lengths
        (-1, 0, None, False), 
        (0, -1, None, False)
    ]
)
def test_validate_length(min_length:int, max_length:int, input:str, validate_not_none:bool):
    """Tests that CodeValidator validates based on the min_length and max_lengths."""
    validator = CodeValidator(min_length=min_length, max_length=max_length)
    assert validator.min_length == min_length
    assert validator.max_length == max_length
    if validate_not_none:
        assert validator.validate(input) == input
    else:
        assert validator.validate(input) is None


def test_regex():
    """Tests CodeValidator.regex.""" 
    REGEX_1 = "^([0-9]{3,4})$"
    REGEX_2 = r"^([0-9]{3})(?:[-\s])([0-9]{3})$"
    REGEX_3 = r"^(?:([0-9]{3})(?:[-\s])([0-9]{3}))|([0-9]{6})$" 
    # No Regular Expression
    # Need generic validator to work
    validator = CodeValidator()
    assert validator.regex_validator is None, "No Regex"
    assert validator.validate(None) == None
    # assert validator.validate("") == None
    # assert validator.validate("   ") == None
    # assert validator.validate(" A  ") == "A"    
    # assert validator.validate("12") == "12", "No Regex 2"
    # assert validator.validate("123") == "123", "No Regex 3"
    # assert validator.validate("1234") == "1234", "No Regex 4"
    # assert validator.validate("12345") == "12345", "No Regex 5"
    # assert validator.validate("12a4") == "12a4", "No Regex invalid"

    # Regular Expression
    validator = CodeValidator(regex=REGEX_1)
    assert validator.regex_validator is not None, "Regex should not be None"
    assert validator.validate("12") is None, "Regex 2"
    assert validator.validate("123") == "123", "Regex 3"
    assert validator.validate("1234") == "1234", "Regex 4"
    assert validator.validate("12345") is None, "Regex 5"
    assert validator.validate("12a4") is None, "Regex invalid"

    # Reformatted
    validator = CodeValidator(regex_validator = RegexValidator(REGEX_2), length=6)
    assert validator.validate("123-456") == "123456", "Reformat 123-456"
    assert validator.validate("123 456") == "123456", "Reformat 123 456"
    assert validator.validate("123456") is None, "Reformat 123456"
    assert validator.validate("123.456") is None, "Reformat 123.456"

    validator = CodeValidator(regex_validator = RegexValidator(REGEX_3), length=6)
    assert str(validator.regex_validator) == f"RegexValidator{{{REGEX_3}}}", "Reformat 2 Regex"
    assert validator.validate("123-456") == "123456", "Reformat 2 123-456"
    assert validator.validate("123 456") == "123456", "Reformat 2 123 456"
    assert validator.validate("123456") == "123456", "Reformat 2 123456"