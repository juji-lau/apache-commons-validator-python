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
import pytest
from src.main.routines.credit_card_validator import CreditCardValidator
from src.main.routines.checkdigit.luhn_checkdigit import LuhnCheckDigit
from src.main.routines.regex_validator import RegexValidator
from src.main.routines.code_validator import CodeValidator


# Valid credit card numbers (correct Luhn check digits)
_VALID_VISA: Final[str] = "4417123456789113"              # 16 digits
_VALID_SHORT_VISA: Final[str] = "4222222222222"           # 13 digits
_VALID_AMEX: Final[str] = "378282246310005"               # 15 digits
_VALID_MASTERCARD: Final[str] = "5105105105105100"        # 16 digits
_VALID_DISCOVER: Final[str] = "6011000990139424"          # 16 digits
_VALID_DISCOVER65: Final[str] = "6534567890123458"        # 16 digits (FIXME: verify with real Discover 65 range)
_VALID_DINERS: Final[str] = "30569309025904"              # 14 digits
_VALID_VPAY: Final[str] = "4370000000000061"              # 16 digits
_VALID_VPAY2: Final[str] = "4370000000000012"             # 16 digits

# Invalid credit card numbers (bad Luhn or formatting)
_ERROR_VISA: Final[str] = "4417123456789112"              # 16 digits
_ERROR_SHORT_VISA: Final[str] = "4222222222229"           # 13 digits, etc.
_ERROR_AMEX: Final[str] = "378282246310001"
_ERROR_MASTERCARD: Final[str] = "5105105105105105"
_ERROR_DISCOVER: Final[str] = "6011000990139421"
_ERROR_DISCOVER65: Final[str] = "6534567890123450"        # FIXME: verify
_ERROR_DINERS: Final[str] = "30569309025901"
_ERROR_VPAY: Final[str] = "4370000000000069"

# Grouped valid test data
_VALID_CARDS: Final[list[str]] = [
    _VALID_VISA,
    _VALID_SHORT_VISA,
    _VALID_AMEX,
    _VALID_MASTERCARD,
    _VALID_DISCOVER,
    _VALID_DISCOVER65,
    _VALID_DINERS,
    _VALID_VPAY,
    _VALID_VPAY2,
    "60115564485789458",  # From VALIDATOR-403, custom test case
]

# Grouped invalid test data
_ERROR_CARDS: Final[list[str]] = [
    _ERROR_VISA,
    _ERROR_SHORT_VISA,
    _ERROR_AMEX,
    _ERROR_MASTERCARD,
    _ERROR_DISCOVER,
    _ERROR_DISCOVER65,
    _ERROR_DINERS,
    _ERROR_VPAY,
    "",
    "12345678901",          # too short (11 digits)
    "12345678901234567890", # too long (20 digits)
    "4417123456789112",     # invalid check digit
]

def test_add_allowed_card_type() -> None:
    """
    Disables all card types (NONE), so even valid cards should fail validation.
    """
    ccv : Final[CreditCardValidator] = CreditCardValidator(options=CreditCardValidator.NONE)

    assert not ccv.is_valid(_VALID_VISA), f"Expected VISA card {_VALID_VISA} to be invalid with NONE flag"
    assert not ccv.is_valid(_VALID_AMEX), f"Expected AMEX card {_VALID_AMEX} to be invalid with NONE flag"
    assert not ccv.is_valid(_VALID_MASTERCARD), f"Expected MASTERCARD card {_VALID_MASTERCARD} to be invalid with NONE flag"
    assert not ccv.is_valid(_VALID_DISCOVER), f"Expected DISCOVER card {_VALID_DISCOVER} to be invalid with NONE flag"
    assert not ccv.is_valid(_VALID_DINERS), f"Expected DINERS card {_VALID_DINERS} to be invalid with NONE flag"

