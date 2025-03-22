
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
    Removed singleton method
    TODO: add serializeable and cloneable, check singletons

"""
from modulus_checkdigit import ModulusCheckDigit

class EAN13CheckDigit(ModulusCheckDigit):
    """
    Modulus 10 EAN-13 / UPC / ISBN-13 Check Digit calculation and validation.

    This class implements a check digit routine for the EAN-13 format, 
    which is widely used for barcodes. The calculation follows the 
    Modulus 10 algorithm, assigning different weights to digits based 
    on their position.

    Attributes:
        POSITION_WEIGHT (list[int]): Weighting given to digits depending on their right position
    """

    # self._serialVersionUID = 1726347093230424107
    # EAN13_CHECK_DIGIT
    POSITION_WEIGHT = [3, 1]

    def __init__(self):
        """
        Constructs a modulus 10 Check Digit routine for EAN/UPC.
        """
        super().__init__()
    
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
        return char_value * self.POSITION_WEIGHT[right_pos % 2]