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
from src.main.routines.CreditCardValidator import CreditCardValidator;
from src.main.routines.DateValidator import DateValidator;
from src.main.routines.EmailValidator import EmailValidator;
from src.main.routines.UrlValidator import UrlValidator;
from GenericTypeValidator import GenericTypeValidator
from typing import Final
import re
import locale

class GenericValidator:
    """
    This class contains basic methods for performing validations. Removed functions for
    double, long, and short because these do not exist in Python (e.g. is_short, etc)
    """

    # Static constants for validators
    URL_VALIDATOR: Final[UrlValidator] = UrlValidator()
    CREDIT_CARD_VALIDATOR: Final[CreditCardValidator] = CreditCardValidator()

    @staticmethod
    def adjust_for_line_ending(value: str, line_end_length: int) -> int:
        n_count = 0
        r_count = 0
        for char in value:
            if char == '\n':
                n_count += 1
            if char == '\r':
                r_count += 1
        rn_count = r_count + n_count
        return n_count * line_end_length - rn_count

    @staticmethod
    def is_blank_or_null(value: str) -> bool:
        """
        Checks if the field isn't null and the length of the field is greater than zero, not including whitespace.
        """
        return value is None or value.strip() == ""

    @staticmethod
    def is_byte(value: str) -> bool:
        """
        Checks if the value can safely be converted to a byte.
        """
        return GenericTypeValidator.format_byte(value) is not None

    @staticmethod
    def is_credit_card(value: str) -> bool:
        """
        Checks if the field is a valid credit card number.
        """
        return GenericValidator.CREDIT_CARD_VALIDATOR.is_valid(value)

    @staticmethod
    def is_date(value: str, locale: locale) -> bool:
        """
        Checks if the field is a valid date.
        """
        return DateValidator.get_instance().is_valid(value, locale)

    @staticmethod
    def is_date_with_pattern(value: str, date_pattern: str, strict: bool) -> bool:
        """
        Checks if the field is a valid date with a specific pattern.
        """
        return DateValidator.get_instance().is_valid(value, date_pattern, strict)

    @staticmethod
    def is_email(value: str) -> bool:
        """
        Checks if a field has a valid e-mail address.
        """
        return EmailValidator.get_instance().is_valid(value)

    @staticmethod
    def is_float(value: str) -> bool:
        """
        Checks if the value can safely be converted to a float.
        """
        return GenericTypeValidator.format_float(value) is not None

    @staticmethod
    def is_in_range(value, min_value, max_value) -> bool:
        """
        Checks if a value is within a range. Instead of writing an is_in_range for 
        byte, double, float, int, long, and short like in the Java version, 
        we just remove the typing for the arguments. 
        """
        return min_value <= value <= max_value

    @staticmethod
    def is_int(value: str) -> bool:
        """
        Checks if the value can safely be converted to an integer.
        """
        return GenericTypeValidator.format_int(value) is not None

    @staticmethod
    def is_url(value: str) -> bool:
        """
        Checks if the field is a valid URL address.
        """
        return GenericValidator.URL_VALIDATOR.is_valid(value)

    @staticmethod
    def match_regexp(value: str, regexp: str) -> bool:
        """
        Checks if the value matches the regular expression.
        """
        if not regexp:
            return False
        return bool(re.match(regexp, value))

    @staticmethod
    def max_length(value: str, max_len: int) -> bool:
        """
        Checks if the value's length is less than or equal to the max.
        """
        return len(value) <= max_len

    @staticmethod
    def max_length_with_line_end(value: str, max_len: int, line_end_length: int) -> bool:
        """
        Checks if the value's adjusted length is less than or equal to the max, accounting for line endings.
        """
        adjust_amount = GenericValidator.adjust_for_line_ending(value, line_end_length)
        return len(value) + adjust_amount <= max_len

    @staticmethod
    def max_value(value, max_value) -> bool:
        """
        Checks if the value is less than or equal to the max. Instead of writing an max_value for 
        double, float, int, and long like in the Java version, we just remove the typing for the arguments. 
        """
        return value <= max_value

    @staticmethod
    def min_length(value: str, min_len: int) -> bool:
        """
        Checks if the value's length is greater than or equal to the min.
        """
        return len(value) >= min_len

    @staticmethod
    def min_length_with_line_end(value: str, min_len: int, line_end_length: int) -> bool:
        """
        Checks if the value's adjusted length is greater than or equal to the min, accounting for line endings.
        """
        adjust_amount = GenericValidator.adjust_for_line_ending(value, line_end_length)
        return len(value) + adjust_amount >= min_len

    @staticmethod
    def min_value(value, min_value) -> bool:
        """
        Checks if the value is greater than or equal to the min. Instead of writing an min_value for 
        double, float, int, and long like in the Java version, we just remove the typing for the arguments. 
        """
        return value >= min_value

    def __init__(self):
        # Constructor, not needed in Python but keeping it for compatibility
        pass