def test_amex_validator() -> None:
    validator: Final[CodeValidator] = CreditCardValidator.AMEX_VALIDATOR
    regex : Final[RegexValidator] = validator.regex_validator

    # --- Regex: Length checks ---
    assert not regex.is_valid("343456789012"), "Expected False for 12-digit AMEX"
    assert not regex.is_valid("3434567890123"), "Expected False for 13-digit AMEX"
    assert not regex.is_valid("34345678901234"), "Expected False for 14-digit AMEX"
    assert regex.is_valid("343456789012345"), "Expected True for 15-digit AMEX"
    assert not regex.is_valid("3434567890123456"), "Expected False for 16-digit AMEX"
    assert not regex.is_valid("34345678901234567"), "Expected False for 17-digit AMEX"
    assert not regex.is_valid("343456789012345678"), "Expected False for 18-digit AMEX"

    # --- Regex: Prefix checks ---
    assert not regex.is_valid("333456789012345"), "Invalid prefix: 33"
    assert regex.is_valid("343456789012345"), "Valid prefix: 34"
    assert not regex.is_valid("353456789012345"), "Invalid prefix: 35"
    assert not regex.is_valid("363456789012345"), "Invalid prefix: 36"
    assert regex.is_valid("373456789012345"), "Valid prefix: 37"
    assert not regex.is_valid("383456789012345"), "Invalid prefix: 38"
    assert not regex.is_valid("413456789012345"), "Invalid prefix: 41"

    # --- Regex: Invalid character ---
    assert not regex.is_valid("3434567x9012345"), "Invalid character in AMEX number"

    #*********** Test Validator **********
    # --- Validation using is_valid() and validate() ---
    assert regex.is_valid(_ERROR_AMEX), f"Regex should match {_ERROR_AMEX} even if Luhn check fails"
    assert not validator.is_valid(_ERROR_AMEX), f"{_ERROR_AMEX} should fail Luhn validation"
    assert validator.validate(_ERROR_AMEX) is None, f"validate() should return None for invalid {_ERROR_AMEX}"

    assert validator.is_valid(_VALID_AMEX), f"{_VALID_AMEX} should be valid AMEX"
    assert validator.validate(_VALID_AMEX) == _VALID_AMEX, f"validate() should return original value for {_VALID_AMEX}"

    # --- Other card types should be rejected ---
    assert not validator.is_valid(_VALID_DINERS), "Diners card should not validate with AMEX validator"
    assert not validator.is_valid(_VALID_DISCOVER), "Discover card should not validate with AMEX validator"
    assert not validator.is_valid(_VALID_MASTERCARD), "Mastercard should not validate with AMEX validator"
    assert not validator.is_valid(_VALID_VISA), "Visa should not validate with AMEX validator"
    assert not validator.is_valid(_VALID_SHORT_VISA), "Short Visa should not validate with AMEX validator"

    # --- Additional valid AMEX numbers (test data from industry examples) ---
    assert validator.is_valid("371449635398431"), "Valid AMEX (A) should pass"
    assert validator.is_valid("340000000000009"), "Valid AMEX (B) should pass"
    assert validator.is_valid("370000000000002"), "Valid AMEX (C) should pass"
    assert validator.is_valid("378734493671000"), "Valid AMEX (D) should pass"


def test_array_constructor() -> None:
    """
    Test the CodeValidator array constructor.
    Custom validator using only VISA and AMEX validators.
    """
    ccv : Final[CreditCardValidator] = CreditCardValidator(
        credit_card_validators=[
            CreditCardValidator.VISA_VALIDATOR,
            CreditCardValidator.AMEX_VALIDATOR
        ]
    )

    # Valid types
    assert ccv.is_valid(_VALID_VISA), f"Expected VISA {_VALID_VISA} to be valid"
    assert ccv.is_valid(_VALID_SHORT_VISA), f"Expected short VISA {_VALID_SHORT_VISA} to be valid"
    assert ccv.is_valid(_VALID_AMEX), f"Expected AMEX {_VALID_AMEX} to be valid"
    # Invalid types
    assert not ccv.is_valid(_VALID_MASTERCARD), "Mastercard should not be accepted by custom VISA/AMEX validator"
    assert not ccv.is_valid(_VALID_DISCOVER), "Discover should not be accepted by custom VISA/AMEX validator"

    # Invalid numbers
    for card, label in [
        (_ERROR_VISA, "VISA"),
        (_ERROR_SHORT_VISA, "Short VISA"),
        (_ERROR_AMEX, "AMEX"),
        (_ERROR_MASTERCARD, "Mastercard"),
        (_ERROR_DISCOVER, "Discover"),
    ]:
        assert not ccv.is_valid(card), f"{label} card {card} should be invalid"

    # assert default behavior is triggered when None is passed
    ccv_default = CreditCardValidator(credit_card_validators=None)
    assert ccv_default.is_valid(_VALID_VISA)  # this should now succeed if VISA is in the default bitmask

def test_diners_option() -> None:
    """
    Test the Diners Card option
    """
    validator : Final[CreditCardValidator] = CreditCardValidator(options=CreditCardValidator.DINERS)

    assert not validator.is_valid(_ERROR_DINERS), f"{_ERROR_DINERS} should be invalid"
    assert validator.validate(_ERROR_DINERS) is None, f"{_ERROR_DINERS} should return None on validate()"
    assert validator.validate(_VALID_DINERS) == _VALID_DINERS, f"Expected {_VALID_DINERS} to be valid and return itself"

    # Only DINERS should be accepted
    assert not validator.is_valid(_VALID_AMEX), "AMEX should not be valid with DINERS-only validator"
    assert validator.is_valid(_VALID_DINERS), "DINERS card should be valid"
    assert not validator.is_valid(_VALID_DISCOVER), "DISCOVER should not be valid"
    assert not validator.is_valid(_VALID_MASTERCARD), "MASTERCARD should not be valid"
    assert not validator.is_valid(_VALID_VISA), "VISA should not be valid"
    assert not validator.is_valid(_VALID_SHORT_VISA), "Short VISA should not be valid"

