""" 
Module Name: isin_checkdigit.py
Description: Translates apache.commons.validator.routines.checkdigit.ISINCheckDigit.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/checkdigit/ISINCheckDigit.java 
         
Author: Alicia Chu
License (Taken from apache.commons.validator.routines.checkdigit.ISINCheckDigit.java):
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
- StringBuilder -> list of strings
"""
from typing import Final
from src.apache_commons_validator_python.routines.checkdigit.modulus_checkdigit import ModulusCheckDigit, CheckDigitException

class ISINCheckDigit(ModulusCheckDigit):
    """Modulus 10 ISIN (International Securities Identifying Number) Check Digit
    calculation and validation.

    ISINs are 12-character alphanumeric identifiers used for securities.
    This validator uses the Modulus 10 Double Add Double method:
    - Every second digit is weighted by 2, starting from the right.
    - Alphabetic characters are converted to values: A=10, B=11, ..., Z=35.
    - Weighted digits over 9 are split and summed (e.g., 18 -> 1 + 8 = 9).
    """

    _MAX_ALPHANUMERIC_VALUE: Final[int] = 35
    _POSITION_WEIGHT: Final[list[int]] = [2, 1]
    _ISIN_CHECK_DIGIT: Final["ISINCheckDigit"] = None  # Set after class definition

    def __init__(self) -> None:
        """Initializes an ISINCheckDigit validator."""
        super().__init__()

    def _calculate_modulus(self, code: str, includes_check_digit: bool) -> int:
        """Calculates the modulus for the given ISIN code after transforming characters
        to digits.

        Args:
            code (str): The code to calculate the modulus for.
            includes_check_digit (bool): Whether the code includes the Check Digit or not.

        Returns:
            int: The computed modulus value.

        Raises:
            CheckDigitException: If the code contains invalid characters or an invalid check digit.
        """

        transformed = []

        #checks if included checkdigit is valid
        if includes_check_digit:
            check_digit = code[-1]
            if not check_digit.isdigit():
                raise CheckDigitException(f"Invalid checkdigit[{check_digit}] in {code}")
            
        for i, char in enumerate(code):
            try:
                char_value = int(char, 36)  # Converts letters A-Z to 10-35
            except ValueError:
                raise CheckDigitException(f"Invalid character[{i}]='{char}' in {code}")
            
            if char_value < 0 or char_value > self._MAX_ALPHANUMERIC_VALUE:
                raise CheckDigitException(f"Invalid Character[{i + 1}] = '{char_value}'")
            transformed.append(str(char_value))

        transformed_code = ''.join(transformed)
        return super()._calculate_modulus(transformed_code, includes_check_digit)
    
    def _weighted_value(self, char_value: int, left_pos: int, right_pos: int) -> int:
        """Calculates the weighted value of a digit for ISIN check digit calculation.

        Even positions (from the right) are weighted by 2, odd by 1.
        Values over 9 are reduced by summing their digits (digital root).

        Args:
            char_value (int): The numeric value of the character.
            left_pos (int): Position from the left (unused).
            right_pos (int): Position from the right (used to select weight).

        Returns:
            int: The weighted sum value of the digit.
        """
        weight: Final[int] = self._POSITION_WEIGHT[right_pos % 2]
        weighted_value: Final[int] = char_value * weight
        return self.sum_digits(weighted_value)

# Singleton instance assignment 
ISINCheckDigit._ISIN_CHECK_DIGIT = ISINCheckDigit()
