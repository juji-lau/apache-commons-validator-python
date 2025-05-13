""" 
Module Name: date_validator.py

Description: Translates apache.commons.validator.routines.DateValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/DateValidator.java

Authors: Alicia Chu, Juji Lau

License (Taken from apache.commons.validator.routines.DateValidator.java):
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
from typing import Optional, Final, Callable

from src.apache_commons_validator_python.routines.abstract_calendar_validator import AbstractCalendarValidator
from src.apache_commons_validator_python.util.validator_utils import integer_compare

class DateValidator(AbstractCalendarValidator):
    """
    Date validation and conversion utilities.

    This class offers methods to validate and convert string representations
    of dates into `datetime` objects optionally using various parsing formats, 
    timezones, and locales.
   
    Attributes:
        serializable (bool): Indicates if the object is serializable.
        cloneable (bool): Indicates if the object can be cloned.
        VALIDATOR (DateValidator): The singleton instance of this class
    """
    serializable = True    # class extends AbstracCalendarvalidator which is serializable
    cloneable = False      # class extends AbstracCalendarvalidator which is not cloneable
    __VALIDATOR: Optional[DateValidator] = None  # Singleton instance of this DateValidator


    def __init__(self, *, strict: bool = True, date_style:int=3) -> None:
        """
        Constructs a DateValidator instance with configurable parsing strictness and
        date style.

        Args:
            strict (bool): If True, enables strict date parsing. Defaults to True.
            date_style (int): An integer representing the date formatting style (default = 3, i.e. SHORT).
        """
        super().__init__(strict=strict, date_style=date_style, time_style=-1)
    
    @classmethod
    def get_instance(cls) -> DateValidator:
        """
        Returns the singleton instance of DateValidator.

        Returns:
            DateValidator: The single global instance of the class.
        """
        if cls.__VALIDATOR is None:
            cls.__VALIDATOR = cls()
        return cls.__VALIDATOR
    
    def compare_dates(self, value: datetime, compare: datetime, time_zone: Optional[tzinfo] = None) -> int:
        """Compare two datetime values by day, month, and year (ignores time component).

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare against.
            time_zone (Optional[tzinfo]): Optional time zone to align both values before comparison.

        Returns:
            int: 0 if the dates are equal, -1 if `value` is earlier, +1 if later.
        """
        calendar_value: Final[datetime] = self.__get_calendar(value, time_zone)
        calendar_compare: Final[datetime] = self.__get_calendar(compare, time_zone)
        return self._compare(calendar_value, calendar_compare, "day")

    def compare_months(self, value: datetime, compare: datetime, time_zone: Optional[tzinfo] = None) -> int:
        """Compare two datetime values by month and year (ignores day and time).

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare against.
            time_zone (Optional[tzinfo]): Optional time zone to align both values before comparison.

        Returns:
            int: 0 if the month/year are equal, -1 if `value` is earlier, +1 if later.
        """
        calendar_value: Final[datetime] = self.__get_calendar(value, time_zone)
        calendar_compare: Final[datetime] = self.__get_calendar(compare, time_zone)
        return self._compare(calendar_value, calendar_compare, "month")

    def compare_quarters(
        self,
        value: datetime,
        compare: datetime,
        time_zone: Optional[tzinfo] = None,
        month_of_first_quarter: datetime = 1
    ) -> int:
        """Compare two datetime values by quarter and year.

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare against.
            time_zone (Optional[tzinfo]): Optional time zone to align both values before comparison.
            month_of_first_quarter (datetime): Month the first quarter starts (1 = January, 3 = March, etc.).

        Notes:
            This Python implementation uses `month_of_first_quarter=1` by default,
            replicating the overloaded Java method:
                compareQuarters(value, compare, timeZone)
        Returns:
            int: 0 if quarters are equal, -1 if `value` is earlier, +1 if later.
        """
        calendar_value: datetime = self.__get_calendar(value, time_zone)
        calendar_compare: datetime = self.__get_calendar(compare, time_zone)
        return super()._compare_quarters(calendar_value, calendar_compare, month_of_first_quarter)
    
    def compare_weeks(
        self,
        value: datetime,
        compare: datetime,
        time_zone: Optional[tzinfo] = None
    ) -> int:
        """Compare two datetime values by ISO week number and year.

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare against.
            time_zone (Optional[tzinfo]): Optional time zone to align both values before comparison.

        Returns:
            int: 0 if ISO week/year are equal, -1 if `value` is earlier, +1 if later.
        """
        calendar_value: Final[datetime] = self.__get_calendar(value, time_zone)
        calendar_compare: Final[datetime] = self.__get_calendar(compare, time_zone)
        # datetime.datetime does not have the attribute, "week"
        # First, compare the year. If needed, extract the week.
        year_diff = self._compare(calendar_value, calendar_compare, "year")
        if year_diff == 0:
            _, val_week, _ = calendar_value.isocalendar()
            _, compare_week, _ = calendar_compare.isocalendar()
            return integer_compare(val_week, compare_week)
        return year_diff

    def compare_years(
        self,
        value: datetime,
        compare: datetime,
        time_zone: Optional[tzinfo] = None
    ) -> int:
        """Compare two datetime values by year only.

        Args:
            value (datetime): The first datetime to compare.
            compare (datetime): The second datetime to compare against.
            time_zone (Optional[tzinfo]): Optional time zone to align both values before comparison.

        Returns:
            int: 0 if years are equal, -1 if `value` is earlier, +1 if later.
        """
        calendar_value: Final[datetime] = self.__get_calendar(value, time_zone)
        calendar_compare: Final[datetime] = self.__get_calendar(compare, time_zone)
        return self._compare(calendar_value, calendar_compare, "year")
    

    def __get_calendar(
        self,
        value: datetime,
        time_zone: Optional[tzinfo]
    ) -> datetime:
        """
        Returns a datetime object adjusted to the specified time zone, if provided.

        Args:
            value (datetime): The input datetime.
            time_zone (Optional[tzinfo]): The time zone to convert to. If None, the original is returned.

        Returns:
            datetime: Timezone-adjusted datetime, or original if `time_zone` is None.
        """
        if time_zone is not None:
            # If the datetime is naive (no tzinfo), attach the timezone directly
            if value.tzinfo is None:
                return value.replace(tzinfo=time_zone) 
            # If it's timezone-aware, convert to the new timezone
            return value.astimezone(time_zone)
        return value
    
    def _process_parsed_value(
        self,
        value: object,
        formatter: Callable
    ) -> datetime:
        """Processes the parsed value by converting a `date` object to a `datetime` with
        time set to 00:00:00.

        Args:
            value (object): The parsed value from the formatter (typically a `date` or `datetime`).
            formatter (Callable): Formatter used during parsing (unused but kept for compatibility with Java).

        Returns:
            datetime: The normalized datetime object.

        Raises:
            TypeError: If `value` is not a `date` or `datetime`.

        """
        if isinstance(value, datetime):
            return value
        elif isinstance(value, date):
            # Converts it to a datetime by adding a time of 00:00:00.
            return datetime.combine(value, time.min)
        raise TypeError(f"Unsupported value type: {type(value)}")

    
    def validate(
        self,
        value: str,
        pattern: Optional[str] = None,
        locale: Optional[str] = None,
        time_zone: Optional[tzinfo] = None
    ) -> Optional[datetime]:
        """
        Validate and convert a date string to a datetime object.

        Args:
            value (str): Input date string.
            pattern (Optional[str]): Date pattern (e.g., '%Y-%m-%d'). Uses default if None.
            locale (Optional[str]): Locale to use for parsing.
            time_zone (Optional[tzinfo]): Time zone to apply to resulting datetime.

        Returns:
            Optional[datetime]: Parsed datetime if valid; otherwise, None.
        """
        return self._parse(value, pattern, locale, time_zone)