""" 
Module Name: code_validator.py
Description: Translates apache.commons.validator.routines.CodeValidator.java
  Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/CodeValidator.java
  Paraphrased from apache.commons.validator.routines.CodeValidator:
    
    This class provides generic Code Validation, providing format, minimum/maximum length, 
    and check digit validations.

    This class performs the following validations on a code:
      - If the code is ``None``, return ``None``/``False`` as appropriate.
      - Trim the input. If the resulting code is empty, return ``None``/``False`` as appropriate.
      - Check the *format* of the code using a *regular expression* (if specified).
      - Check the *minimum* and *maximum* length (if specified) of the *parsed* code 
        (that is, parsed by the *regular expression*).
      - Perform :class:`CheckDigit` validation on the parsed code (if specified).
      - The :meth:`validate` method returns the trimmed, parsed input (or ``None`` if validation failed).
   
    **Note:**  
    The :meth:`is_valid` method will return ``True`` if the input passes validation.
    Since this includes trimming as well as potentially dropping parts of the input, 
    it is possible for a string to pass validation but fail the check digit test 
    if passed directly to it. Check digit routines generally don't trim input 
    nor do they check the format/length.

    To ensure valid input is passed to a method, use :meth:`validate` as follows:

    .. code-block:: python

        valid = validator.validate(input)
        if valid is not None:
            some_method(valid)

    The validator should be configured with the appropriate regular expression, 
    minimum/maximum length, and check digit validator before calling one of the two 
    validation methods:

    - :meth:`is_valid`
    - :meth:`validate`

    Codes often include *format* characters—such as hyphens—to improve human readability.  
    These can be removed prior to length and check digit validation by specifying them as 
    a *non-capturing* group in the regular expression (i.e., using the ``(?:   )`` notation).

    Alternatively, avoid using parentheses except for the parts you want to capture.

    :since: 1.4
 
Author: Juji Lau
License (Taken from apache.commons.validator.routines.ISBNValidator):
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
  - Removed getInstance() which supports singletone behavior for a Java class.  In here, singleton behavior is implicit.
  - Added a setter for self.convert.  getInstance(convert) provided a way to do this, but now that it's removed, this adds a new way.
"""
import logging
from typing import Optional, Final
# from generic_validator import GenericValidator
from ..routines.regex_validator import RegexValidator
from ..routines.checkdigit.checkdigit import CheckDigit


class CodeValidator:
    """This class performs generic code validation, including format checks using
    regular expressions, minimum/maximum length validation, and check digit validation.

    It ensures that:
      - If the input code is `None`, returns `None`.
      - It trims the input code and checks if the result is non-empty.
      - It validates the code format using a regular expression (if specified).
      - It checks the minimum and maximum length of the code (if specified).
      - It optionally performs check digit validation.

    Attributes:
        regex_validator (RegexValidator): The regular expression validator for the code format.
        checkdigit (CheckDigit): The check digit validation routine.
        min_length (int): The minimum length of the code.
        max_length (int): The maximum length of the code.
        serializable (bool): Indicates if the object is serializable (class attribute).
        cloneable (bool): Indicates if the object can be cloned (class attribute).
    """
    
    # Attributes to manage serialization and cloning capabilities
    serializable = True    # class is serializable
    cloneable = False      # class is not cloneable

    def __init__(self, *, regex:str = None, regex_validator:RegexValidator=None, length:int=None, min_length:int = -1, max_length:int = -1, checkdigit:CheckDigit=None):
        """Initializes the CodeValidator with default values.

        Args:
            regex (str, optional): The regular expression for validating the code format.
            regex_validator (RegexValidator, optional): An existing RegexValidator object.
            length (int, optional): The length of the code (default -1). Sets the attribute min_length and max_length to the same value
            min_length (int, optional): The minimum length of the code (defaults to -1 for no restriction).
            max_length (int, optional): The maximum length of the code (defaults to -1 for no restriction).
            check_digit (CheckDigit): The check digit validation routine.
        """
        if regex is None and regex_validator is None:
            self.__regex_validator:Final[Optional[RegexValidator]] = None
        elif regex_validator is not None:
            self.__regex_validator = regex_validator
        else:
            self.__regex_validator = RegexValidator(regex)

        if length is None:
            self.__min_length:Final[int] = min_length
            self.__max_length:Final[int] = max_length
        else:
            self.__min_length = length
            self.__max_length = length

        self.__checkdigit:Final[CheckDigit] = checkdigit

    @property
    def checkdigit(self) -> CheckDigit:
        """Returns the checkdigit attribute."""
        return self.__checkdigit
    
    @property
    def max_length(self) -> int:
        """Returns the max_length attribute."""
        return self.__max_length

    @property
    def min_length(self) -> int:
        """Returns the min_length attribute."""
        return self.__min_length

    @property
    def regex_validator(self) -> Optional[RegexValidator]:
        """Returns the regex_validator attribute."""
        return self.__regex_validator  

    def is_valid(self, input:str) -> bool:
        """Validates the input by calling validate().  returning either True or False.

        Args:
            input (str): The code to validate and check for validity.
        Returns:
            `False` if the return value of validate() is None.
            `True` otherwise.
        """
        return self.validate(input) != None
    

    def validate(self, input:str) -> Optional[str]:
        """
        Validate the input returning either the valid input or None if the input is invalid
        Note: This method trims the input and if `self.regex_validator` is set, it may also 
            change the input as part of the validation.

        Args: 
            input (str): The code to validate.
        
        Returns: 
            The validated input if the code is valid
            `None` if the code is invalid
        """
        if input is None:
            return None

        # Check if the code is empty
        code = input.strip()
        if code is None:
            return None
        
        # Validate/reformat using regular expression
        if self.regex_validator is not None:
            code = self.regex_validator.validate(code)
            if code is None:
                return None

        # Check length
        if ((self.min_length >= 0 and len(code) < self.min_length) or
            (self.max_length >= 0 and len(code) > self.max_length)):
            return None

        # Validate the check digit
        if ((self.checkdigit is not None) and (not self.checkdigit.is_valid(code))):
            return None

        return code