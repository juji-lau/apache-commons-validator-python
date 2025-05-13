"""
Module Name: test_isbn_validator.py
Description:
    This file contains:
        Test cases from test.java.org.apache.commons.validator.routines.ISBNValidatorTest.java
            Link: https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/ISBNValidatorTest.java
        Additional test cases

Authors: Alicia Chu, Juji Lau

License (Taken from apache.commons.validator.routines.ISBNValidatorTest):
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
from src.apache_commons_validator_python.util.regex import Regex
from src.apache_commons_validator_python.routines.isbn_validator import ISBNValidator

# Constants
valid_isbn10_format = [
    "1234567890", 
    "123456789X", 
    "12345-1234567-123456-X", 
    "12345 1234567 123456 X", 
    "1-2-3-4", 
    "1 2 3 4"
]

invalid_isbn10_format = [ 
    "", # empty
    "   ", # empty
    "1", # too short
    "123456789", # too short
    "12345678901", # too long
    "12345678X0", # X not at end
    "123456-1234567-123456-X", # Group too long
    "12345-12345678-123456-X", # Publisher too long
    "12345-1234567-1234567-X", # Title too long
    "12345-1234567-123456-X2", # Check Digit too long
    "--1 930110 99 5", # format
    "1 930110 99 5--", # format
    "1 930110-99 5-", # format
    "1.2.3.4", # Invalid Separator
    "1=2=3=4", # Invalid Separator
    "1_2_3_4", # Invalid Separator
    "123456789Y", # Other character at the end
    "dsasdsadsa", # invalid characters
    "I love sparrows!", # invalid characters
    "068-556-98-45" # format
]

valid_isbn13_format = [
    "9781234567890", 
    "9791234567890", 
    "978-12345-1234567-123456-1", 
    "979-12345-1234567-123456-1", 
    "978 12345 1234567 123456 1", 
    "979 12345 1234567 123456 1", 
    "978-1-2-3-4", 
    "979-1-2-3-4", 
    "978 1 2 3 4", 
    "979 1 2 3 4"
]

invalid_isbn13_format = [
    "", # empty
    "   ", # empty
    "1", # too short
    "978123456789", # too short
    "97812345678901", # too long
    "978-123456-1234567-123456-1", # Group too long
    "978-12345-12345678-123456-1", # Publisher too long
    "978-12345-1234567-1234567-1", # Title too long
    "978-12345-1234567-123456-12", # Check Digit too long
    "--978 1 930110 99 1", # format
    "978 1 930110 99 1--", # format
    "978 1 930110-99 1-", # format
    "123-4-567890-12-8", # format
    "978.1.2.3.4", # Invalid Separator
    "978=1=2=3=4", # Invalid Separator
    "978_1_2_3_4", # Invalid Separator
    "978123456789X", # invalid character
    "978-0-201-63385-X", # invalid character
    "dsasdsadsadsa", # invalid characters
    "I love sparrows!", # invalid characters
    "979-1-234-567-89-6" # format
]

# Fixtures
@pytest.fixture
def validator():
    return ISBNValidator.get_instance()

@pytest.mark.parametrize(
    "invalid_input", [
        ("123456789"),
        ("12345678901"),
        (""),
        ("X234567890")
    ]
)
def test_conversion_errors(validator:ISBNValidator, invalid_input:str):
    with pytest.raises(ValueError) as e:
        validator.convert_to_isbn13(invalid_input)


@pytest.mark.parametrize(
    "input, expected_is_valid", [
        ("1930110990", False),
        ("1930110991", False),
        ("1930110992", False),
        ("1930110993", False),
        ("1930110994", False),
        ("1930110995", True),  # valid check digit by formula (1× 1st digit + 2×second digit+⋯+10×ninth digit) mod11 = 0
        ("1930110996", False),
        ("1930110997", False),
        ("1930110998", False),
        ("1930110999", False),
        ("193011099X", False),
        ("9781930110990", False),
        ("9781930110991", True),  # valid check digit by formula (1×first digit+3×second digit+1×third digit+3×fourth digit+⋯+1×twelfth digit)mod10=0
        ("9781930110992", False),
        ("9781930110993", False),
        ("9781930110994", False),
        ("9781930110995", False),
        ("9781930110996", False),
        ("9781930110997", False),
        ("9781930110998", False),
        ("9781930110999", False),
        ("978193011099X", False)
    ]
)
def test_is_valid_invalid(validator:ISBNValidator, input:str, expected_is_valid:bool):
    """Tests `is_valid()` using invalid ISBN-10 codes."""
    assert validator.is_valid(input) == expected_is_valid


def test_invalid_isbn10_format(validator:ISBNValidator):
    """Test invalid ISBN-10 formats with `is_valid_isbn10()`, `validate_isbn10()`, and `Regex.pattern_matches()`."""
    pattern = Regex.compile(pattern_str=ISBNValidator.ISBN10_REGEX)
    for i, invalid_format in enumerate(invalid_isbn10_format):
        assert Regex.pattern_matches(pattern=pattern, string=invalid_format) is False, f"Pattern[{i}=invalid_format"
        assert validator.is_valid_isbn10(invalid_format) is False, f"is_valid_isbn10[{i}]={invalid_format}"
        assert validator.validate_isbn10(invalid_format) is None, f"validate_isbn10[{i}]={invalid_format}"
   

def test_invalid_isbn13_format(validator:ISBNValidator):
    """Test invalid ISBN-13 formats with `is_valid_isbn13()`, `validate_isbn13()`, and `Regex.pattern_matches()`."""
    pattern = Regex.compile(pattern_str=ISBNValidator.ISBN13_REGEX)
    for i, invalid_format in enumerate(invalid_isbn10_format):
        assert Regex.pattern_matches(pattern=pattern, string=invalid_format) is False, f"Pattern[{i}]={invalid_format}"
        assert validator.is_valid_isbn13(invalid_format) is False, f"is_valid_isbn13[{i}]={invalid_isbn13_format}"
        assert validator.validate_isbn13(invalid_format) is None, f"validate_isbn13[{i}]={invalid_format}"

@pytest.mark.parametrize(
    "valid_input", [
        ("1930110995"),
        ("1-930110-99-5"),
        ("1 930110 99 5"),
        ("020163385X"),
        ("0-201-63385-X"),
        ("0 201 63385 X")
    ]
)
def test__is_valid_isbn10_valid(validator:ISBNValidator, valid_input:str):
    """Test is_valid() on valid ISBN-10 codes"""
    assert validator.is_valid_isbn10(valid_input) is True
    assert validator.is_valid(valid_input) is True


@pytest.mark.parametrize(
    "valid_input", [
        ("9781930110991"),
        ("978-1-930110-99-1"),
        ("978 1 930110 99 1"),
        ("9780201633856"),
        ("978-0-201-63385-6"),
        ("978 0 201 63385 6")
    ]
)
def test_is_valid_isbn13_valid(validator:ISBNValidator, valid_input:str):
    """Test `is_valid()` and `is_valid_isbn13()` on valid ISBN-13 codes"""
    assert validator.is_valid_isbn13(valid_input) is True
    assert validator.is_valid(valid_input) is True


def test_null(validator:ISBNValidator):
    """Test all functions on `None` input."""
    assert validator.is_valid(None) is False, "is_valid"
    assert validator.is_valid_isbn10(None) is False, "is_valid_isbn10"
    assert validator.is_valid_isbn13(None) is False, "is_valid_isbn13"
    assert validator.validate(None) is None, "validate"
    assert validator.validate_isbn10(None) is None, "validate_isbn10"
    assert validator.validate_isbn13(None) is None, "validate_isbn13"
    assert validator.convert_to_isbn13(None) is None, "convert_to_isbn13"


@pytest.mark.parametrize(
    "input_isbn10, expected_output", [
        ("1930110995", "1930110995"),
        ("1-930110-99-5", "1930110995"),
        ("1 930110 99 5", "1930110995"),
        ("020163385X", "020163385X"),
        ("0-201-63385-X", "020163385X"),
        ("0 201 63385 X", "020163385X")
    ]
)
def test_validate_isbn10(input_isbn10:str, expected_output:str):
    """Test `valiate()` and `validate_isbn10()` on valid ISBN-10 codes without converting to ISBN-13."""
    validator = ISBNValidator.get_instance(convert=False)
    assert validator.validate_isbn10(input_isbn10) == expected_output
    assert validator.validate(input_isbn10) == expected_output


@pytest.mark.parametrize(
    "input_isbn10, expected_output", 
    [
        ("1930110995", "9781930110991"),
        ("1-930110-99-5", "9781930110991"),
        ("1 930110 99 5", "9781930110991"),
        ("020163385X", "9780201633856"),
        ("0-201-63385-X", "9780201633856"),
        ("0 201 63385 X", "9780201633856")
    ]
)
def test_validate_isbn10_convert(validator:ISBNValidator, input_isbn10:str, expected_output:str):
    """Test `validate()` on valid ISBN-10 codes that have been converted to ISBN-13."""
    assert validator.validate(input_isbn10) == expected_output


@pytest.mark.parametrize(
    "input_isbn13, expected_output", [
        ("9781930110991", "9781930110991"),
        ("978-1-930110-99-1", "9781930110991"),
        ("978 1 930110 99 1", "9781930110991"),
        ("9780201633856", "9780201633856"),
        ("978-0-201-63385-6", "9780201633856"),
        ("978 0 201 63385 6", "9780201633856")

    ]
)
def test_validate_isbn13(validator:ISBNValidator, input_isbn13:str, expected_output:str):
    """Test `valiate()` and `validate_isbn13()` on valid ISBN-13 codes."""
    assert validator.validate_isbn13(input_isbn13) == expected_output
    assert validator.validate(input_isbn13) == expected_output


def test_valid_isbn10_format():
    """Test valid ISBN-10 formats."""
    pattern = Regex.compile(ISBNValidator.ISBN10_REGEX)
    for i, valid_isbn10 in enumerate(valid_isbn10_format):
        assert Regex.pattern_matches(pattern=pattern, string=valid_isbn10), f"Pattern[{i}={valid_isbn10}"


def test_valid_isbn13_format():
    """Test valid ISBN-13 formats."""
    pattern = Regex.compile(ISBNValidator.ISBN13_REGEX)
    for i, valid_isbn13 in enumerate(valid_isbn13_format):
        assert Regex.pattern_matches(pattern=pattern, string=valid_isbn13), f"Pattern[{i}={valid_isbn13}"