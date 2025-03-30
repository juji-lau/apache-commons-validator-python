""" 
Module Name: test_isbn10_checkdigit.py
Description:
    This file tests the implementation of ISBN10CheckDigit using ModulusCheckDigit.  
    This file contains:
        Test cases from: 
            test.java.org.apache.commons.validator.routines.checkdigit.ISBN10CheckDigitTest.java
            (https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/checkdigit/ISBN10CheckDigitTest.java)
        Additional test cases
Author: Juji Lau
License (Taken from apache.commons.validator.routines.checkdigit.ISBN10CheckDigitTest.java):
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
"""

from src.main.routines.checkdigit.isbn10_checkdigit import ISBN10CheckDigit
from src.test.routines.checkdigit.test_abstract_checkdigit import AbstractCheckDigitTest


class TestISBN10CheckDigit(AbstractCheckDigitTest):
    """ISBN-10 Check Digit Test."""
    def setup_method(self):
        self._routine = ISBN10CheckDigit.ISBN10_CHECK_DIGIT
        self._valid = ["1930110995", "020163385X", "1932394354", "1590596277"]