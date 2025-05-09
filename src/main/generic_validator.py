"""
Licensed to the Apache Software Foundation (ASF) under one or more
contributor license agreements.  See the NOTICE file distributed with
this work for additional information regarding copyright ownership.
The ASF licenses this file to You under the Apache License, Version 2.0
(the "License"); you may not use this file except in compliance with
the License.  You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

#from src.main.routines.credit_card_validator import CreditCardValidator
#from src.main.routines.date_validator import DateValidator
#from src.main.routines.email_validator import EmailValidator
#from src.main.routines.url_validator import UrlValidator
#from src.main.generic_type_validator import GenericTypeValidator
from typing import Final
import re
import locale


class GenericValidator:
    """
    This class contains basic methods for performing validations. Removed functions for
    double, long, and short for is_in_range (just have one general is_in_range).
    """


    @staticmethod
    def is_blank_or_null(value: str) -> bool:
        """
        Checks if the field isn't null and the length of the field is greater than zero, not including whitespace.
        """
        return value is None or value.strip() == ""


    def __init__(self):
        # Constructor, not needed in Python but keeping it for compatibility
        pass