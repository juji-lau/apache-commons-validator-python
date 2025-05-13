""" 
Module Name: isbn10_checkdigit.py
Description: Translates apache.commons.validator.routines.checkdigit.ISBN10CheckDigit.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/checkdigit/ISBN10CheckDigit.java 
Parapphrased from apache.commons.validator.routines.checkdigit.ISBN10CheckDigit.java:
    Modulus 11 ISBN-10 Check Digit calculation/validation.
    ISBN-10 Numbers are a numeric code except for the last (check) digit which can have a value of "X".

    Check digit calculation is based on modulus 11 with digits being weighted based by their position, 
    from right to left  with the first digit being weighted 1, the second 2 and so on. 
    If the check digit is calculated as "10" it is converted to "X".

    **NOTE:**
    From 1st January 2007 the book industry will start to use a new 13 digit ISBN number 
    (rather than this 10 digit ISBN number) which uses the EAN-13 / UPC standard (see EAN13CheckDigit).
    
    For further information see:
        - `Wikipedia - ISBN <https://en.wikipedia.org/wiki/ISBN>`
        - `ISBN-13 Transition Details <http://www.isbn.org/standards/home/isbn/transition.asp>
         
Author: Juji Lau
License (Taken from apache.commons.validator.routines.checkdigit.ISBN10CheckDigit.java):
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
from __future__ import annotations
from typing import Union
from src.apache_commons_validator_python.routines.checkdigit.checkdigit_exception import CheckDigitException
from src.apache_commons_validator_python.routines.checkdigit.modulus_checkdigit import ModulusCheckDigit

class ISBN10CheckDigit(ModulusCheckDigit):
    """This class perfroms Modulus 11 ISBN-10 Check Digit calculation/validation.
    ISBN-10 Numbers are a numeric code except for the last (check) digit which can have
    a value of "X".

    Check digit calculation is based on modulus 11 with digits being weighted based by their position,
    from right to left  with the first digit being weighted 1, the second 2 and so on.
    If the check digit is calculated as "10" it is converted to "X".

    Attributes:
        serializable (bool): Inherited from ModulusCheckDigit (True)
        clone (bool):  Inherited from ModulusCheckDigit (False)
        ISBN10_CHECK_DIGIT (ISBN10CheckDigit): Singleton instance of this class.
    """
    # ISBN10_CHECK_DIGIT should be public, but to make implementing singletons easier, I've made it private.
    __ISBN10_CHECK_DIGIT:ISBN10CheckDigit = None

    def __init__(self):
        """Constructs a modulus 11 Check Digit routine for ISBN-10."""
        super().__init__(modulus = ModulusCheckDigit.MODULUS_11)
    
    @classmethod
    @property
    def ISBN10_CHECK_DIGIT(cls):
        """Enforces singleton behavior and returns the singleton instance of this
        validator.

        Returns:
            A singleton instance of the validator.
        """
        if cls.__ISBN10_CHECK_DIGIT is None:
            cls.__ISBN10_CHECK_DIGIT = ISBN10CheckDigit()
        return cls.__ISBN10_CHECK_DIGIT
    
    def _to_check_digit(self, char_value: int) -> Union[str, CheckDigitException]:
        """Convert an integer value to a character at a specified position. If the value
        is 10 for the check digit (position 1), it is converted to 'X'.

        Args:
            char_value (int): The integer value of the character.

        Returns:
            The converted character ('X' if the value is 10).

        Raises:
            CheckDigitException if an error occurs.
        """
        if char_value == 10:
            return "X"   
        return super()._to_check_digit(char_value)
    
    def _to_int(self, character:str, left_pos:int, right_pos:int) -> Union[str, CheckDigitException]:
        """Convert a character at a specified position to an integer value. If the
        character is 'X' at the check digit position (position 1), it is converted to
        10.

        Args:
            character (str): The character to convert. (Should be a string of length 1 as Python does not support Char).
            left_pos (int): The position of the character in the code, counting from left to right (for identifiying the position in the string).
            right_pos (int): The position of the character in the code, counting from right to left (not used here).

        Returns:
            The integer value of the character.

        Raises:
            CheckDigitException if an error occurs.
        """ 
        if right_pos == 1 and character == "X":
            return 10
        return super()._to_int(character, left_pos, right_pos)

    def _weighted_value(self, char_value:int, left_pos:int, right_pos:int) -> int:
        """Calculates the weighted value of a character in the code at a specified
        position.

        For ISBN-10 (from right to left) digits are weighted by their position.

        Args:
            char_value (int): The numeric value of the character.
            left_pos (int): The position of the character in the code, counting from left to right.
            right_pos (int): The position of the character in the code, counting from right to left.

        Returns:
            The weighted value of the character.
        """
        return char_value * right_pos