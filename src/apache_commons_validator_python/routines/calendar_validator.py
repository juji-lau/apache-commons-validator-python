""" 
Module Name: calendar_validator.py

Description: Translates apache.commons.validator.routines.CalendarValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/CalendarValidator.java
    This file is meant to translate Java's ``Calendar`` class.  However, since Python's
    ``datetime.datetime`` class is much more closely functional to Java's ``Calendar`` class, this
    file will be validating Python's ``datetime.datetime`` class. 

Author: Juji Lau

License (Taken from apache.commons.validator.routines.CalendarValidator.java):
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
from __future__ import annotations            
from datetime import datetime, date, time, tzinfo
from typing import Optional, Callable

from src.apache_commons_validator_python.routines.abstract_calendar_validator import AbstractCalendarValidator
from src.apache_commons_validator_python.util.datetime_helpers import timezone_has_same_rules
from src.apache_commons_validator_python.util.validator_utils import integer_compare


class CalendarValidator(AbstractCalendarValidator):
    """Calendar Validation and Conversion Routines (using Python datetime objects)

    This module provides a collection of methods for validating and converting a
    string representing a date and/or time into a Python datetime (or date/time)
    object. Parsing can be performed using various mechanisms:
        - Using the default format for the default locale.
        - Using a specified pattern with the default locale.
        - Using the default format for a specified locale.
        - Using a specified pattern with a specified locale.

    For each of the above mechanisms, validation function implementations are provided
    which either use the system’s default timezone or allow a timezone to be explicitly specified.

    Usage:
        - Use one of the is_valid() methods to simply check if a given string is valid.
        - Use one of the validate() methods to both validate the input and return a
        converted datetime (or date/time) object.

    Additionally, methods are provided to create datetime objects adjusted for
    different time zones if the system default is not appropriate. Alternatively,
    the ``adjust_to_timezone()`` method can be used to modify the timezone of an
    existing ``datetime`` object.

    Once a value has been successfully converted, several comparison methods are
    available to perform date arithmetic and comparison checks:

        - compare_dates(): Compares the day, month, and year of two datetime objects.
        - compare_weeks(): Compares the week and year of two datetime objects.
        - compare_months(): Compares the month and year of two datetime objects.
        - compare_quarters(): Compares the quarter (computed from the month) and year
            of two datetime objects.

        These compare methods return 0 if the arguments are equal, -1 if the first
        argument is earlier, or +1 if it is later.

    To allow the same parsing mechanism used for input validation to be
    used for output formatting, corresponding format() methods are provided. These
    methods enable formatting of datetime objects by:
        - Using a specified pattern.
        - Using the format for a specified locale.
        - Using the format for the default locale.

    Attributes:
        VALDIATOR (CalendarValidator): An instance of this validator.
        serializable (bool): Indicates if the object is serializable (class attribute).
        cloneable (bool): Indicates if the object can be cloned (class attribute).
    """
    __VALIDATOR:CalendarValidator = None
    # Attributes to manage serialization and cloning capabilities
    serializable = True    # Class extends AbstracCalendarvalidator which is serializable
    cloneable = False      # Class extends AbstracCalendarvalidator which is not cloneable

    def __init__(self, *, strict:bool = True, date_style:int=3):
        """Constructs an instance of the CalendarValidator with the specified params.

        Args:
            strict (bool): If strict ``Format`` parsing should be used. (default is true)
            date_style (int): The date style to use for locale validation. Formatted 'short' by default.
        """
        super().__init__(strict=strict, date_style=date_style, time_style=-1)


    @classmethod
    def adjust_to_time_zone(cls, value:datetime, time_zone:tzinfo) -> datetime:
        """Adjusts a datetime's value to a different time_zone.

        Args:
            value (datetime): The value to adjust.
            time_zone (tzinfo): The new time zone to use to adjust the Calendar to.

        Returns:
            A new datetime with the values adjusted.
        """
        # Case 1: For a naive datetime, simply attach the new timezone.
        if value.tzinfo is None:
            return value.replace(tzinfo=time_zone)
        
        # Case 2: If current tzinfo has the same rules as new_tz,
        # then simply reassign the tzinfo without converting the local time.
        if timezone_has_same_rules(value.tzinfo, time_zone):
            return value.replace(tzinfo=time_zone)
        
        # Case 3: Otherwise, extract the local fields and create a new datetime.
        # This ensures that the local displayed time remains unchanged.
        year = value.year
        month = value.month
        day = value.day
        hour = value.hour
        minute = value.minute
        second = value.second
        microsecond = value.microsecond
        
        return datetime(year, month, day, hour, minute, second, microsecond, tzinfo=time_zone)


    @classmethod
    def get_instance(cls):
        """Returns the singleton instance of the CalendarValidator."""
        if cls.__VALIDATOR == None:
            cls.__VALIDATOR = cls()
        return cls.__VALIDATOR

    def compare_dates(self, value:datetime, compare:datetime) -> int:
        """
        Compare Dates (day, month and year - not time)

        Args:
            value (datetime): The datetime value to check.
            compare (datetime): The datetime to compare the value to.
        
        Returns:
            0 if the dates are equal, 
            -1 if the first date is less than the second.
            +1 if the first date is greater than the second.
        """
        return self._compare(value, compare, "day")


    def compare_months(self, value:datetime, compare:datetime) -> int:
        """Compare Months (month and year).

        Args:
            value (datetime): The datetime value to check.
            compare (datetime): The datetime to compare the value to.

        Returns:
            0 if the months are equal,
            -1 if the first month is less than the second.
            +1 if the first month is greater than the second.
        """
        return self._compare(value, compare, "month")

    
    def compare_quarters(self, value:datetime, compare:datetime, month_of_first_quarter:int = 1) -> int:
        """Compare Quarters (quarter and year).

        Args:
            value (datetime): The datetime value to check.
            compare (datetime): The datetime to compare the value to.
            month_of_first_quarter (int): The month the first quarter starts (default is 1 or Jaunuary)

        Returns:
            0 if the quarters are equal,
            -1 if the first quarters is less than the second.
            +1 if the first quarters is greater than the second.
        """
        return super()._compare_quarters(value=value, compare=compare, month_of_first_quarter=month_of_first_quarter)


    def compare_weeks(self, value:datetime, compare:datetime) -> int:
        """Compare Weeks (week and year).

        Args:
            value (datetime): The datetime value to check.
            compare (datetime): The datetime to compare the value to.

        Returns:
            0 if the weeks are equal,
            -1 if the first week is less than the second.
            +1 if the first week is greater than the second.
        """
        if self._compare(value, compare, "year") != 0:
            return self._compare(value, compare, "year")
    
        value_week = value.isocalendar()[1]
        compare_week = compare.isocalendar()[1]
        return integer_compare(value_week, compare_week)
        

    def compare_years(self, value:datetime, compare:datetime) -> int:
        """Compare Years.

        Args:
            value (datetime): The datetime value to check.
            compare (datetime): The datetime to compare the value to.

        Returns:
            0 if the years are equal,
            -1 if the first year is less than the second.
            +1 if the first year is greater than the second.
        """
        return self._compare(value, compare, "year")


    def _process_parsed_value(self, value:date, formatter:Callable) -> datetime:
        """Convert the parsed ``date`` to a `datetime`.

        Args:
            value (date): The parsed ``date`` object created.
            formatter (st): The format to parse the value with.

        Returns:
            The parsed value  converted to a `datetime`, with all time fields set to 0.
        """
        return datetime.combine(value, time())
            
    
    def validate(self, value:str=None, pattern:str=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None) -> datetime: 
        """Validate/convert a `datetime` using the specified `locale` and `timezone`. If
        these arguments are not provided, the system default will be used.

        Args:
            value (str): The value validation is being performed on.
            pattern (str):
            dt_locale (str): A locale string (e.g., "en_US") used for the date formatting.
                If ``None``, the default will be used.
            time_zone (tzinfo/timezone):

        Returns:
            The parsed `datetime` if valid or ``None`` if invalid.
        """
        return self._parse(value, pattern, locale, time_zone)