def test_diners_validator() -> None:
    """
    Tests the DINERS CodeValidator (regex + Luhn).
    """
    validator: Final[CodeValidator] = CreditCardValidator.DINERS_VALIDATOR
    regex: Final[RegexValidator] = validator.regex_validator

    # --- Regex: Length checks ---
    # --- Regex: Length checks (prefix 300) ---
    assert not regex.is_valid("300456789012"), "Too short (12) - prefix 300"
    assert not regex.is_valid("3004567890123"), "Too short (13) - prefix 300"
    assert regex.is_valid("30045678901234"), "Valid length (14) - prefix 300"
    assert not regex.is_valid("300456789012345"), "Too long (15) - prefix 300"
    assert not regex.is_valid("3004567890123456"), "Too long (16) - prefix 300"
    assert not regex.is_valid("30045678901234567"), "Too long (17) - prefix 300"
    assert not regex.is_valid("300456789012345678"), "Too long (18) - prefix 300"

    # --- Regex: Length checks (prefix 36) ---
    assert not regex.is_valid("363456789012"), "Too short (12) - prefix 36"
    assert not regex.is_valid("3634567890123"), "Too short (13) - prefix 36"
    assert regex.is_valid("36345678901234"), "Valid length (14) - prefix 36"
    assert not regex.is_valid("363456789012345"), "Too long (15) - prefix 36"
    assert not regex.is_valid("3634567890123456"), "Too long (16) - prefix 36"
    assert not regex.is_valid("36345678901234567"), "Too long (17) - prefix 36"
    assert not regex.is_valid("363456789012345678"), "Too long (18) - prefix 36"

    # --- Regex: Prefix checks ---
    #valid prefixes
    triple_valid_prefixes = ["300", "301", "302", "303", "304", "305", ]
    for prefix in triple_valid_prefixes:
        number = prefix + "45678901234"
        assert regex.is_valid(number), f"Expected prefix {prefix} to be valid"
    
    assert regex.is_valid("30955678901234"), f"Expected prefix 3095 to be valid"
    assert regex.is_valid("36345678901234"), f"Expected prefix 36 to be valid"
    assert regex.is_valid("38345678901234"), f"Expected prefix 38 to be valid"
    assert regex.is_valid("39345678901234"), f"Expected prefix 39 to be valid"

   
    #invalid prefixes
    assert not regex.is_valid("30645678901234"), f"Expected prefix 306 to be invalid"   
    assert not regex.is_valid("30945678901234"), f"Expected prefix 3094 to be invalid"   
    assert not regex.is_valid("30965678901234"), f"Expected prefix 3096 to be invalid"
    assert not regex.is_valid("35345678901234"), f"Expected prefix 35 to be invalid" 
    assert not regex.is_valid("37345678901234"), f"Expected prefix 37 to be invalid"      

    # --- Regex: Invalid chars ---
    assert not regex.is_valid("3004567x901234"), "Invalid char in prefix 300"
    assert not regex.is_valid("3634567x901234"), "Invalid char in prefix 36"

    # --- Validator ---
    assert regex.is_valid(_ERROR_DINERS), "Regex should match even if Luhn fails"
    assert not validator.is_valid(_ERROR_DINERS), "Invalid DINERS should fail Luhn"
    assert validator.validate(_ERROR_DINERS) is None, "Invalid DINERS should return None"

    assert validator.is_valid(_VALID_DINERS), "Valid DINERS should pass"
    assert validator.validate(_VALID_DINERS) == _VALID_DINERS, "Expected original DINERS on validate()"

    # Should not accept other types
    for label, card in [
        ("AMEX", _VALID_AMEX),
        ("DISCOVER", _VALID_DISCOVER),
        ("MASTERCARD", _VALID_MASTERCARD),
        ("VISA", _VALID_VISA),
        ("VISA (short)", _VALID_SHORT_VISA),
    ]:
        assert not validator.is_valid(card), f"{label} card should not validate as DINERS"

    # Additional known-valid test cards
    for card in [
        "30000000000004",
        "30123456789019",
        "36432685260294"
    ]:
        assert validator.is_valid(card), f"Expected {card} to be valid DINERS"


def test_discover_option() -> None:
    """
    Tests a CreditCardValidator with DISCOVER option only.
    """
    validator: Final[CreditCardValidator] = CreditCardValidator(options=CreditCardValidator.DISCOVER)

    # Luhn fail
    assert not validator.is_valid(_ERROR_DISCOVER), "Expected ERROR_DISCOVER to be invalid"
    assert not validator.is_valid(_ERROR_DISCOVER65), "Expected ERROR_DISCOVER65 to be invalid"
    assert validator.validate(_ERROR_DISCOVER) is None, "validate() should return None for ERROR_DISCOVER"

    # Luhn pass
    assert validator.validate(_VALID_DISCOVER) == _VALID_DISCOVER, "Expected VALID_DISCOVER to validate"
    assert validator.validate(_VALID_DISCOVER65) == _VALID_DISCOVER65, "Expected VALID_DISCOVER65 to validate"

    # accept Discover type
    assert validator.is_valid(_VALID_DISCOVER), "VALID_DISCOVER should be accepted"
    assert validator.is_valid(_VALID_DISCOVER65), "VALID_DISCOVER65 should be accepted"

    # Should reject other types
    for label, card in [
        ("AMEX", _VALID_AMEX),
        ("DINERS", _VALID_DINERS),
        ("MASTERCARD", _VALID_MASTERCARD),
        ("VISA", _VALID_VISA),
        ("VISA (short)", _VALID_SHORT_VISA),
    ]:
        assert not validator.is_valid(card), f"{label} card should not validate under DISCOVER-only validator"

