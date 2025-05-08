
""" 
Module Name: modulus_checkdigit.py
Description: Translates apache.commons.validator.routines.checkdigit.ModulusCheckDigit.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/checkdigit/ModulusCheckDigit.java
Parapphrased from apache.commons.validator.routines.checkdigit.ModulusCheckDigit.java:
    Abstract Modulus Check digit calculation/validation:
        Provides a base class for building Modulus Check Digit routines.
        This implementation only handles single-digit numeric codes, such as EAN-13. 
        For alphanumeric codes such as EAN-128 you will need to implement/override the `toInt()` and `toChar()` methods.
         
Author: Juji Lau
License (Taken from apache.commons.validator.routines.checkdigit.ModulusCheckDigit.java):
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
    In ModulusCheckDigit._to_int() for the argument, `final char character`:
        - I accept a Python str of len(1) in the place of Java's char.
        - Python does not support single characters
        - I raise a ValueError exception via CheckDigitException if the input is not a string of length 1.

"""
# from modulus_checkdigit import ModulusCheckDigit
from abc import abstractmethod
from typing import Optional, Union, Final
from src.main.routines.checkdigit.abstract_checkdigit import AbstractCheckDigit
from src.main.routines.checkdigit.checkdigit_exception import CheckDigitException
# from src.main.generic_validator import GenericValidator

