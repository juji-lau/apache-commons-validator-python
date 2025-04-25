""" 
Module Name: test_regex_validator.py
Description:
    To run:
        - Go to: apache-commons-validator-python/src/
        - In the terminal, type: pytest
    This file contains:
        - Test cases from test.java.org.apache.commons.validator.routines.RegexValidator.java
            Link: https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/RegexValidatorTest.java
        - Additional test cases
Author: Juji Lau
License (Taken from apache.commons.validator.routines.RegexValidator):
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
from src.main.routines.regex_validator import RegexValidator

# Constants
REGEX = "^([abc]*)(?:\\-)([DEF]*)(?:\\-)([123]*)$"
COMPONENT_1 = "([abc]{3})"
COMPONENT_2 = "([DEF]{3})"
COMPONENT_3 = "([123]{3})"
SEPARATOR_1 = r"(?:\-)"
SEPARATOR_2 = r"(?:\s)"
REGEX_1 = f"^{COMPONENT_1}{SEPARATOR_1}{COMPONENT_2}{SEPARATOR_1}{COMPONENT_3}$"
REGEX_2 = f"^{COMPONENT_1}{SEPARATOR_2}{COMPONENT_2}{SEPARATOR_2}{COMPONENT_3}$"
REGEX_3 = f"^{COMPONENT_1}{COMPONENT_2}{COMPONENT_3}$"
MULTIPLE_REGEX = [REGEX_1, REGEX_2, REGEX_3]

# Error messages
MESSAGE_MISSING_REGEX = "Regular expressions are missing."
MESSAGE_FAILED_REGEX = "Failed to compile "
MESSAGE_INVALID_TYPE = "Regexs must be a String or a list of Strings."


@pytest.mark.parametrize("regex_input, expected_message", [
    (None, MESSAGE_MISSING_REGEX),
    ("", MESSAGE_MISSING_REGEX),
    ([None], MESSAGE_MISSING_REGEX),
    ([], MESSAGE_MISSING_REGEX),
    (["ABC", None], MESSAGE_MISSING_REGEX),
    (["", "ABC"], MESSAGE_MISSING_REGEX),
    # unclosed bracket causes an error
    ("^([abCD12]*$", MESSAGE_FAILED_REGEX),
    # using an integer instead of a string raises an error
    (34, MESSAGE_INVALID_TYPE)
]) 
def test_init_invalid(regex_input:str, expected_message:str):
    """Tests various invalid inputs for RegexValidator's __init__."""
    with pytest.raises(ValueError) as e:
        RegexValidator(regex_input)
    assert expected_message in str(e.value)


@pytest.mark.parametrize("index, expected_pattern", [
    (0, REGEX_1),
    (1, REGEX_2),
    (2, REGEX_3)
])
def test_patterns(index:int, expected_pattern:str):
    """Test that RegexValidator correctly returns stored regex patterns."""
    validator = RegexValidator(MULTIPLE_REGEX)
    assert validator.patterns[index].pattern == expected_pattern


@pytest.mark.parametrize("regex, value, expected_valid, expected_match, expected_validate", [
    # Valid inputs
    (MULTIPLE_REGEX, "AAC FDE 321", True, ["AAC", "FDE", "321"], "AACFDE321"),
    (REGEX_1, "AAC FDE 321", False, None, None),
    (REGEX_2, "AAC FDE 321", True, ["AAC", "FDE", "321"], "AACFDE321"),
    (REGEX_3, "AAC FDE 321", False, None, None),
    # Invalid input
    (MULTIPLE_REGEX, "AAC*FDE*321", False, None, None)
])
def test_multiple_regex_case_insensitive(regex:str, value:str, expected_valid:bool, expected_match:str, expected_validate:list):
    """Test is_valid(), validate(), and match() for various case-insensitive multiple regex validators."""
    validator = RegexValidator(regex, case_sensitive=False)
    assert validator.is_valid(value) == expected_valid
    assert validator.match(value) == expected_match
    assert validator.validate(value) == expected_validate 


@pytest.mark.parametrize("regex, value, expected_valid, expected_validate, expected_match", [
    # Valid inputs
    (MULTIPLE_REGEX, "aac FDE 321" , True, "aacFDE321", ["aac", "FDE", "321"]),
    (REGEX_1, "aac FDE 321", False, None, None),
    (REGEX_2, "aac FDE 321", True, "aacFDE321", ["aac", "FDE", "321"]),
    (REGEX_3, "aaC FDE 321", False, None, None),
    # Invalid input
    (MULTIPLE_REGEX, "AAC*FDE*321" , False, None, None)
])
def test_multiple_regex_case_sensitive(regex:str, value:str, expected_valid:bool, expected_validate:str, expected_match:list):
    """Test is_valid(), validate(), and match() for various case-sensitive multiple regex validators."""
    validator = RegexValidator(regex, case_sensitive=True)
    assert validator.is_valid(value) == expected_valid
    assert validator.validate(value) == expected_validate 
    assert validator.match(value) == expected_match


@pytest.mark.parametrize("regex", [
    # Valid inputs
    (REGEX),
    (MULTIPLE_REGEX),
    (REGEX_1),
    (REGEX_2),
    (REGEX_3),
])
def test_is_none(regex:str):
    """Test is_valid(), validate(), and match() on the input None"""
    validator = RegexValidator(regex)
    assert not validator.is_valid(None)
    assert validator.validate(None) is None
    assert validator.match(None) is None


@pytest.mark.parametrize("regex, sensitive, value, expected_valid, expected_validate, expected_match", [
    # Valid inputs
    (REGEX, True, "ac-DE-1" , True, "acDE1", ["ac", "DE", "1"]),
    (REGEX, True, "AB-de-1", False, None, None), 
    (REGEX, False, "AB-de-1", True, "ABde1", ["AB", "de", "1"]),
    (REGEX, False, "ABd-de-1", False, None, None),
    ("^([A-Z]*)$", None, "ABC", True, "ABC", ["ABC"])
])
def test_single_regex(regex:str, sensitive:bool, value:str, expected_valid:bool, expected_validate:str, expected_match:list):
    """Test instance methods with single regular expression (case sensitive AND insensitive)."""
    if sensitive is None:
        validator = RegexValidator(regex)
    else:
        validator = RegexValidator(regex, case_sensitive=sensitive)
    assert validator.is_valid(value) == expected_valid
    assert validator.validate(value) == expected_validate
    assert validator.match(value) == expected_match


@pytest.mark.parametrize("regex, expected_string", [
    (REGEX, ("RegexValidator{" + REGEX + "}")), 
    ([REGEX, REGEX], ("RegexValidator{" + REGEX + "," + REGEX + "}"))
])
def test_str(regex: Union[str, list[str]], expected_string: str):
    """Test to_string() method."""
    validator = RegexValidator(regex)
    assert str(validator) == expected_string