def test_discover_validator() -> None:
    """
    Tests the DISCOVER CodeValidator (regex + Luhn).
    """
    validator: Final[CodeValidator] = CreditCardValidator.DISCOVER_VALIDATOR
    regex: Final[RegexValidator] = validator.regex_validator

    # --- Length checks for prefix 6011 and 65 ---
    assert not regex.is_valid("601156789012"), "Too short (12) - 6011"
    assert not regex.is_valid("653456789012"), "Too short (12) - 65"
    assert not regex.is_valid("6011567890123"), "Too short (13) - 6011"
    assert not regex.is_valid("6534567890123"), "Too short (13) - 65"
    assert not regex.is_valid("60115678901234"), "Too short (14) - 6011"
    assert not regex.is_valid("65345678901234"), "Too short (14) - 65"
    assert not regex.is_valid("601156789012345"), "Too short (15) - 6011"
    assert not regex.is_valid("653456789012345"), "Too short (15) - 65"
    assert regex.is_valid("6011567890123456"), "Valid length (16) - 6011"
    assert regex.is_valid("6444567890123456"), "Valid prefix 644"
    assert regex.is_valid("6484567890123456"), "Valid prefix 648"
    assert regex.is_valid("6534567890123456"), "Valid prefix 65"
    assert not regex.is_valid("65345678901234567"), "Too long (17) - 65"
    assert not regex.is_valid("601156789012345678"), "Too long (18) - 6011"
    assert not regex.is_valid("653456789012345678"), "Too long (18) - 65"

    # --- Invalid prefixes ---
    invalid_prefixes = [
        "640", "641", "642", "643",  # below 644
        "6010", "6012"              # not 6011
    ]
    for prefix in invalid_prefixes:
        number = prefix + "567890123456"
        assert not regex.is_valid(number), f"Invalid Discover prefix: {prefix}"

    # --- Invalid characters ---
    assert not regex.is_valid("6011567x90123456"), "Invalid char in Discover number"

    # --- Test Validator ---
    assert regex.is_valid(_ERROR_DISCOVER), "Regex should match even if Luhn fails"
    assert regex.is_valid(_ERROR_DISCOVER65), "Regex should match even if Luhn fails"
    assert not validator.is_valid(_ERROR_DISCOVER), "Should fail Luhn check (6011)"
    assert not validator.is_valid(_ERROR_DISCOVER65), "Should fail Luhn check (65)"
    assert validator.validate(_ERROR_DISCOVER) is None, "validate() should return None for Luhn-failing 6011"

    assert validator.validate(_VALID_DISCOVER) == _VALID_DISCOVER, "Valid Discover (6011)"
    assert validator.validate(_VALID_DISCOVER65) == _VALID_DISCOVER65, "Valid Discover (65)"

    assert validator.is_valid(_VALID_DISCOVER), "VALID_DISCOVER should pass"
    assert validator.is_valid(_VALID_DISCOVER65), "VALID_DISCOVER65 should pass"

    # Reject other cards
    for label, card in [
        ("AMEX", _VALID_AMEX),
        ("DINERS", _VALID_DINERS),
        ("MASTERCARD", _VALID_MASTERCARD),
        ("VISA", _VALID_VISA),
        ("VISA (short)", _VALID_SHORT_VISA),
    ]:
        assert not validator.is_valid(card), f"{label} card should not validate as Discover"

    # Additional valid Discover test numbers
    for card in [
        "6011111111111117",
        "6011000000000004",
        "6011000000000012"
    ]:
        assert validator.is_valid(card), f"Expected Discover test card {card} to be valid"

def test_disjoint_range() -> None:
    """
    Tests custom CreditCardRange validation logic.
    """
    range_13_16: Final = CreditCardValidator.CreditCardRange(low="305", high="4", lengths=[13, 16])
    ccv: Final[CreditCardValidator] = CreditCardValidator(credit_card_ranges=[range_13_16])

    assert len(_VALID_SHORT_VISA) == 13
    assert len(_VALID_VISA) == 16
    assert len(_VALID_DINERS) == 14

    # Should accept VISA 13 and 16-digit cards
    assert ccv.is_valid(_VALID_SHORT_VISA), f"Expected valid 13-digit VISA {_VALID_SHORT_VISA}"
    assert ccv.is_valid(_VALID_VISA), f"Expected valid 16-digit VISA {_VALID_VISA}"

    # Should reject invalid VISA
    assert not ccv.is_valid(_ERROR_SHORT_VISA), f"Invalid VISA (13) should fail"
    assert not ccv.is_valid(_ERROR_VISA), f"Invalid VISA (16) should fail"

    # Should reject 14-digit Diners (not in allowed lengths)
    assert not ccv.is_valid(_VALID_DINERS), "14-digit Diners should fail with lengths=[13, 16]"

    # Now add 14 to valid lengths
    range_13_14_16: Final = CreditCardValidator.CreditCardRange(low="305", high="4", lengths=[13, 14, 16])
    ccv_with_14: Final[CreditCardValidator] = CreditCardValidator(credit_card_ranges=[range_13_14_16])
    assert ccv_with_14.is_valid(_VALID_DINERS), "Expected Diners card to be valid when 14-digit is allowed"

