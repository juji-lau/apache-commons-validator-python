""" 
Module Name: luhn_checkdigit.py
Description: Translates apache.commons.validator.routines.checkdigit.LuhnCheckDigit.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/checkdigit/LuhnCheckDigit.java

Author: Alicia Chu
License (Taken from apache.commons.validator.routines.checkdigit.LuhnCheckDigit.java):
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
"""
# from ..routines.checkdigit.checkdigit import CheckDigit
# from ..routines.checkdigit.modulus_checkdigit import ModulusCheckDigit
# from ..routines.checkdigit.checkdigit_exception import CheckDigitException
from .checkdigit import CheckDigit
from .modulus_checkdigit import ModulusCheckDigit
from .checkdigit_exception import CheckDigitException

class LuhnCheckDigit(ModulusCheckDigit):
    """
    This class is used to validate check digits using the Luhn (modulus 10) algorithm,
    which is commonly applied to credit card numbers and other identification numbers.

    The Luhn algorithm weights digits from right to left, doubling every
    second digit and subtracting 9 if the result exceeds 9. This helps detect
    common data entry errors such as transpositions and single-digit mistakes.

    Attributes:
        LUHN_CHECK_DIGIT (LuhnCheckDigit): Singleton instance of this class.
    """
    # Singleton Luhn Check Digit instance
    LUHN_CHECK_DIGIT = None

    def __init__(self):
        """Constructs a ModulusCheckDigit instance with modulus 10 for Luhn
        calculation."""
        super().__init__(modulus=self.MODULUS_10)

    def _weighted_value(self, char_value: int, left_pos: int, right_pos: int) -> int:
        """Calculates the weighted value of a digit based on the Luhn algorithm.

        Args:
            char_value (int): Numeric value of the character.
            left_pos (int): Position from left (not used).
            right_pos (int): Position from right (used to determine weight).

        Returns:
            int: Weighted value with Luhn logic applied.
        """

        # Weighting given to digits depending on their right position
        # Weight 2 to digits in even positions (from the right),
        # Weight 1 to digits in odd positions.
        weight = 2 if (right_pos % 2 == 0) else 1
        weighted = char_value * weight
        return weighted - 9 if weighted > 9 else weighted

# Initialize singleton instance
LuhnCheckDigit.LUHN_CHECK_DIGIT = LuhnCheckDigit()