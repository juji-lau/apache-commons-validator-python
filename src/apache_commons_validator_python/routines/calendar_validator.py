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
    """
    Calendar Validation and Conversion Routines.
    
    This class offers methods to validate and convert string representations of datetime
    objects into `datetime` objects, and methods to format `datetime` objects as strings.

    Formatting, parsing, and validation methods support custom patterns, locales, and timezones,
    using the system default if not provided.

    Attributes:
        serializable (bool): Indicates if the object is serializable (class attribute).
        cloneable (bool): Indicates if the object can be cloned (class attribute).
    """    
    # Attributes to manage serialization and cloning capabilities
    serializable = True    # Class extends AbstracCalendarvalidator which is serializable
    cloneable = False      # Class extends AbstracCalendarvalidator which is not cloneable
    __VALIDATOR:CalendarValidator = None    # A singleton instance of this CalendarValidator.


    def __init__(self, *, strict:bool = True, date_style:int=3):
        """Initializes the CalendarValidator with configurable parsing strictness and
        date style.

        Args:
            strict (bool): If True, enforces strict format parsing. Defaults to True.
            date_style (int): The date style to use for locale validation. Defaults to 3 (short format).
        """
        super().__init__(strict=strict, date_style=date_style, time_style=-1)


    @classmethod
    def adjust_to_time_zone(cls, value:datetime, time_zone:tzinfo) -> datetime:
        """Adjusts a datetime's value to a different timezone.

        Args:
            value (datetime): The datetime value to adjust.
            time_zone (tzinfo): The new timezone to apply.

        Returns:
            datetime: A new datetime with the adjusted timezone.
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
        """Returns the singleton instance of the CalendarValidator.

        Returns:
            CalendarValidator: The singleton instance.
        """
        if cls.__VALIDATOR == None:
            cls.__VALIDATOR = cls()
        return cls.__VALIDATOR

    def compare_dates(self, value:datetime, compare:datetime) -> int:
        """
        Compares two datetimes based on day, month, and year (not time).

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare.

        Returns:
            int: 0 if equal, -1 if value < compare, 1 if value > compare.
        """
        return self._compare(value, compare, "day")


    def compare_months(self, value:datetime, compare:datetime) -> int:
        """Compare two datetimes based on months (month and year).

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare.

        Returns:
            int: 0 if equal, -1 if value < compare, 1 if value > compare.
        """
        return self._compare(value, compare, "month")

    
    def compare_quarters(self, value:datetime, compare:datetime, month_of_first_quarter:int = 1) -> int:
        """Compare two datetimes based on Quarters (quarter and year).

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare.
            month_of_first_quarter (int): The starting month of the first quarter. Defaults to 1 (January).

        Returns:
            int: 0 if equal, -1 if value < compare, 1 if value > compare.
        """
        return super()._compare_quarters(value=value, compare=compare, month_of_first_quarter=month_of_first_quarter)


    def compare_weeks(self, value:datetime, compare:datetime) -> int:
        """
        Compare two datetimes based on year, then ISO week.
        
        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare.

        Returns:
            int: 0 if equal, -1 if value < compare, 1 if value > compare.
        """
        if self._compare(value, compare, "year") != 0:
            return self._compare(value, compare, "year")
    
        value_week = value.isocalendar()[1]
        compare_week = compare.isocalendar()[1]
        return integer_compare(value_week, compare_week)
        

    def compare_years(self, value:datetime, compare:datetime) -> int:
        """Compares two datetimes based on year.

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare.

        Returns:
            int: 0 if equal, -1 if value < compare, 1 if value > compare.
        """
        return self._compare(value, compare, "year")


    def _process_parsed_value(self, value:date, formatter:Callable) -> datetime:
        """
        Converts a parsed date to a datetime with time set to midnight.

        Args:
            value (date): The parsed date object.
            formatter (Callable): The formatter used for parsing.

        Returns:
            datetime: The combined datetime object with time set to 00:00:00.
        """
        return datetime.combine(value, time())
            
    
    def validate(self, value:str=None, pattern:str=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None) -> datetime: 
        """
        Validates and converts a string to a datetime object.

        Args:
            value (str, optional): The string to validate.
            pattern (str, optional): The pattern to use for parsing.
            locale (str, optional): The locale to use for parsing.
            time_zone (tzinfo, optional): The timezone to apply.

        Returns:
            datetime or None: The parsed datetime if valid, otherwise None.
        """
        return self._parse(value, pattern, locale, time_zone)