def test_generic() -> None:
    """
    Tests the genericCreditCardValidator() using default card types.
    """
    ccv: Final[CreditCardValidator] = CreditCardValidator.generic_credit_card_validator()
    
    for card in _VALID_CARDS:
        assert ccv.is_valid(card), f"Expected valid card to pass: {card}"

    for card in _ERROR_CARDS:
        assert not ccv.is_valid(card), f"Expected invalid card to fail: {card}"

def test_is_valid() -> None:
    """
    Full validation using the default CreditCardValidator constructor.
    Includes edge cases like null, empty string, length violations, and bad characters.
    """
    ccv: Final[CreditCardValidator] = CreditCardValidator()

    # Null / blank input
    assert ccv.validate(None) is None, "validate(None) should return None"
    assert not ccv.is_valid(None), "is_valid(None) should return False"
    assert not ccv.is_valid(""), "Empty string should be invalid"

    # Length violations
    assert not ccv.is_valid("123456789012"), "Too short (12 digits) should fail"
    assert not ccv.is_valid("12345678901234567890"), "Too long (20 digits) should fail"

    # Invalid characters
    assert not ccv.is_valid("4417123456789112"), "Invalid check digit should fail"
    assert not ccv.is_valid("4417q23456w89113"), "Non-digit characters should fail"

    # Valid cards
    for card in [
        _VALID_VISA,
        _VALID_SHORT_VISA,
        _VALID_AMEX,
        _VALID_MASTERCARD,
        _VALID_DISCOVER,
        _VALID_DISCOVER65
    ]:
        assert ccv.is_valid(card), f"Expected card to pass: {card}"

    # Invalid cards
    for card in [
        _ERROR_VISA,
        _ERROR_SHORT_VISA,
        _ERROR_AMEX,
        _ERROR_MASTERCARD,
        _ERROR_DISCOVER,
        _ERROR_DISCOVER65
    ]:
        assert not ccv.is_valid(card), f"Expected card to fail: {card}"

    # AMEX-only validator should not accept valid VISA
    amex_only: Final = CreditCardValidator(options=CreditCardValidator.AMEX)
    assert not amex_only.is_valid(_VALID_VISA), "VISA should fail when only AMEX is enabled"

def test_mastercard_option() -> None:
    """
    Tests CreditCardValidator with only MASTERCARD option.
    """
    validator: Final[CreditCardValidator] = CreditCardValidator(options=CreditCardValidator.MASTERCARD)

    assert not validator.is_valid(_ERROR_MASTERCARD), "Invalid Mastercard should fail is_valid()"
    assert validator.validate(_ERROR_MASTERCARD) is None, "validate() should return None for invalid Mastercard"
    assert validator.validate(_VALID_MASTERCARD) == _VALID_MASTERCARD, "Valid Mastercard should return itself"
    
    assert validator.is_valid(_VALID_MASTERCARD), "Valid Mastercard should pass"

    # Other card types should not validate
    for label, card in [
        ("AMEX", _VALID_AMEX),
        ("DINERS", _VALID_DINERS),
        ("DISCOVER", _VALID_DISCOVER),
        ("VISA", _VALID_VISA),
        ("VISA (short)", _VALID_SHORT_VISA),
    ]:
        assert not validator.is_valid(card), f"{label} should not pass with MASTERCARD-only validator"

