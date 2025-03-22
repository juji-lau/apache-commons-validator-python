"""
Module Name: isbn_validator.py

Link: https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/ISBNValidatorTest.java

Author: Alicia Chu

License:
    Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements.
    See the NOTICE file distributed with this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software distributed under the License is
    distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and limitations under the License.

"""
import pytest
from main.routines.isbn import ISBNValidator
import re


valid_isbn10_format = [
    "1234567890", "123456789X", "12345-1234567-123456-X", 
    "12345 1234567 123456 X", "1-2-3-4", "1 2 3 4"
]

invalid_isbn10_format = [ "", # empty
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
    "9781234567890", "9791234567890", "978-12345-1234567-123456-1", 
    "979-12345-1234567-123456-1", "978 12345 1234567 123456 1", 
    "979 12345 1234567 123456 1", "978-1-2-3-4", "979-1-2-3-4", 
    "978 1 2 3 4", "979 1 2 3 4"
]

invalid_isbn13_format = ["", # empty
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

valid_isbn10 = ["1930110995", "1-930110-99-5", "1 930110 99 5", "020163385X", "0-201-63385-X", "0 201 63385 X"]

valid_isbn13 = ["9781930110991","978-1-930110-99-1", "978 1 930110 99 1", "9780201633856", "978-0-201-63385-6", "978 0 201 63385 6"]
# test cases for test_invalid only (testing is_valid)
@pytest.mark.parametrize("isbn, expected", [
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
])


def test_invalid(validator, isbn, expected):
    assert validator.is_valid(isbn) == expected, f"FAILED: is_valid('{isbn}') expected {expected}, but got {validator.is_valid(isbn)}"

@pytest.mark.parametrize("isbn", valid_isbn10_format)
def test_valid_isbn10_format(isbn):
    pattern = re.compile(ISBNValidator.ISBN10_REGEX)
    assert pattern.match(isbn), f"FAILED: ISBN-10 format check failed for '{isbn}' (Did not match regex pattern)"

@pytest.mark.parametrize("isbn", invalid_isbn10_format)
def test_invalid_isbn10_format(isbn):
    '''
    Test invalid ISBN-10 formats with is_valid_isbn10, validate_isbn10, 
    and pattern matching.
    '''
    validator = ISBNValidator()
    pattern = re.compile(ISBNValidator.ISBN10_REGEX)
    assert not validator.is_valid_isbn10(isbn), "is_valid_isbn10 = " + isbn
    assert validator.validate_isbn10(isbn) is None, "validate_isbn10 = " + isbn
    assert not pattern.match(isbn), "Pattern = " + isbn

    assert not validator.is_valid_isbn10(isbn), f"FAILED: is_valid_isbn10('{isbn}') should return False, but got True"
    assert validator.validate_isbn10(isbn) is None, f"FAILED: validate_isbn10('{isbn}') should return None, but got {validator.validate_isbn10(isbn)}"
    assert not pattern.match(isbn), f"FAILED: ISBN-10 format check incorrectly passed for '{isbn}' (Should NOT match regex pattern)"

@pytest.mark.parametrize("isbn", valid_isbn13_format)
def test_valid_isbn13_format(isbn):
    pattern = re.compile(ISBNValidator.ISBN13_REGEX)
    assert pattern.match(isbn), f"FAILED: ISBN-13 format check failed for '{isbn}' (Did not match regex pattern)"

@pytest.mark.parametrize("isbn", invalid_isbn13_format)
def test_invalid_isbn13_format(isbn):
    validator = ISBNValidator()
    pattern = re.compile(ISBNValidator.ISBN13_REGEX)
    assert not validator.is_valid_isbn13(isbn), f"FAILED: is_valid_isbn13('{isbn}') should return False, but got True"
    assert validator.validate_isbn13(isbn) is None, f"FAILED: validate_isbn13('{isbn}') should return None, but got {validator.validate_isbn13(isbn)}"
    assert not pattern.match(isbn), f"FAILED: ISBN-13 format check incorrectly passed for '{isbn}' (Should NOT match regex pattern)"

@pytest.mark.parametrize("isbn", valid_isbn10)
def test_valid_isbn10(isbn):
    '''
    Test is_valid and is_valid_isbn10 with list valid_isbn10.
    '''
    validator = ISBNValidator()
    assert validator.is_valid(isbn), f"FAILED: is_valid({isbn}) should return True, but got False"
    assert validator.is_valid_isbn10(isbn), f"FAILED: is_valid_isbn10({isbn}) should return True, but got False"

@pytest.mark.parametrize("isbn", valid_isbn13)
def test_valid_isbn13(isbn):
    '''
    Test is_valid and is_valid_isbn13 with list valid_isbn13.
    '''
    validator = ISBNValidator()
    assert validator.is_valid(isbn), f"FAILED: is_valid({isbn}) should return True, but got False"
    assert validator.is_valid_isbn13(isbn), f"FAILED: is_valid_isbn13({isbn}) should return True, but got False"


@pytest.mark.parametrize("isbn", valid_isbn10)
def test_validate_isbn10(isbn):
    validator = ISBNValidator()
    expected = isbn.replace("-", "").replace(" ", "")
    assert validator.validate_isbn10(isbn) == expected, f"Failed validate_isbn10: {isbn} (Expected: {expected})"
    assert validator.validate(isbn) == expected, f"Failed for validate: {isbn} (Expected: {expected})"

@pytest.mark.parametrize("isbn", valid_isbn13)
def test_validate_isbn13(isbn):
    validator = ISBNValidator()
    expected = isbn.replace("-", "").replace(" ", "")
    assert validator.validate_isbn13(isbn) == expected, f"Failed validate_isbn13: {isbn} (Expected: {expected})"
    assert validator.validate(isbn) == expected, f"Failed for validate: {isbn} (Expected: {expected})"

def test_conversion_errors():
    validator = ISBNValidator()
    with pytest.raises(ValueError):
        validator.convert_to_isbn13("123456789 ")

    with pytest.raises(ValueError):
        validator.convert_to_isbn13("12345678901")

    with pytest.raises(ValueError):
        validator.convert_to_isbn13("")

    with pytest.raises(ValueError):
        validator.convert_to_isbn13("X234567890")

def test_null_values():
    validator = ISBNValidator()
    assert not validator.is_valid(None)
    assert not validator.is_valid_isbn10(None)
    assert not validator.is_valid_isbn13(None)
    assert validator.validate(None) is None
    assert validator.validate_isbn10(None) is None
    assert validator.validate_isbn13(None) is None
    assert validator.convert_to_isbn13(None) is None
