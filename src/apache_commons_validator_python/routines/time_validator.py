""" 
Module Name: time_validator.py

Description: 
    This module provides a Python translation of Apache Commons Validator’s
    ``TimeValidator.java``, focusing on validating and converting time strings
    into Python’s ``datetime`` objects (with the date fields set to the unix epoch: Jan 1, 1970), 
    using locale-aware formats and custom patterns.  Original Java source at:
        https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/TimeValidator.java


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
"""
from __future__ import annotations
from datetime import datetime, date, time, tzinfo
from typing import Optional, Callable

from src.apache_commons_validator_python.routines.abstract_calendar_validator import AbstractCalendarValidator


class TimeValidator(AbstractCalendarValidator):
    """
    Time validation and conversion utilities.

    This class offers methods to parse and validate ``time`` string representations 
    into ``datetime`` objects, with the ``date`` fields set to the unix epoch (Jan 1, 1970),
    and methods to format ``datetime.time`` objects as strings.

    Formatting, parsing, and validation methods support custom patterns, locales, and timezones,
    using the system default if not provided.
    
    Attributes:
        serializable (bool): Indicates if the object is serializable.
        cloneable (bool): Indicates if the object can be cloned.
    """
    serializable = True   # Class extends AbstracCalendarvalidator which is serializable
    cloneable = False      # Class extends AbstracCalendarvalidator which is not cloneable
    __VALIDATOR: Optional[TimeValidator] = None  # Singleton instance of this TimeValidator

    def __init__(self, *, strict:bool = True, time_style:int = 3) -> None:
        """Constructs a TimeValidator instance with configurable parsing strictness and
        time style.

        Args:
            strict (bool): If True, enables strict date parsing. Defaults to True.
            time_style (int): An integer representing the date formatting style (default = 3, i.e. SHORT).
        """
        super().__init__(strict=strict, date_style=-1, time_style=time_style)
    
    @classmethod
    def get_instance(cls) -> TimeValidator:
        """
        Retrieve the singleton TimeValidator instance.

        Returns:
            TimeValidator: The single, shared instance of this class.
        """
        if cls.__VALIDATOR is None:
            cls.__VALIDATOR = cls()
        return cls.__VALIDATOR
    
    def compare_hours(self, value: datetime, compare: datetime) -> int:
        """
        Compare two datetimes by hour component only.

        Args:
            value (datetime): First datetime to compare.
            compare (datetime): Second datetime to compare against.

        Returns:
            int: 0 if hours equal, -1 if ``value.hour`` < ``compare.hour``, +1 otherwise.
        """
        return self._compare(value, compare, "hour")

    
    def compare_minutes(self, value: datetime, compare: datetime) -> int:
        """
        Compare two datetimes by hour, then minute components.

        Args:
            value (datetime): First datetime to compare.
            compare (datetime): Second datetime to compare against.

        Returns:
            int: 0 if minute/hour equal, -1 if ``value.minute`` < ``compare.minute``, +1 otherwise.
        """
        return self._compare(value, compare, "minute")

    
    def compare_seconds(self, value: datetime, compare: datetime) -> int:
        """Compare two datetimes by hour, minute, then second components.

        Args:
            value (datetime): First datetime to compare.
            compare (datetime): Second datetime to compare against.

        Returns:
            int: 0 if second/minute/hour equal, -1 if ``value.second`` < ``compare.second``, +1 otherwise.
        """
        return self._compare_time(value, compare, "second")
    

    def compare_time(self, value:datetime, compare:datetime) -> int:
        """
        Compare two datetimes by full time (hour, minute, second, then microsecond).

         Note:
            Python’s ``datetime`` uses microseconds rather than milliseconds (Java's Calendar).
            This implementation accomodates that.
        
        Args:
            value (datetime): First datetime to compare.
            compare (datetime): Second datetime to compare against.

        Returns:
            int: 0 if times equal, -1 if ``value`` < ``compare``, +1 otherwise.
        """
        return self._compare_time(value, compare, "microsecond")

    
    def _process_parsed_value(self, value:object, formatter:Callable) -> datetime:
        """
        Converts the parsed value into a ``datetime`` with the time fields set to midnight
        if the value is a `date`.

        Args:
            value (object): Parsed ``date`` or ``datetime`` from the parser.
            formatter (Callable): Parsing formatter (unused, but included for consistency).

        Returns:
            datetime: A ``datetime``; midnight added for date inputs.

        Raises:
            TypeError: If ``value`` is not a ``date`` or ``datetime``.
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
        Validate and parse a time string into a datetime.

        The resulting datetime represents the parsed time on the epoch date
        (1970-01-01).

        Args:
            value (str): Time string to validate.
            pattern (str, optional): LDML pattern for parsing.
            locale (str, optional): Locale code (e.g., 'en_US').
            time_zone (tzinfo, optional): Time zone to apply.

        Returns:
            datetime or None: Parsed datetime if valid, otherwise None.
        """
        return self._parse(value, pattern, locale, time_zone)