def test_mastercard_using_separators() -> None:
    """
    Tests Mastercard regex with various valid separator formats.
    """
    mastercard_regex_sep: Final[str] = r"^(5[1-5]\d{2})(?:[- ])?(\d{4})(?:[- ])?(\d{4})(?:[- ])?(\d{4})$"
    validator: Final[CodeValidator] = CodeValidator(regex=mastercard_regex_sep, checkdigit=LuhnCheckDigit.LUHN_CHECK_DIGIT)
    regex: Final[RegexValidator] = validator.regex_validator

    # Valid formats
    valid_cases: Final[list[tuple[str, str]]] = [
        ("5134567890123456", "Number"),
        ("5134-5678-9012-3456", "Hyphen"),
        ("5134 5678 9012 3456", "Space"),
        ("5134-5678 9012-3456", "MixedA"),
        ("5134 5678-9012 3456", "MixedB"),
    ]

    for number, label in valid_cases:
        assert regex.validate(number) == "5134567890123456", f"{label} input should normalize to 5134567890123456"

    # Invalid separators and groupings
    invalid_cases: Final[list[tuple[str, str]]] = [
        ("5134.5678.9012.3456", "Invalid Separator A"),
        ("5134_5678_9012_3456", "Invalid Separator B"),
        ("513-45678-9012-3456", "Invalid Grouping A"),
        ("5134-567-89012-3456", "Invalid Grouping B"),
        ("5134-5678-901-23456", "Invalid Grouping C"),
    ]

    for number, label in invalid_cases:
        assert not regex.is_valid(number), f"{label} input {number} should be invalid"

    # Luhn validated numbers with valid formatting
    valid_luhn_cases: Final[list[tuple[str, str]]] = [
        ("5500-0000-0000-0004", "Valid-A"),
        ("5424 0000 0000 0015", "Valid-B"),
        ("5301-250070000191", "Valid-C"),
        ("5123456789012346", "Valid-D"),
    ]

    for number, label in valid_luhn_cases:
        expected = number.replace(" ", "").replace("-", "")
        assert validator.validate(number) == expected, f"{label} should normalize and validate as {expected}"

def test_mastercard_validator() -> None:
    """
    Tests the MASTERCARD CodeValidator (regex + Luhn).
    """
    validator: Final[CodeValidator] = CreditCardValidator.MASTERCARD_VALIDATOR
    regex: Final[RegexValidator] = validator.regex_validator

    # --- Length checks (12–18 digits) ---
    assert not regex.is_valid("513456789012"), "Too short (12 digits)"
    assert not regex.is_valid("5134567890123"), "Too short (13 digits)"
    assert not regex.is_valid("51345678901234"), "Too short (14 digits)"
    assert not regex.is_valid("513456789012345"), "Too short (15 digits)"
    assert regex.is_valid("5134567890123456"), "Valid length (16 digits)"
    assert not regex.is_valid("51345678901234567"), "Too long (17 digits)"
    assert not regex.is_valid("513456789012345678"), "Too long (18 digits)"

    # --- Prefix checks ---
    valid_prefixes = ["51", "52", "53", "54", "55"]
    for prefix in valid_prefixes:
        number = prefix + "34567890123456"
        assert regex.is_valid(number), f"Valid Mastercard prefix: {prefix}"

    invalid_prefixes = ["41", "50", "56", "61"]
    for prefix in invalid_prefixes:
        number = prefix + "34567890123456"
        assert not regex.is_valid(number), f"Invalid prefix: {prefix}"

    # --- Invalid character ---
    assert not regex.is_valid("5134567x90123456"), "Should reject non-digit characters"

    # --- Test Validator ---
    # --- Regex match but Luhn fails ---
    assert regex.is_valid(_ERROR_MASTERCARD), "Regex should match even if Luhn fails"
    assert not validator.is_valid(_ERROR_MASTERCARD), "Should fail Luhn validation"
    assert validator.validate(_ERROR_MASTERCARD) is None, "validate() should return None"

    # --- Fully valid card ---
    assert validator.is_valid(_VALID_MASTERCARD), "Should accept valid Mastercard"
    assert validator.validate(_VALID_MASTERCARD) == _VALID_MASTERCARD, "validate() should return original"

    # --- Should reject other card types ---
    for label, card in [
        ("AMEX", _VALID_AMEX),
        ("DINERS", _VALID_DINERS),
        ("DISCOVER", _VALID_DISCOVER),
        ("VISA", _VALID_VISA),
        ("VISA (short)", _VALID_SHORT_VISA),
    ]:
        assert not validator.is_valid(card), f"{label} should not be accepted by Mastercard validator"

    # --- Known-valid Mastercard test numbers ---
    valid_mastercards: Final[list[str]] = [
        "5500000000000004",  # A
        "5424000000000015",  # B
        "5301250070000191",  # C
        "5123456789012346",  # D
        "5555555555554444",  # E
    ]
    for card in valid_mastercards:
        assert validator.is_valid(card), f"Expected valid Mastercard: {card}"

    # --- Extensive range test: 222100–272099 (new Mastercard range) ---
    rev: Final[RegexValidator] = validator.regex_validator
    pad: Final[str] = "0000000000"  # makes 16-digit cards

    assert not rev.is_valid("222099" + pad), "Prefix 222099 should be invalid"

    for i in range(222100, 272100):
        card = f"{i}{pad}"
        assert rev.is_valid(card), f"Expected prefix {i} to be valid Mastercard"

    assert not rev.is_valid("272100" + pad), "Prefix 272100 should be invalid (outside Mastercard range)"

