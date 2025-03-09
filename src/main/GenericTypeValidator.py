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

import logging
from typing import Final, Optional
from GenericValidator import GenericValidator
from datetime import datetime
import locale

class GenericTypeValidator:
    """
        GenericTypeValidator class provides methods to format and validate different 
        types of data inputs. Removed function from Java version for 
        double, long, and short since these do not exist in Python.
    """
    serializable: Final[bool] = True
    cloneable: Final[bool] = False
    _logger = logging.getLogger(__name__)

    @staticmethod
    # Method to convert a string value to an integer (byte)
    def format_byte(value: Optional[str]) -> Optional[int]:
        if value is None:
            return None

        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
     # Method to convert a string value to an integer (byte) with optional locale support
    def format_byte_locale(value: Optional[str], locale: Optional[str] = None) -> Optional[int]:
        if value is None:
            return None

        try:
            if locale:
                locale.setlocale(locale.LC_ALL, locale)
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    # Method to check if a string value represents a valid credit card and convert it to an integer
    def format_credit_card(value: Optional[str]) -> Optional[int]:
        if GenericValidator.is_credit_card(value):
            return int(value)
        return None

    @staticmethod
     # Method to convert a string value to a datetime object (date) using the system's locale
    def format_date(value: Optional[str], locale: Optional[str] = None) -> Optional[datetime]:
        if value is None:
            return None

        try:
            if locale:
                locale.setlocale(locale.LC_ALL, locale)

            return datetime.strptime(value, "%x") # Try to convert the value to a datetime object
        except ValueError:
            if GenericTypeValidator._logger.isEnabledFor(logging.DEBUG):
                GenericTypeValidator._logger.debug(f"Date parse failed value=[{value}], locale=[{locale}]")
            return None

    @staticmethod
    # Method to convert a string value to a datetime object using a custom date pattern
    def format_date_pattern(value: Optional[str], date_pattern: Optional[str], strict: bool) -> Optional[datetime]:
        if value is None or date_pattern is None:
            return None

        try:
            date = datetime.strptime(value, date_pattern)
            if strict and len(value) != len(date_pattern):
                return None
            return date
        except ValueError:
            if GenericTypeValidator._logger.isEnabledFor(logging.DEBUG):
                GenericTypeValidator._logger.debug(f"Date parse failed value=[{value}], pattern=[{date_pattern}], strict=[{strict}]")
            return None

    @staticmethod
     # Method to convert a string value to a float with optional locale support
    def format_float(value: Optional[str]) -> Optional[float]:
        if value is None:
            return None

        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def format_float_locale(value: Optional[str], locale: Optional[str] = None) -> Optional[float]:
        if value is None:
            return None

        try:
            if locale:
                locale.setlocale(locale.LC_ALL, locale)
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def format_int(value: Optional[str]) -> Optional[int]:
        if value is None:
            return None

        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def format_int_locale(value: Optional[str], locale: Optional[str] = None) -> Optional[int]:
        if value is None:
            return None

        try:
            if locale:
                locale.setlocale(locale.LC_ALL, locale)
            return int(value)
        except (ValueError, TypeError):
            return None

""" 
#deprecated
class GenericValidator:
    @staticmethod
    def is_credit_card(value: Optional[str]) -> bool:
       
        return True  # Placeholder for actual validation """
