
""" 
Module Name: ean13.py
Description: Translates apache.commons.validator.routines.checkdigit.EAN13CheckDigit.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/checkdigit/EAN13CheckDigit.java 
Parapphrased from apache.commons.validator.routines.checkdigit.EAN13CheckDigit.java:
    Modulus 10 EAN-13 UPC ISBN-13 Check Digit calculation/validation.
    Check digit calculation is based on modulus 10 with digits in an odd position (from right to left) being weighted 1 and even position digits being weighted 3.

    For further information see:
        - EAN-13: https://en.wikipedia.org/wiki/European_Article_Number (Wikipedia - European Article Number)
        - UPC: https://en.wikipedia.org/wiki/Universal_Product_Code (Wikipedia - Universal Product Code)
        - ISBN-13: https://en.wikipedia.org/wiki/ISBN (Wikipedia - International Standard Book Number (ISBN))
         
Author: Juji Lau
License (Taken from apache.commons.validator.routines.checkdigit.EAN13CheckDigit.java):
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
from typing  import Final
from src.main.routines.checkdigit.modulus_checkdigit import ModulusCheckDigit


class EAN13CheckDigit(ModulusCheckDigit):
    """
    Modulus 10 EAN-13 / UPC / ISBN-13 Check Digit calculation and validation.

    This class implements a check digit routine for the EAN-13 format, 
    which is widely used for barcodes. The calculation follows the 
    Modulus 10 algorithm, assigning different weights to digits based 
    on their position.

    Attributes:
        serializable (bool): Inherited from ModulusCheckDigit (True)
        clone (bool):  Inherited from ModulusCheckDigit (False)
    
    Constants:
        EAN13_CHECK_DIGIT (EAN13CheckDigit): Singleton instance of this class.
        POSITION_WEIGHT (list[int]): Weighting given to digits depending on their right position
    """
    # EAN13_CHECK_DIGIT should be public, but to make implementing singletons easier, I've made it private.
    __EAN13_CHECK_DIGIT:EAN13CheckDigit = None
    __POSITION_WEIGHT:Final[list] = [3, 1]

    def __init__(self):
        """Constructs a Check Digit routine for EAN-13."""
        super().__init__()

    @classmethod
    @property
    def EAN13_CHECK_DIGIT(cls):
        """
        Enforces singleton behavior and returns the singleton instance of this validator.

        Returns:
            A singleton instance of the validator.
        """
        if cls.__EAN13_CHECK_DIGIT is None:
            cls.__EAN13_CHECK_DIGIT = EAN13CheckDigit()
        return cls.__EAN13_CHECK_DIGIT
    
    def _weighted_value(self, char_value:int, left_pos:int, right_pos:int) -> int:
        """
        Calculates the weighted value of a character in the code at a specified position.

        For EAN-13 (from right to left), odd digits are weighted with a factor of one.
        For EAN-13 (from right to left), even digits are weighted with a factor of three.
        
        Args:
            char_value (int): The numeric value of the character.
            left_pos (int): The position of the character in the code, counting from left to right.
            right_pos (int): The position of the character in the code, counting from right to left.
        
        Returns:
            The weighted value of the character.
        """
        return char_value * self.__POSITION_WEIGHT[right_pos % 2]