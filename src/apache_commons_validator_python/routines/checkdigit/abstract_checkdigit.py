""" 
Module Name: checkdigit.py

Description: 
    This module provides the `AbstractCheckDigit` class, translating Apache Commons 
    Validator’s `AbstractCheckDigit.java` into Python. It serves as a base for check 
    digit algorithms, defining the interface for computing and validating check digits.
    Original link at: 
        https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/checkdigit/AbstractCheckDigit.java
 
Author: Juji Lau

License:
    Licensed to the Apache Software Foundation (ASF) under one or more
    contributor license agreements. See the NOTICE file distributed with
    this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0
    (the "License"); you may not use this file except in compliance with
    the License. You may obtain a copy of the License at:

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

# from ..routines.checkdigit.checkdigit import CheckDigit
from .checkdigit import CheckDigit

class AbstractCheckDigit(CheckDigit):
    """
    Abstract base class for check digit algorithms.

    Subclasses must implement methods for calculating and validating check digits
    according to specific standards (e.g., ISBN, EAN-13).
    """    
    pass