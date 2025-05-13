""" 
Module Name: checkdigit.py
Description: Translates apache.commons.validator.routines.checkdigit.CheckDigit.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/checkdigit/CheckDigit.java
Paraphrased from apache.commons.validator.routines.checkdigit.CheckDigit.java:
      
    Check Digit calculation and validation.
    
    The logic for validating check digits was previously embedded within specific
    code validation, which included format and length verification. The `CheckDigit`
    class separates the check digit calculation logic, making it easier to test and reuse.
    
    Although Commons Validator primarily focuses on validation, `CheckDigit` also defines
    behavior for calculating and generating check digits. This allows users to reuse the same
    logic for both validation and generation. For example, validator.routines.ISBNValidator 
    makes specific use of this feature by providing the facility to validate 
    ISBN-10 codes and then converting them to the new ISBN-13 standard.
    
    `CheckDigit` is used by the generic `CodeValidator` implementation.
    
    Implementations:
        See the package summary for a full list of implementations provided within Commons Validator.

 
Author: Juji Lau
License (Taken from apache.commons.validator.routines.checkdigit.CheckDigit.java):
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
    Added serializeable and clone as abstract attributes

"""

from abc import ABC, abstractmethod
from typing import Union
# from code_validator import CodeValidator  #circular import
from src.apache_commons_validator_python.routines.checkdigit.checkdigit_exception import CheckDigitException

class CheckDigit(ABC):
    """Check Digit calculation and validation.

    The logic for validating check digits was previously embedded within specific
    code validation, which included format and length verification. The `CheckDigit`
    class separates the check digit calculation logic, making it easier to test and reuse.

    Although Commons Validator primarily focuses on validation, `CheckDigit` also defines
    behavior for calculating and generating check digits. This allows users to reuse the same
    logic for both validation and generation. For example, validator.routines.ISBNValidator
    makes specific use of this feature by providing the facility to validate
    ISBN-10 codes and then converting them to the new ISBN-13 standard.

    `CheckDigit` is used by the generic `CodeValidator` implementation.

    Attributes:
        serializable (bool): Indicates if the object is serializable.
        clone (bool): Indicates if the object can be cloned.
    """
    # Forces subclasses to define this attribute
    @property
    @abstractmethod
    def serializable(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def clone(self) -> bool:
        pass

    @abstractmethod
    def calculate(self, code: str) -> Union[str, CheckDigitException, None]:
        """Calculates the Check Digit for a code.

        Args:
            code (str): The code to calculate the Check Digit for.  It must not include the checkdigit

        Returns:
            The calculated Check Digit

        Raises:
            CheckDigitException if an error occurs.
        """
        raise CheckDigitException

    @abstractmethod
    def is_valid(self, code:str) -> bool:
        """Validates the check digit for the code.

        Args:
            code (str): The code to validate, the string must include the check digit.

        Returns:
            True if the check digit is valid; False otherwise
        """
        pass