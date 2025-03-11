"""
Module Name: isbn_validator.py
Description:
    Translates apache.commons.validator.routines.ISBNValidator.java
    This module provides a class `ISBNValidator` for validating ISBN-10 and ISBN-13 codes.
    It also supports converting ISBN-10 codes to ISBN-13 if the `convert` attribute is set to `True`.
    The class uses regular expressions to validate the formats and check digits for ISBN-10 and ISBN-13 codes.
    It also allows ISBN-10 codes to be converted to ISBN-13 using specific conversion logic.

Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/ISBNValidator.java

Author: Juji Lau

License:
    Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements.
    See the NOTICE file distributed with this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software distributed under the License is
    distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and limitations under the License.

Changes:
    - Removed `getInstance()` method, which supports singleton behavior in the Java version. Singleton behavior is implicit in this Python version.
    - Added a setter for the `convert` property. In the original Java version, `getInstance(convert)` provided a way to configure this, but it has been replaced with a direct attribute.

"""

import CodeValidator
from checkdigit import CheckDigitException, EAN13CheckDigit, ISBN10CheckDigit


class ISBNValidator:
    """
    A validator class for ISBN-10 and ISBN-13 codes.

    This class validates whether a code is a valid ISBN-10 or ISBN-13 and provides the ability
    to convert ISBN-10 codes to ISBN-13 if the `convert` property is set to `True`.

    Attributes:
        convert (bool): If True, all ISBN-10 codes will be converted to ISBN-13.
        isbn10_validator (CodeValidator): Validator instance for ISBN-10 codes.
        isbn13_validator (CodeValidator): Validator instance for ISBN-13 codes.
        serializable (bool): Indicates if the object is serializable.
        cloneable (bool): Indicates if the object can be cloned.

    Constants:
        ISBN_10_LEN (int): The length of an ISBN-10 code.
        SEP (str): The separator used in ISBN code formats (either hyphens or spaces).
        GROUP (str): Regular expression pattern for the group portion of the ISBN code.
        PUBLISHER (str): Regular expression pattern for the publisher portion of the ISBN code.
        TITLE (str): Regular expression pattern for the title portion of the ISBN code.
        ISBN10_REGEX (str): Regular expression pattern for ISBN-10 validation.
        ISBN13_REGEX (str): Regular expression pattern for ISBN-13 validation.
    """
    # Constants
    # self._serialVersionUID = 4319515687976420405L
    ISBN_10_LEN = 10
    SEP = "(?:\\-|\\s)"
    GROUP = "(\\d{1,5})"
    PUBLISHER = "(\\d{1,7})"
    TITLE = "(\\d{1,6})"
    
    # ISBN-10 consists of 4 groups of numbers separated by either dashes (-) or spaces.  
    # The first group is 1-5 characters, second 1-7, third 1-6, and fourth is 1 digit or an X.
    ISBN10_REGEX = "^(?:(\\d{9}[0-9X])|(?:" + GROUP + SEP + PUBLISHER + SEP + TITLE + SEP + "([0-9X])))$"
    
    # ISBN-13 consists of 5 groups of numbers separated by either dashes (-) or spaces.  
    # The first group is 978 or 979, the second group is 1-5 characters, third 1-7, fourth 1-6, and fifth is 1 digit.
    ISBN13_REGEX = "^(978|979)(?:(\\d{10})|(?:" + SEP + GROUP + SEP + PUBLISHER + SEP + TITLE + SEP + "([0-9])))$"


    def __init__(self, convert:bool = True):
        """
        Initializes the ISBNValidator with default values.
        Initializes two validators, one for ISBN-10 and one for ISBN-13, using the appropriate
        regular expressions and check digits.
        Python's version of: org.apache.validator.routines.ISBNValidator()
        
        Args:
            convert (bool): If True, enables the conversion of ISBN-10 codes to ISBN-13.

        """
        self._convert = convert       # Read only after instantiation 
        self._isbn10_validator = CodeValidator(self.ISBN10_REGEX, 10, ISBN10CheckDigit.ISBN10_CHECK_DIGIT)
        self._isbn13_validator = CodeValidator(self.ISBN13_REGEX, 13, EAN13CheckDigit.EAN13_CHECK_DIGIT)
        
        # Attributes to manage serialization and cloning capabilities
        self.serializable = True    # class is serializable
        self.clone = False          # class is not cloneable

    # TODO: How to do inheritied objects:
      # clone, equals, finalize, getClass, hashCode, notify, notifyAll, wait, wait
    
    @property
    def convert(self):
        """Returns the convert attribute."""
        return self._convert
    
    @convert.setter
    def convert(self, convert: bool) -> None:
        """ Sets the convert attribute."""
        self._convert = convert
      
    def convert_to_isbn13(self, isbn10:str) -> str:
        """
        Convert an ISBN-10 code to an ISBN-13 code.
        Python's version of: org.apache.validator.routines.ISBNValidator.convertToISBN13()
        
        Parameters:
          isbn10: The ISBN-10 code to convert. Must be a valid ISBN-10 with NO formatting characters.

        Returns:
          isbn13: A converted ISBN-13 code, or None if the ISBN-10 code is not valid.
        """
        # check for validity
        if isbn10 is None:
          return None

        # Remove leading and trailing spaces
        isbn10 = isbn10.strip()
        if len(isbn10) != self.ISBN_10_LEN:
          raise ValueError(f"Invalid length for {len(isbn10)} for '{isbn10}'")
        
        # Calculate the new ISBN-13 code (drop the original checkdigit)
        isbn13 = "978" + isbn10[:-1]
        try:
          checkDigit = self.isbn13_validator.getCheckDigit().calculate(isbn13)
          isbn13 += checkDigit
          return isbn13
        except CheckDigitException as e:
          raise ValueError(f"Check digit error for '{input}' - {e}")

    # TODO: Circular dependency
    def is_valid(self, code:str) -> bool:
        """
        Checks if code is either a valid ISBN-10 or ISBN-13 code.
        ython's version of: org.apache.validator.routines.ISBNValidator.isValid()
        
        Parameter(s):
          code: The code to check.

        Returns:
          True if the code is a valid ISBN-10 or ISBN-13 code, otherwise false.
        """
        return self.is_valid_isbn10(code) or self.is_valid_isbn13(code)


    def is_valid_isbn10(self, code:str) -> bool:
        """
        Checks if code is a valid ISBN-10 code.
        Python's version of: org.apache.validator.routines.ISBNValidator.isValidISBN10()
        
        Parameters:
          code: The ISBN-10 code to check.

        Returns:
          True if the code is a valid ISBN-10 code, otherwise false.
        """
        return self._isbn10_validator.is_valid(code)
    
    def is_valid_isbn13(self, code:str) -> bool:
        """
        Checks if code is a valid ISBN-13 code.
        Python's version of: org.apache.validator.routines.ISBNValidator.isValidISBN13()
        
        Parameters:
          code: The ISBN-13 code to check.

        Returns:
          True if the code is a valid ISBN-13 code, otherwise false.
        """
        return self._isbn13_validator.is_valid(code)

    def validate(self, code:str) -> str:
        """
        Checks if code is either a valid ISBN-10 or ISBN-13 code.
        If valid, this method returns the ISBN code with formatting characters removed (i.e. space or hyphen).
        Converts an ISBN-10 codes to ISBN-13 if convertToISBN13 is true.
        Python's version of: org.apache.validator.routines.ISBNValidator.validate()
        
        Parameters:
          code: The code to validate.

        Returns:
          A valid ISBN code if valid, otherwise None.
        """
        result = self.validate_isbn13(code)
        if result is None:
          result = self.validate_isbn10(code)  
          if result != None and self.convert == True:
            result = self.convert_to_isbn13(result)
        return result

    def validate_isbn10(self, code:str) -> str:
        """
        Checks if code is a valid ISBN-10 code.
        If valid, this method returns the ISBN-10 code with formatting characters removed (i.e. space or hyphen).
        Python's version of: org.apache.validator.routines.ISBNValidator.validateISBN10()
        
        Parameters:
          code: The code to validate.

        Returns:
          A valid ISBN-10 code if valid, otherwise None.
        """
        result = self._isbn10_validator.validate(code)
        if result is not None:
          return str(result)     
        return None

    def validate_isbn13(self, code:str) -> str:
        """
        Checks if code is a valid ISBN-13 code.
        If valid, this method returns the ISBN-13 code with formatting characters removed (i.e. space or hyphen).
        Python's version of: org.apache.validator.routines.ISBNValidator.validateISBN13()
        
        Parameters:
          code: The code to validate.

        Returns:
          A valid ISBN-13 code if valid, otherwise None.
        """
        # check for validity
        if self.is_valid_isbn13(code):
          result = self._isbn13_validator.validate(code)
          if result is not None:
            return str(result)
        return None