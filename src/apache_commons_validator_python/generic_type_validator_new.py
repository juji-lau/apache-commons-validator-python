"""Licensed to the Apache Software Foundation (ASF) under one or more contributor
license agreements.  See the NOTICE file distributed with this work for additional
information regarding copyright ownership. The ASF licenses this file to You under the
Apache License, Version 2.0 (the "License"); you may not use this file except in
compliance with the License.  You may obtain a copy of the License at.

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from typing import Final, Optional
from ..generic_validator_new import GenericValidator
from datetime import datetime
import locale
import numpy as np


class GenericTypeValidator:
    """GenericTypeValidator class provides methods to format and validate different
    types of data inputs.

    Use NumPy data types for byte, double, short, and long from Java version since these
    do not exist in Python.
    """

    serializable: Final[bool] = True
    cloneable: Final[bool] = False
    _logger = logging.getLogger(__name__)

    @staticmethod
    def format_byte(value: Optional[str]) -> Optional[int]:
        """Method to convert a string value to an integer (byte)

        Args:
            value (str): the value validation is being performed on

        Returns: the converted integer (byte) value
        """
        if value is None:
            return None
        try:
            return np.int8(value)
        except ValueError:
            return None

    @staticmethod
    def format_byte_locale(
        value: Optional[str], locale: Optional[str] = None
    ) -> Optional[int]:
        """Method to convert a string value to an integer (byte) with optional locale
        support.

        Args:
            value (str): the value validation is being performed on
            locale (str) the locale to use to parse the number (system default if null)

        Returns: the converter integer (byte) value
        """
        if value is None:
            return None

        try:
            # Set the locale if provided, otherwise use the default locale
            if locale:
                locale.setlocale(locale.LC_ALL, locale)
            else:
                locale.setlocale(locale.LC_ALL, "")  # Use default locale

            # Attempt to convert the value to np.int8 (byte type in NumPy)
            return np.int8(value)

        except (ValueError, TypeError):
            # Return None if parsing fails or locale error occurs
            return None

    @staticmethod
    def format_credit_card(value: Optional[str]) -> Optional[int]:
        """Method to check if a string value represents a valid credit card and convert
        it to an integer.

        Args:
            value (str): the valie validation is being performed on

        Returns: the converted Credit Card number
        """
        if GenericValidator.is_credit_card(value):
            return int(value)
        return None

    @staticmethod
    # Method to convert a string value to a datetime object (date) using the system's locale
    def format_date(
        value: Optional[str], locale: Optional[str] = None
    ) -> Optional[datetime]:
        """Method to convert a string value to a datetime object (date) using the
        system's locale.

        Args:
            value (str): the value validation is being performed on
            locale (str): the locale to use to parse the data (system default if null)

        Returns: the converted Date value
        """
        if value is None:
            return None

        try:
            if locale:
                locale.setlocale(locale.LC_ALL, locale)

            return datetime.strptime(
                value, "%x"
            )  # Try to convert the value to a datetime object
        except ValueError:
            if GenericTypeValidator._logger.isEnabledFor(logging.DEBUG):
                GenericTypeValidator._logger.debug(
                    f"Date parse failed value=[{value}], locale=[{locale}]"
                )
            return None

    @staticmethod
    def format_date_pattern(
        value: Optional[str], date_pattern: Optional[str], strict: bool
    ) -> Optional[datetime]:
        """Method to convert a string value to a datetime object using a custom date
        pattern.

        Args:
            value (str): the value validation is being performed on
            date_pattern (str): the pattern
            strict (bool): whether or not to have an exact match of the date_pattern

        Returns: the converted Date value
        """
        if value is None or date_pattern is None:
            return None

        try:
            date = datetime.strptime(value, date_pattern)
            if strict and len(value) != len(date_pattern):
                return None
            return date
        except ValueError:
            if GenericTypeValidator._logger.isEnabledFor(logging.DEBUG):
                GenericTypeValidator._logger.debug(
                    f"Date parse failed value=[{value}], pattern=[{date_pattern}], strict=[{strict}]"
                )
            return None

    @staticmethod
    def format_double(value: Optional[str]) -> Optional[float]:
        """Method to convert a string value to a float with optional locale support.

        Args:
            value (str): the value validation is being performed on

        Returns: the converted Double value
        """
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def format_double_locale(
        value: Optional[str], locale: Optional[str] = None
    ) -> Optional[float]:
        """Format a string value into a float (double-precision), respecting the
        provided locale.

        Returns:
            None if the value is invalid.
        """
        if value is None:
            return None

        try:
            # Set the locale if provided, otherwise use the default locale
            if locale:
                locale.setlocale(locale.LC_ALL, locale)
            else:
                locale.setlocale(locale.LC_ALL, "")  # Use default locale

            return float(value)

        except (ValueError, TypeError):
            # Return None if parsing fails
            return None
        
    @staticmethod
    def format_float(value: Optional[str]) -> Optional[float]:
        """Method to convert a string value to a float.

        Args:
            value (str): the value validation is being performed on

        Returns: the converted Float value
        """
        if value is None:
            return None
        try:
            return np.float32(value)
        except ValueError:
            return None

    @staticmethod
    def format_float_locale(
        value: Optional[str], locale: Optional[str] = None
    ) -> Optional[float]:
        """Method to convert a string value to a float with locale support.

        Args:
            value (str): the value validation is being performed on
            locale (str): the locale to use to parse the number (system default if None)

        Returns: the converted float value
        """
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
        """Checks if the value can safely be converted to an int primitive.

        Args:
            value (str): the value validation is being performed on

        Returns: the converted int value
        """
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def format_int_locale(
        value: Optional[str], locale: Optional[str] = None
    ) -> Optional[int]:
        """Format a string value into an integer, respecting the provided locale.

        Returns None if the value is invalid or out of range.
        """
        if value is None:
            return None

        try:
            # Set the locale if provided, otherwise use the default locale
            if locale:
                locale.setlocale(locale.LC_ALL, locale)
            else:
                locale.setlocale(locale.LC_ALL, "")  # Use default locale

            # Attempt to parse the value as a number
            parsed_value = locale.atoi(value)  # Convert the string to an integer

            # Return the parsed value as np.int32 (standard integer type in NumPy)
            return np.int32(parsed_value)

        except (ValueError, locale.Error):
            # Return None if parsing fails or locale error occurs
            return None

    @staticmethod
    def format_long(value: Optional[str]) -> Optional[int]:
        """Format a string value into a long integer (64-bit).

        Returns None if the value is invalid or out of range.
        """
        if value is None:
            return None
        try:
            return np.int64(value)
        except ValueError:
            return None

    @staticmethod
    def format_long_locale(
        value: Optional[str], locale: Optional[str] = None
    ) -> Optional[int]:
        """Format a string value into a long integer (64-bit), respecting the provided
        locale.

        Returns None if the value is invalid or out of range.
        """
        if value is None:
            return None

        try:
            # Set the locale if provided, otherwise use the default locale
            if locale:
                locale.setlocale(locale.LC_ALL, locale)
            else:
                locale.setlocale(locale.LC_ALL, "")  # Use default locale

            # Attempt to parse the value as a long integer (64-bit)
            parsed_value = locale.atoi(value)  # Convert the string to an integer

            # Return the parsed value as np.int64 (64-bit integer type in NumPy)
            return np.int64(parsed_value)

        except (ValueError, locale.Error):
            # Return None if parsing fails or locale error occurs
            return None
        
    @staticmethod
    def format_short(value: Optional[str]) -> Optional[int]:
        """Format a string value into a short integer (16-bit).

        Returns None if the value is invalid or out of range.
        """
        if value is None:
            return None
        try:
            return np.int16(value)
        except ValueError:
            return None

    @staticmethod
    def format_short_locale(
        value: Optional[str], locale: Optional[str] = None
    ) -> Optional[int]:
        """Format a string value into a short integer (16-bit), respecting the provided
        locale.

        Returns None if the value is invalid or out of range.
        """
        if value is None:
            return None

        try:
            # Set the locale if provided, otherwise use the default locale
            if locale:
                locale.setlocale(locale.LC_ALL, locale)
            else:
                locale.setlocale(locale.LC_ALL, "")  # Use default locale

            # Attempt to parse the value as a short integer (16-bit)
            parsed_value = locale.atoi(value)  # Convert the string to an integer

            # Return the parsed value as np.int16 (16-bit integer type in NumPy)
            return np.int16(parsed_value)

        except (ValueError, locale.Error):
            # Return None if parsing fails or locale error occurs
            return None


""" 
#deprecated
class GenericValidator:
    @staticmethod
    def is_credit_card(value: Optional[str]) -> bool:
       
        return True  # Placeholder for actual validation """