def test_range_generator() -> None:
    """
    Combines standard validators with additional custom range-based validators.
    """
    # Built-in validators for AMEX, VISA, MASTERCARD, DISCOVER
    validators: Final[list[CodeValidator]] = [
        CreditCardValidator.AMEX_VALIDATOR,
        CreditCardValidator.VISA_VALIDATOR,
        CreditCardValidator.MASTERCARD_VALIDATOR,
        CreditCardValidator.DISCOVER_VALIDATOR
    ]

    # Range-based validators for Diners (not part of above list)
    ranges: Final[list[CreditCardValidator.CreditCardRange]] = [
        CreditCardValidator.CreditCardRange("300", "305", 14, 14),
        CreditCardValidator.CreditCardRange("3095", None, 14, 14),
        CreditCardValidator.CreditCardRange("36", None, 14, 14),
        CreditCardValidator.CreditCardRange("38", "39", 14, 14),
    ]

    ccv: Final[CreditCardValidator] = CreditCardValidator(
        credit_card_validators=validators,
        credit_card_ranges=ranges
    )

    # Valid cards should pass
    for card in _VALID_CARDS:
        assert ccv.is_valid(card), f"Expected valid card: {card}"

    # Error cards should fail
    for card in _ERROR_CARDS:
        assert not ccv.is_valid(card), f"Expected invalid card: {card}"


def test_range_generator_no_luhn() -> None:
    """
    Tests prefix + length range validator without any Luhn check.
    """
    # Create validator that accepts:
    # - Prefixes starting with "1", length 6 or 7
    # - Prefixes 644–65, length 8
    ranges: Final[list[CreditCardValidator.CreditCardRange]] = [
        CreditCardValidator.CreditCardRange("1", None, 6, 7),
        CreditCardValidator.CreditCardRange("644", "65", 8, 8),
    ]

    validator: Final[CreditCardValidator] = CreditCardValidator.create_range_validator(
        CreditCardValidator,
        ranges=ranges,
        check_digit=None
    )

    # Prefix "1", length 6 or 7
    assert validator.is_valid("1990000"), "1990000 should be valid (prefix 1, len 7)"
    assert validator.is_valid("199000"), "199000 should be valid (prefix 1, len 6)"
    assert not validator.is_valid("000000"), "Prefix 0 should be invalid"
    assert not validator.is_valid("099999"), "Prefix 0 should be invalid"
    assert not validator.is_valid("200000"), "Prefix 2 should be invalid"

    # Prefix 644–65, length 8
    assert not validator.is_valid("64399999"), "643 prefix below range"
    assert validator.is_valid("64400000"), "644 prefix valid"
    assert validator.is_valid("64900000"), "649 prefix valid"
    assert validator.is_valid("65000000"), "650 prefix valid"
    assert validator.is_valid("65999999"), "659 prefix valid"
    assert not validator.is_valid("66000000"), "660 prefix above range"


def test_valid_length() -> None:
    """
    Unit test for validLength() static method.
    Checks both min/max and specific length list variants.
    """
    # --- Single length: 14 ---
    range_14: Final = CreditCardValidator.CreditCardRange("", "", 14, 14)
    assert CreditCardValidator.valid_length(14, range_14), "14 should be valid for [14,14]"
    assert not CreditCardValidator.valid_length(15, range_14), "15 should not be valid for [14,14]"
    assert not CreditCardValidator.valid_length(13, range_14), "13 should not be valid for [14,14]"

    # --- Range: 15–17 ---
    range_15_17: Final = CreditCardValidator.CreditCardRange("", "", 15, 17)
    assert not CreditCardValidator.valid_length(14, range_15_17), "14 should not be valid for [15–17]"
    assert CreditCardValidator.valid_length(15, range_15_17), "15 should be valid for [15–17]"
    assert CreditCardValidator.valid_length(16, range_15_17), "16 should be valid for [15–17]"
    assert CreditCardValidator.valid_length(17, range_15_17), "17 should be valid for [15–17]"
    assert not CreditCardValidator.valid_length(18, range_15_17), "18 should not be valid for [15–17]"

    # --- Explicit list: [15, 17] ---
    range_explicit: Final = CreditCardValidator.CreditCardRange("", "", lengths=[15, 17])
    assert not CreditCardValidator.valid_length(14, range_explicit), "14 should not be valid for [15,17]"
    assert CreditCardValidator.valid_length(15, range_explicit), "15 should be valid for [15,17]"
    assert not CreditCardValidator.valid_length(16, range_explicit), "16 should not be valid for [15,17]"
    assert CreditCardValidator.valid_length(17, range_explicit), "17 should be valid for [15,17]"
    assert not CreditCardValidator.valid_length(18, range_explicit), "18 should not be valid for [15,17]"


