""" 
Module Name: time_validator.py

Description: Translates apache.commons.validator.routines.TimeValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/TimeValidator.java

Author: Juji Lau

License (Taken from apache.commons.validator.routines.TimeValidator.java):
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
  
"""
from __future__ import annotations
from datetime import datetime, date, time, tzinfo
from typing import Optional, Callable

from src.main.routines.abstract_calendar_validator import AbstractCalendarValidator


class TimeValidator(AbstractCalendarValidator):
    """
    Time validation and conversion utilities.

    This module provides methods to validate and convert string representations
    of times into `datetime.time` objects using various parsing formats and locales.

    Supported conversions:
    - Default format for the default locale
    - Specified pattern with the default locale
    - Default format for a specified locale
    - Specified pattern with a specified locale

    All conversion methods (`validate()`) allow optional specification of time zones.
    If this is not provided, the system default will be used.
    
    Alternatively, the `CalendarValidator.adjust_to_timezone()` method can be used to adjuat the `tzinfo`
    of the `datetime` object afterwards. 

    Once a value has been successfully converted the following methods can be 
    used to perform various time comparison checks:

    Date comparison methods:
    - `compare_time(d1, d2)`: Compares the hours, minutes, seconds, and milliseconds of two datettimes.
    - `compare_seconds(d1, d2)`: Compares the hours, minutes, and seconds of two times.
    - `compare_minutes(d1, d2)`: Compares hours and minutes of two times.
    - `compare_hours(d1, d2)`: Compares the hours of two times

    Formatting methods mirror parsing options and support:
    - Specified pattern
    - Format for a specified locale
    - Format for the default locale

    Attributes:
        serializable (bool): Indicates if the object is serializable.
        cloneable (bool): Indicates if the object can be cloned.
        VALIDATOR (TimeValidator): The singleton instance of this class
    """
    serializable = True   # Class extends AbstracCalendarvalidator which is serializable
    cloneable = False      # Class extends AbstracCalendarvalidator which is not cloneable

    __VALIDATOR: Optional[TimeValidator] = None  # Singleton instance

    def __init__(self, *, strict:bool = True, time_style:int = 3) -> None:
        """
        Constructs a TimeValidator instance with configurable parsing strictness and date style.

        Args:
            strict (bool): If True, enables strict date parsing. Defaults to True.
            time_style (int): An integer representing the date formatting style (default = 3, i.e. SHORT).
        """
        super().__init__(strict=strict, date_style=-1, time_style=time_style)
    
    @classmethod
    def get_instance(cls) -> TimeValidator:
        """
        Returns the singleton instance of TimeValidator.
        Ensures only one instance is created and reused globally.

        Returns:
            TimeValidator: A singleton instance of the class.
        """
        if cls.__VALIDATOR is None:
            cls.__VALIDATOR = cls()
        return cls.__VALIDATOR
    
    def compare_hours(self, value: datetime, compare: datetime) -> int:
        """
        Compare two datetime values by hours (ignores date component).

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare against.

        Returns:
            0 if the hours are equal, 
            -1 if the hour of value is less than the hour of compare, 
            +1 if the hour of value is greater than the hour of compare.
        """
        return self._compare(value, compare, "hour")

    
    def compare_minutes(self, value: datetime, compare: datetime) -> int:
        """
        Compare two datetime values by hours and minutes (ignores the date component).

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare against.

        Returns:
            0 if the hour/minutes are equal, 
            -1 if the minute of value is less than the minute of compare, 
            +1 if the minute of value is greater than the minute of compare.
        """
        return self._compare(value, compare, "minute")

    
    def compare_seconds(self, value: datetime, compare: datetime) -> int:
        """
        Compare two datetime values by hours, minutes, and seconds.

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare against.

        Returns:
            0 if the hour/minutes/seconds are equal, 
            -1 if the seconds of value is less than the seconds of compare, 
            +1 if the seconds of value is greater than the seconds of compare.
        """
        return self._compare_time(value, compare, "second")
    

    def compare_time(self, value:datetime, compare:datetime) -> int:
        """
        Compare two datetime values by absolute time (hour, minute, second, and microscecond).

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare against.

        Returns:
            0 if the times are equal
            -1 if the time represented by value is less than (earlier) the time of compare.
            +1 if the time represented by value is greater than (later) the time of compare.
        
        Changes from Java:
            Java compares the *millisecond* of two ``Calendar`` object.  
            Python's ``datetime`` does not have milliseconds. 
            The finest unit of time in a ``datetime.time`` is the *microsecond*.
            This implementation compares milliseconds to determine the earlier time.
        """
        return self._compare_time(value, compare, "microsecond")

    
    def _process_parsed_value(self, value:object, formatter:Callable) -> datetime:
        """
        Convert the parsed timezone naieve ``datetime`` to a timezone aware ``datetime``.

        Args:
            value (object): The parsed ``date`` object created.
            formatter (Callable): The formatter used during parsing (not used here, but included for consistency).

        Returns:
            The newly timezone-aware ``datetime`` object.
        """
        if isinstance(value, datetime):
            return value
        elif isinstance(value, date):
            # Converts it to a datetime by adding a time of 00:00:00.
            return datetime.combine(value, time.min)
        raise TypeError(f"Unsupported value type: {type(value)}")

    
    def validate(
        self, *,
        value: str,
        pattern: Optional[str] = None,
        locale: Optional[str] = None,
        time_zone: Optional[tzinfo] = None
    ) -> Optional[datetime]:
        """
        Validates and converts a time string into a datetime object using the provided pattern, locale, and time zone.
        The datetime will represent the time string elapsed since the epoch (year, month, day will be set to 1970, 1, 1 respectively.)

        Args:
            value (str): The input string to validate.
            pattern (Optional[str]): The date pattern (e.g., 'yyyy-MM-dd'). If None, a default pattern is used.
            locale (Optional[str]): The locale to apply (e.g., 'en_US'). If None, the system default is used.
            time_zone (Optional[tzinfo]): The timezone to apply to the resulting datetime. If None, no change is made.

        Returns:
            Optional[datetime]: 
                A datetime object representing the time-string elapsed since the the Epoch, if parsing succeeds. 
                ``None`` if invalid.
        """
        return self._parse(value, pattern, locale, time_zone)