class ModulusCheckDigit(AbstractCheckDigit):
    """
    Abstract base class for Modulus Check Digit calculation and validation.

    This class provides a foundation for implementing modulus-based check digit routines.
    It supports single-digit numeric codes like EAN-13. For alphanumeric codes (e.g., EAN-128)
    override the `_to_int()` and `_to_char()` methods.

    Attributes:
        MODULUS_10 (int):
        MODULUS_11 (int): 
        modulus (int): 
        serializable (bool): Indicates if the object is serializable.
        clone (bool): Indicates if the object can be cloned.
    """
    
    # Constants:
    MODULUS_10:Final[int] = 10
    MODULUS_11:Final[int] = 11
    
    # Attributes to manage serialization and cloning capabilities
    serializable = True    # class is serializable
    clone = False          # class is not cloneable

    def __init__(self, *, modulus:int = MODULUS_10):
        """
        Constructs a CheckDigit routine for a specified modulus.
        
        Args:
            modulus (int): The modulus value to use for the check digit calculation.
        """
        super().__init__()
        self.__modulus:Final[int] = modulus

    @property
    def modulus(self) -> int:
        """ Gets the modulus value this check digit routine is based on."""
        return self.__modulus
    
    # # The modulus can be greater than 10 provided that the implementing class overrides toCheckDigit and toInt (for example as in ISBN10CheckDigit).
    # @modulus.setter
    # def modulus(self):
    #     self.__modulus__ = 10
    
    # concrete method
    @staticmethod #so do not pass self when calling self.sum_digits in test_isin_checkdigit
    def sum_digits(number:int) -> int:
        """
        Add together the individual digits in a number.

        Args: 
            number (int): The number whose digits are to be added

        Returns: 
            The sum of the digits.
        """
        total = 0
        todo = number
        while (todo > 0):
            total += todo %10           # Add the digit from number
            todo //=10                  # Update todo to be 1 less digit
        return total

    # concrete method (automatically overrides parent)
    def calculate(self, code:str) -> Union[str, CheckDigitException, None]:
        """
        Calculate a modulus heck Digit for a code which does not yet have one.

        Args:
            code (str): The code for which to calculate the Check Digit; the check digit should not be included
        
        Returns: 
            The calculated Check Digit
        
        Raises: 
            CheckDigitException if an error occurs calculating the check digit.
        """
        # TODO: uncomment when you have access to this class
        # if GenericValidator.is_blank_or_null(code):
        #     raise CheckDigitException("Code is missing", ValueError())
        if code is None or code == "":
            raise CheckDigitException("Code is missing", ValueError())
        # TODO: end
        if code is None or code == "":
            return False
        # TODO: end
        modulus_result = self._calculate_modulus(code, False)
        char_value = (self.modulus - modulus_result) % self.modulus
        return self._to_check_digit(char_value)

    def _calculate_modulus(self, code:str, includes_check_digit:bool) -> Union[int, CheckDigitException, None]:
        """
        Calculate the modulus for a code.

        Args:
            code (str): The code to calculate the modulus for.
            includes_check_digit (str): Whether the code includes the Check Digit or not.

        Returns:
            The modulus value

        Raises:
            CheckDigitException if an error occurs calculating the modulus for the specified code.
        """
        total = 0
        for i in range(0, len(code)):
            lth = len(code) + int(not includes_check_digit)
            left_pos = i + 1
            right_pos = lth - i
            char_value = self._to_int(code[i], left_pos, right_pos)
            total += self._weighted_value(char_value, left_pos, right_pos)

        if total == 0:
            raise CheckDigitException("Invalid code, sum is zero", ValueError)
        
        return total % self.modulus

    def is_valid(self, code:str) -> bool:
        """
        Validate a modulus check digit for a code.

        Args:
            code (str): The code to validate.
        
        Returns:
            True if the check digit is valid.
            False otherwise.
        """
        # TODO: Uncomment once we recieve GenericValidator
        # if GenericValidator.is_blank_or_null(code):
        #     return False
        if code is None or code == "":
            return False
        # TODO: end
        try:
            modulus_result = self._calculate_modulus(code, True)
            return (modulus_result == 0)
        except CheckDigitException as e:
            return False

    
    def _to_check_digit(self, char_value:int) -> Union[str, CheckDigitException, None]:
        """
        Convert an integer value to a check digit.
        Note: 
            This implementation only handles single-digit numeric values. 
            For non-numeric characters, override this method to provide integer --> character conversion.
        
        Args:
            char_value (int): The integer value of the character.
        
        Returns:
            The converted character.
        
        Raises:
            CheckDigitException if integer charcter value doesn't represent a numeric character.
        """
        if char_value >= 0 and char_value <= 9:
            return str(char_value)
        
        raise CheckDigitException(f"Invalid Check Digit Value = {char_value}", ValueError())
        
    def _to_int(self, character:str, left_pos:int, right_pos:int) -> Union[int, CheckDigitException, None]:
        """
        Convert a character at a specified position to an integer value.
        Note:
            - This implementation only handles numeric values. 
            - For non-numeric characters, override this method to provide character --> integer conversion.

        Args:
            character (str): The character to convert. (Should be a string of length 1 as Python does not support Char).
            left_pos (int): The position of the character in the code, counting from left to right (for identifiying the position in the string).
            right_pos (int): The position of the character in the code, counting from right to left (not used here).
        
        Returns:
            The integer value of the character.
        
        Raises:
            CheckDigitException if charcter is non-numeric, or not a string of length 1.
        """
        if len(character) != 1:
            raise CheckDigitException("Character must be a string of length 1.", ValueError())
        
        if character[0].isdigit():
            return int(character[0])
        
        raise CheckDigitException(f"Invalid character[{left_pos}] = '{character}'.", ValueError())

    @abstractmethod
    def _weighted_value(self, char_value:int, left_pos:int, right_pos:int) -> Union[int, CheckDigitException, None]:
        """
        Calculates the weighted value of a character in the code at a specified position.

        Some modulus routines weight the value of a character depending on its position in the code (for example, ISBN-10), 
        while others use different weighting factors for odd/even positions (for example, EAN or Luhn). 
        Implement the appropriate mechanism required by overriding this method.
       
        Args:
            char_value (int): The numeric value of the character.
            left_pos (int): The position of the character in the code, counting from left to right.
            right_pos (int): The position of the character in the code, counting from right to left.
        
        Returns:
            The weighted value of the character.

        Raises:
            CheckDigitException if an error occurs calculating the weighted value.
        """
        pass