def test_visa_option() -> None:
    """
    Tests CreditCardValidator with only the VISA flag enabled.
    """
    validator: Final[CreditCardValidator] = CreditCardValidator(options=CreditCardValidator.VISA)

    assert not validator.is_valid(_ERROR_VISA), f"{_ERROR_VISA} should be invalid"
    assert not validator.is_valid(_ERROR_SHORT_VISA), f"{_ERROR_SHORT_VISA} should be invalid (check digit)"
    assert validator.validate(_ERROR_VISA) is None, f"validate() should return None for {_ERROR_VISA}"

    assert validator.validate(_VALID_VISA) == _VALID_VISA, "Valid VISA should pass validate()"
    assert validator.validate(_VALID_SHORT_VISA) == _VALID_SHORT_VISA, "Valid short VISA should pass validate()"

    assert not validator.is_valid(_VALID_AMEX), "AMEX should not be valid for VISA-only validator"
    assert not validator.is_valid(_VALID_DINERS), "DINERS should not be valid"
    assert not validator.is_valid(_VALID_DISCOVER), "DISCOVER should not be valid"
    assert not validator.is_valid(_VALID_MASTERCARD), "MASTERCARD should not be valid"

    assert validator.is_valid(_VALID_VISA), "VISA should be valid"
    assert validator.is_valid(_VALID_SHORT_VISA), "Short VISA should be valid"

def test_visa_validator() -> None:
    """
    Tests the VISA CodeValidator (regex + Luhn).
    """
    validator: Final[CodeValidator] = CreditCardValidator.VISA_VALIDATOR
    regex: Final[RegexValidator] = validator.regex_validator

    # --- Length checks ---
    assert not regex.is_valid("423456789012"), "Too short (12)"
    assert regex.is_valid("4234567890123"), "Valid length (13)"
    assert not regex.is_valid("42345678901234"), "Invalid length (14)"
    assert not regex.is_valid("423456789012345"), "Invalid length (15)"
    assert regex.is_valid("4234567890123456"), "Valid length (16)"
    assert not regex.is_valid("42345678901234567"), "Too long (17)"
    assert not regex.is_valid("423456789012345678"), "Too long (18)"

    # --- Invalid prefixes and characters ---
    assert not regex.is_valid("3234567890123"), "Invalid prefix (32)"
    assert not regex.is_valid("3234567890123456"), "Invalid prefix (32)"
    assert not regex.is_valid("4234567x90123"), "Invalid character in short VISA"
    assert not regex.is_valid("4234567x90123456"), "Invalid character in long VISA"

    # --- Validator behavior ---
    assert regex.is_valid(_ERROR_VISA), "Regex should match ERROR_VISA"
    assert regex.is_valid(_ERROR_SHORT_VISA), "Regex should match ERROR_SHORT_VISA"
    assert not validator.is_valid(_ERROR_VISA), "Invalid check digit - ERROR_VISA"
    assert not validator.is_valid(_ERROR_SHORT_VISA), "Invalid check digit - ERROR_SHORT_VISA"
    assert validator.validate(_ERROR_VISA) is None, "validate() should return None for ERROR_VISA"
    
    assert validator.validate(_VALID_VISA) == _VALID_VISA, "validate() should return original VISA"
    assert validator.validate(_VALID_SHORT_VISA) == _VALID_SHORT_VISA, "validate() should return original short VISA"

    # --- Card type exclusions ---
    for label, card in [
        ("AMEX", _VALID_AMEX),
        ("DINERS", _VALID_DINERS),
        ("DISCOVER", _VALID_DISCOVER),
        ("MASTERCARD", _VALID_MASTERCARD)
    ]:
        assert not validator.is_valid(card), f"{label} should not be valid with VISA validator"

    # --- Should accept valid VISA numbers ---
    valid_visas: Final[list[str]] = [
        "4111111111111111",  # A
        "4543059999999982",  # C
        "4462000000000003",  # B
        "4508750000000009",  # D (Electron)
        "4012888888881881",  # E
    ]
    for card in valid_visas:
        assert validator.is_valid(card), f"Expected valid VISA: {card}"

def test_vpay_option() -> None:
    """
    Tests the VPAY-specific CreditCardValidator option.
    """
    validator: Final[CreditCardValidator] = CreditCardValidator(options=CreditCardValidator.VPAY)

    assert validator.is_valid(_VALID_VPAY), "Expected VALID_VPAY to be valid"
    assert validator.is_valid(_VALID_VPAY2), "Expected VALID_VPAY2 to be valid"
    assert not validator.is_valid(_ERROR_VPAY), "Expected ERROR_VPAY to be invalid"

    assert validator.validate(_VALID_VPAY) == _VALID_VPAY, "validate() should return original VALID_VPAY"
    assert validator.validate(_VALID_VPAY2) == _VALID_VPAY2, "validate() should return original VALID_VPAY2"

    # Other cards should not validate
    for label, card in [
        ("AMEX", _VALID_AMEX),
        ("DINERS", _VALID_DINERS),
        ("DISCOVER", _VALID_DISCOVER),
        ("MASTERCARD", _VALID_MASTERCARD),
    ]:
        assert not validator.is_valid(card), f"{label} should not pass with VPAY-only validator"

    # Note: VPAY regex accepts a subset of VISA patterns, so VISA cards may still pass
    assert validator.is_valid(_VALID_VISA), "VISA may be accepted by VPAY validator (shared prefix)"
    assert validator.is_valid(_VALID_SHORT_VISA), "Short VISA may be accepted by VPAY validator (shared prefix)"
