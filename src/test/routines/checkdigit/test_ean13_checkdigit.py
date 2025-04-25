""" 
Module Name: test_ean13_checkdigit.py
Description:
    This file tests the implementation of EAN13CheckDigit using ModulusCheckDigit.  
    This file contains:
        Test cases from: 
            test.java.org.apache.commons.validator.routines.checkdigit.EAN13CheckDigitTest.java
            (https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/checkdigit/EAN13CheckDigitTest.java)
        Additional test cases
Author: Juji Lau
License (Taken from apache.commons.validator.routines.checkdigit.EAN13CheckDigitTest.java):
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

from src.main.routines.checkdigit.ean13_checkdigit import EAN13CheckDigit
from src.test.routines.checkdigit.test_abstract_checkdigit import AbstractCheckDigitTest


class TestEAN13CheckDigit(AbstractCheckDigitTest):
    """EAN-13 Check Digit Test."""
    def setup_method(self):
        """ Sets up routine & valid codes."""
        self._routine = EAN13CheckDigit.EAN13_CHECK_DIGIT
        self._valid = ["9780072129519", "9780764558313", "4025515373438", "0095673400332"]