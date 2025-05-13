""" 
Module Name: credit_card_validator.py

Description: Translates apache.commons.validator.routines.CreditCardValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/CreditCardValidator.java
 
Author: Alicia Chu

License (Taken from apache.commons.validator.routines.CreditCardValidator.java):
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
Changes:
   In Java, the CreditCardValidator class has multiple overloaded constructors but 
   , in Python, all that flexibility is handled in a single __init__ method.


"""
from typing import Final, Optional
from src.apache_commons_validator_python.routines.code_validator import CodeValidator
from src.apache_commons_validator_python.routines.regex_validator import RegexValidator
from src.apache_commons_validator_python.generic_validator_new import GenericValidator
from src.apache_commons_validator_python.routines.checkdigit.checkdigit import CheckDigit
from src.apache_commons_validator_python.routines.checkdigit.luhn_checkdigit import LuhnCheckDigit

class CreditCardValidator:
    """Validates credit card numbers based on known issuer patterns, numeric format, and
    Luhn check digit rules.

    This class supports multiple built-in credit card types such as Visa, MasterCard,
    American Express, Discover, Diners, and VPay. It can also be configured with
    custom validation rules, either through regular expressions or prefix-based
    range validation.

    Attributes:
        serializable (bool): Indicates that instances can be serialized (always True).
        cloneable (bool): Indicates whether instances can be cloned (always False).

    Usage:
        - Use the default constructor to validate common card types.
        - Use `generic_credit_card_validator()` to validate any numeric card
          number within a length range using only Luhn check.
        - Extend with custom `CodeValidator` or range-based validators for
          specialized card types.
    """
    serializable = True    # class is serializable
    cloneable = False      # class is not cloneable
    
    class CreditCardRange:
        """Represents a credit card number range for validating issuer prefix (IIN) and
        permissible card number lengths.

        Attributes:
            low (str): The starting IIN prefix of the range (inclusive).
            high (Optional[str]): The ending IIN prefix of the range (inclusive). If None, only 'low' is used.
            min_len (int): Minimum card number length. Ignored if 'lengths' is provided.
            max_len (int): Maximum card number length. Ignored if 'lengths' is provided.
            lengths (Optional[list[int]]): Explicit list of valid lengths. If provided, overrides min_len/max_len.

        Used to define card validation logic for ranges like:
        - '400000' to '499999' for Visa
        - '510000' to '559999' for older MasterCard prefixes
        """

        def __init__(
            self,
            low: str,
            high: Optional[str] = None,
            min_len: int = -1,
            max_len: int = -1,
            lengths: Optional[list[int]] = None
        ):
            self.low: Final[str] = low
            self.high: Final[Optional[str]] = high
            self.min_len: Final[int] = min_len
            self.max_len: Final[int] = max_len
            self.lengths: Final[Optional[list[int]]] = lengths.copy() if lengths is not None else None

         

    
    # Constants for card type flags
    #int instead of long
    NONE: Final[int] = 0
    AMEX: Final[int] = 1 << 0
    VISA: Final[int] = 1 << 1
    MASTERCARD: Final[int] = 1 << 2
    DISCOVER: Final[int] = 1 << 3
    DINERS: Final[int] = 1 << 4
    VPAY: Final[int] = 1 << 5
    MASTERCARD_PRE_OCT2016: Final[int] = 1 << 6  # Deprecated

    MIN_CC_LENGTH: Final[int] = 12 #minimum allowed length
    MAX_CC_LENGTH: Final[int] = 19 # maximum allowed length

    # Luhn checkdigit validator for the card numbers.
    LUHN_VALIDATOR: Final = LuhnCheckDigit.LUHN_CHECK_DIGIT
    """ 
     American Express (Amex) Card Validator
     <ul>
     <li>34xxxx (15)</li>
     <li>37xxxx (15)</li>
     </ul>
     """
    AMEX_VALIDATOR: Final = CodeValidator(regex=r"^(3[47]\d{13})$", checkdigit=LUHN_VALIDATOR)
    """
     Diners Card Validator
     <ul>
     <li>300xxx - 305xxx (14)</li>
     <li>3095xx (14)</li>
     <li>36xxxx (14)</li>
     <li>38xxxx (14)</li>
     <li>39xxxx (14)</li>
     </ul>
    """
    DINERS_VALIDATOR: Final = CodeValidator(regex=r"^(30[0-5]\d{11}|3095\d{10}|36\d{12}|3[8-9]\d{12})$", checkdigit=LUHN_VALIDATOR)
    """
    Discover Card regular expressions
     <ul>
     <li>6011xx (16)</li>
     <li>644xxx - 65xxxx (16)</li>
     </ul> 
    """
    DISCOVER_REGEX: Final = [
    r"^(6011\d{12,13})$",
    r"^(64[4-9]\d{13})$",
    r"^(65\d{14})$",
    r"^(62[2-8]\d{13})$"
    ]
    DISCOVER_VALIDATOR: Final = CodeValidator(regex=DISCOVER_REGEX, checkdigit=LUHN_VALIDATOR)

    MASTERCARD_REGEX: Final = [
        r"^(5[1-5]\d{14})$",      # Pre-Oct 2016
        r"^(2221\d{12})$",        # 222100–222199
        r"^(222[2-9]\d{12})$",    # 222200 - 222999
        r"^(22[3-9]\d{13})$",
        r"^(2[3-6]\d{14})$",
        r"^(27[01]\d{13})$",
        r"^(2720\d{12})$"
    ]
    MASTERCARD_VALIDATOR: Final = CodeValidator(regex=MASTERCARD_REGEX, checkdigit=LUHN_VALIDATOR)
    """
     Mastercard Card Validator (pre Oct 2016)
     @deprecated for use until Oct 2016 only
    """
    MASTERCARD_VALIDATOR_PRE_OCT2016: Final = CodeValidator(regex=r"^(5[1-5]\d{14})$", checkdigit=LUHN_VALIDATOR)

    VISA_VALIDATOR: Final = CodeValidator(regex=r"^(4)(\d{12}|\d{15})$", checkdigit=LUHN_VALIDATOR)
    VPAY_VALIDATOR: Final = CodeValidator(regex=r"^(4)(\d{12,18})$", checkdigit=LUHN_VALIDATOR)


    def __init__(
    self,
    options: int = AMEX | VISA | MASTERCARD | DISCOVER,
    credit_card_validators: Optional[list[CodeValidator]] = None,
    credit_card_ranges: Optional[list["CreditCardValidator"]] = None,
    ):
        """Initializes a CreditCardValidator instance with built-in or custom
        validators.

        Args:
            options (int, optional): Bitmask flags indicating which built-in card types
                to include (e.g., VISA, AMEX, etc.). Defaults to a combination of
                AMEX, VISA, MASTERCARD, and DISCOVER. Ignored if `credit_card_validators`
                or `credit_card_ranges` is provided.

            credit_card_validators (Optional[list[CodeValidator]]): A custom list of
                `CodeValidator` instances. Each validator defines its own regex and
                check digit logic. Appended to the list of active validators.

            credit_card_ranges (Optional[list[CreditCardRange]]): A list of credit card
                ranges to validate against, using IIN prefix and length rules. Combined
                into a single range-based validator with Luhn check digit logic.

        Notes:
            - If neither `credit_card_validators` nor `credit_card_ranges` is provided,
            the constructor will fall back to using the bitmask `options` to configure
            a default set of built-in card validators.
            - All validators are stored in `self.card_types` and checked in order.
        """
        self.card_types: list[CodeValidator] = []

        # Built-in bitmask validators (used if no explicit validators given)
        if credit_card_validators is None and credit_card_ranges is None:
            if self.is_on(options, self.VISA):
                self.card_types.append(self.VISA_VALIDATOR)
            if self.is_on(options, self.VPAY):
                self.card_types.append(self.VPAY_VALIDATOR)
            if self.is_on(options, self.AMEX):
                self.card_types.append(self.AMEX_VALIDATOR)
            if self.is_on(options, self.MASTERCARD):
                self.card_types.append(self.MASTERCARD_VALIDATOR)
            if self.is_on(options, self.MASTERCARD_PRE_OCT2016):
                self.card_types.append(self.MASTERCARD_VALIDATOR_PRE_OCT2016)
            if self.is_on(options, self.DISCOVER):
                self.card_types.append(self.DISCOVER_VALIDATOR)
            if self.is_on(options, self.DINERS):
                self.card_types.append(self.DINERS_VALIDATOR)

        # Add custom validators (if provided)
        if credit_card_validators is not None:
            self.card_types.extend(credit_card_validators)

        # Add range-based validator (if provided)
        if credit_card_ranges is not None:
            self.card_types.append(self.create_range_validator(credit_card_ranges, self.LUHN_VALIDATOR))


    @staticmethod
    def valid_length(value_length: int, range: CreditCardRange) -> bool:
        """Checks whether a given length is valid based on either an explicit list or a
        min/max range for the credit card.

        Args:
            value_length: The length of the credit card number.
            range: The CreditCardRange to validate against.

        Returns:
            True if the length is valid, False otherwise.
        """
        if range.lengths:
            return value_length in range.lengths
        return range.min_len <= value_length <= range.max_len
    
    @staticmethod
    def is_on(options: int, flag: int) -> bool:
        """Checks if a bitmask flag is enabled in the options.
        
        Args:
            options: Bitmask of all enabled flags.
            flag: The specific flag to check.

        Returns:
            True if the flag is enabled in options, False otherwise.
        """
        return (options & flag) > 0
    
    def is_valid(self, card: str) -> bool:
        """Returns True if the card is valid according to any of the configured card
        types.
        
        Args:
            card: The credit card number as a string.

         Returns:
            True if the card is valid, False otherwise.
        """
        if GenericValidator.is_blank_or_null(card):
            return False
        return any(validator.is_valid(card) for validator in self.card_types)

    def validate(self, card: str) -> Optional[str]:
        """Validates the card and returns the cleaned card number if valid, otherwise
        None.

        Args:
            card: The credit card number to validate.

        Returns:
            The card number if valid, or None if invalid.
        """
        if GenericValidator.is_blank_or_null(card):
            return None
        for validator in self.card_types:
            result = validator.validate(card)
            if result is not None:
                return result
        return None
    
    @classmethod
    def generic_credit_card_validator(cls) -> "CreditCardValidator":
        """Creates a validator that only checks for numeric card numbers with Luhn
        validation, using the default min and max length.
        
        Returns:
            A CreditCardValidator instance using numeric+Luhn check.
        """
        return cls.generic_credit_card_validator_with_range(cls.MIN_CC_LENGTH, cls.MAX_CC_LENGTH)

    @classmethod
    def generic_credit_card_validator_with_exact_length(cls, length: int) -> "CreditCardValidator":
        """Creates a validator for a specific length, e.g., 16-digit cards.
        
        Args:
            length: The exact card length to validate.

        Returns:
            A CreditCardValidator configured to check that length.
        """
        return cls.generic_credit_card_validator_with_range(length, length)

    @classmethod
    def generic_credit_card_validator_with_range(cls, min_len: int, max_len: int) -> "CreditCardValidator":
        """Creates a validator that only ensures the card is numeric, within a given
        length range, and passes the Luhn check.
        
        Args:
            min_len: Minimum allowed length.
            max_len: Maximum allowed length.

        Returns:
            A CreditCardValidator instance with Luhn check and length bounds.
        """
        generic_validator = CodeValidator(regex=r"^(\d+)$", min_length=min_len, max_length=max_len, length=None, checkdigit=cls.LUHN_VALIDATOR)
        return CreditCardValidator(credit_card_validators=[generic_validator])
    
    def create_range_validator(self, ranges: list[CreditCardRange], check_digit) -> CodeValidator:
        """Creates a custom validator that uses a numeric pattern and checks if the
        prefix and length match any of the provided ranges.
        
        Args:
            ranges: A list of CreditCardRange objects specifying IIN and length rules.
            check_digit: A CheckDigit instance used for final validation.

        Returns:
            A CodeValidator that checks card numbers against all provided ranges.
        """

        class RangeRegexValidator(RegexValidator):
            """Custom regex validator that also validates IIN prefix and card length.

            This validator subclasses `RegexValidator` and extends it to support
            additional credit card range checks, including prefix (IIN) range matching
            and length validation using `CreditCardRange`.

            It is used within `CreditCardValidator.create_range_validator()` to build
            flexible, range-aware validators.

            Methods:
                is_valid: Returns True if the value passes both regex and range checks.
                match: Returns a list containing the value if valid, else None.
                validate: Performs full validation against regex and defined ranges.
            """
            def is_valid(self, value: str) -> bool:
                """Checks if the input passes regex and range-based validation.

                Args:
                    value: The credit card number to validate.

                Returns:
                    True if the input matches regex and satisfies at least one
                    prefix/length range.
                """
                return self.validate(value) is not None

            def match(self, value: str):
                """Attempts to match the input value and wrap it in a list if valid.

                Args:
                    value: The credit card number to check.

                Returns:
                    A list containing the value if matched and valid, otherwise None.
                """
                result = self.validate(value)
                return [result] if result else None

            def validate(self, value: str):
                """Validates the input using regex and configured credit card ranges.

                The method checks:
                - If the value matches the regex pattern.
                - If the value length is within the allowed range.
                - If the value starts with a prefix within the low-high IIN range.

                Args:
                    value: The credit card number to validate.

                Returns:
                    The validated value if successful, otherwise None.
                """
                if super().match(value) is None:
                    # super().match(value) returns [] because no groups are captured
                    # if regex pattern no () → no groups → .groups() is empty
                    print(f"[REJECT] Regex mismatch: {value} (using patterns {[p.pattern for p in self.patterns]})")
                    return None
                

                for range in ranges:
                    print(f"\n[CHECKING RANGE] low={range.low}, high={range.high}, value={value}")

                    if not CreditCardValidator.valid_length(len(value), range):
                        print(f"[SKIP] Length {len(value)} not in {range.lengths or (range.min_len, range.max_len)}")
                        continue

                    if range.high is None:
                        if value.startswith(range.low):
                            print(f"[MATCH] value starts with {range.low}")
                            return value
                    else:
                        print(f"  Comparing: {range.low} <= {value} ? {range.low <= value}")
                        prefix_high = value[:len(range.high)]
                        prefix_low= value[:len(range.low)]

                        if range.low <= prefix_low and prefix_high <= range.high:
                            print(f"[MATCH] Range match successful")
                            return value

                print(f"[FAIL] No range matched for {value}")
                return None



        return CodeValidator(regex_validator=RangeRegexValidator(r"\d+$"), checkdigit=check_digit)
    
