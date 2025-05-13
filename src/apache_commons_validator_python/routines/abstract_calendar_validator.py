""" 
Module Name: abstract_calendar_validator.py

Description:
    This module provides a Python translation of the Apache Commons Validator
    AbstractCalendarValidator (original Java source at:
        https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/AbstractCalendarValidator.java).

Author: Juji Lau

License (Taken from apache.commons.validator.routines.AbstractCalendarValidator.java):
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
    - Removed Java's Calendar fields that don't have an equivalent datetime field, and added the closest equivalent Python datetime field 
        (e.g. `Calendar.MILLISECOND` -> datetime.millisecond`)
    - Modified compare() signature to accept string field names instead of integers for consistency with Python's datetime module.
    - Seperated `parse()` into helper functions to handle `date`, `time`, and `datetime` strings independently.
    - Added helper function, `get_format_no_pattern()` to avoid overloading the `_get_format()` when no pattern is passed in (simpler logic).
"""
from babel import Locale
from babel.dates import format_datetime, format_time, format_date
from datetime import datetime, timezone, tzinfo, date
from dateparser import parse
from typing import Union, Optional, Callable

from ..util.datetime_helpers import (
    get_default_tzinfo, 
    get_default_locale, 
    get_tzname, 
    fuzzy_parse, 
    ldml2strpdate, 
    ldml2strptime, 
    parse_pattern_flexible, 
    parse_pattern_strict, 
    ldml_to_strptime_format
)
from ..util.validator_utils import (
    integer_compare, 
    to_lower
)
from ..util.locale import Locale
from ..generic_validator_new import GenericValidator
from ..routines.abstract_format_validator import AbstractFormatValidator


class AbstractCalendarValidator(AbstractFormatValidator):
    """
    Abstract base class for calendar-based validators using format parsing.

    This class provides shared mechanisms for date, time, and datetime parsing,
    validation, and formatting, using Babel, DateParser, and datetime.

    Attributes:
        date_style (int): The date style to use for Locale validation.
        time_style (int): The time style to use for Locale validation.
        serializable (bool): Indicates if the object is serializable.
        cloneable (bool): Indicates if the object can be cloned.
    """
    # Maps the integer date and time style to a string argument for `babel.format()`.
    __int2str_style = {
        0:'full',
        1:'long',
        2:'medium',
        3:'short'
    }
    # Attributes to manage serialization and cloning capabilities
    serializable = True    # class is serializable
    cloneable = False      # class is not cloneable

    def __init__(self, strict:bool, date_style:int, time_style:int):
        """
        Initialize the calendar validator.

        Args:
            strict (bool): Whether to enforce strict parsing rules.
            date_style (int): Date style code (0-3) for locale formatting.
            time_style (int): Time style code (0-3) for locale formatting.
        """
        super().__init__(strict)
        self.__date_style = date_style
        self.__time_style = time_style
    

    def __calculate_compare_result(self, value:datetime, compare:datetime, field:str) -> int:
        """
        Compare a specific datetime attribute between two datetimes.

        Args:
            value (datetime): First datetime.
            compare (datetime): Second datetime.
            field (str): Name of the attribute to compare (e.g., "year", "month").
                Space padding and case-insensitve.

        Returns:
            int: 0 if equal, -1 if `value.<field>` < `compare.<field>`, 1 otherwise.

        """
        return integer_compare(getattr(value, field), getattr(compare, field))


    def __calculate_quarter(self, calendar:datetime, month_of_first_quarter:int) ->int:
        """
        Determine the quarter of the year for a datetime.

        Args:
            calendar (datetime): Input datetime.
            month_of_first_quarter (int): Month where Q1 begins (1=Jan).

        Returns:
            int: Calculated quarter; an integer code combining year and quarter (year*10 + quarter).
        """
        year = calendar.year
        month = calendar.month
        
        if month > month_of_first_quarter:
            relative_month = month - month_of_first_quarter
        else:
            relative_month = month + 12 - month_of_first_quarter
        
        quarter = relative_month // 3 + 1

        if month < month_of_first_quarter:
            year -= 1
        
        return (year * 10) + quarter


    def _compare(self, value:datetime, compare:datetime, field:str) -> int:
        """
        Compare two datetimes at the specified field level, cascading to smaller units if equal.

        Note:
            For field="week", performs ISO week/year comparison. Falls back to successive
            comparisons of year, month, day, and time attributes if needed.

        Args:
            value (datetime): First datetime.
            compare (datetime): Second datetime.
            field (str): Attribute name to compare (field = "week" for ISO week comparisons).
                Space padding and case-insensitve.

        Returns:
            int: Comparison result: 0 if equal, -1 if `value` < `compare`, 1 if `value` > `compare`.
        """ 
        # process field
        field = to_lower(field)

        # Cover edge case of weeks
        if field == "week":
            return self.compare_weeks(value, compare)
            
        # Compare Year
        result = self.__calculate_compare_result(value, compare, field)
        if result != 0 or field == "year":
            return result

        # Compare Month 
        result = self.__calculate_compare_result(value, compare, "month")
        if result != 0 or field == "month":
            return result

        # Compare Day
        result = self.__calculate_compare_result(value, compare, "day")
        if result != 0 or field == "day":
            return result
        
        # Compare Time fields
        return self._compare_time(value, compare, field)
    

    def _compare_quarters(self, value:datetime, compare:datetime, month_of_first_quarter:int) ->int:
        """
        Compare two datetimes by quarter of the year.

        Args:
            value (datetime): First datetime.
            compare (datetime): Second datetime.
            month_of_first_quarter (int): Month where Q1 begins.

        Returns:
            int: 0 if equal quarter, -1 if less, 1 if greater.
        """
        value_quarter = self.__calculate_quarter(value, month_of_first_quarter)
        compare_quarter = self.__calculate_quarter(compare, month_of_first_quarter)
        print(f"Value: {value_quarter}, compare; {compare_quarter}")
        return integer_compare(value_quarter, compare_quarter)


    def _compare_time(self, value:datetime, compare:datetime, field:int) -> int:
        """
        Compare two datetimes at the time component level.
            
        Args:
            value (datetime): First datetime.
            compare (datetime): Second datetime.
            field (str): Time attribute name (e.g. "hour", "minute", "second", "microsecond").  
                Space padding and case insensitve.

        Returns:
            int: 0 if equal, -1 if `value.<field>` < `compare.<field>`, 1 otherwise.

        Raises:
            ValueError: If `field` is not a valid time attribute.
        """
        # process field
        field = to_lower(field)

        # Compare Hour
        result = self.__calculate_compare_result(value, compare, "hour")
        if (result != 0 or field == "hour"):
            return result

        # Compare Minute
        result = self.__calculate_compare_result(value, compare, "minute")
        if (result != 0 or field == "minute"):
            return result

        # Compare Second
        result = self.__calculate_compare_result(value, compare, "second")
        if (result != 0 or field == "second"):
            return result

        # Compare Microsecond
        if field == "microsecond":
            return self.__calculate_compare_result(value, compare, "microsecond")

        raise ValueError(f"Invalid field: {field}")


    def _format(self, *, value:object, formatter:Callable) -> str:
        """
        Format a date or datetime object using the given formatter.

        Args:
            value (object): The input datetime or date.
            formatter (Callable): Function that formats a datetime into string.

        Returns:
            str: Formatted string, or None if `value` is None.
        """
        if value is None:
            return None
        
        # Convert it to a date
        if isinstance(value, datetime):
            return formatter(value)


    def format(self, *, value:object=None, pattern:str=None, locale:Union[str, Locale]=None, time_zone:timezone=None) -> str:
        """
        Format a date/time object to string with optional pattern and locale.

        Args:
            value (object): The date or datetime to format.
            pattern (str): LDML pattern string. Uses locale defaults if None.
            locale (str): Locale code (e.g., "en_US"). Uses system default if None.
            time_zone (timezone): Time zone for output. 
                Uses value.tzinfo if timezone is None. 
                Uses system default if both are None.

        Returns:
            str: Formatted date/time string, or None if `value` is None.
        """
        if value is None:
            return None
        # Decide the timezone:
        # If the time_zone is not given, and the value is timezone-aware, use the tzinfo from the value
        # If the time_zone is not given, and the value is timezone-naive, use the system default
        # If the time_zone is given update the value tzinfo to match

        # If the timezone is not given, use the value's timezone or the system default.
        if time_zone is None:
            if isinstance(value, datetime):
                time_zone = value.tzinfo
            else:
                time_zone = get_default_tzinfo()
        # If the timezone is given, update the value's timezone to match.
        else:
            if isinstance(value, datetime):
                if value.tzinfo is None:
                    value = value.replace(tzinfo=time_zone)
                else:
                    value = value.astimezone(tz=time_zone)
       
        formatter = self._get_format(pattern=pattern, locale=locale)
        return self._format(value=value, formatter=formatter)
   

    def _get_format(self, pattern:str=None, locale:str=None) -> Callable:
        """
        Retrieve a formatting function for datetime based on pattern and/or locale.

        Args:
            pattern (str): LDML format pattern. If None, use the default style for `locale`.
            locale (str): The locale string to use for formatting. Defaults to system locale.

        Returns:
            Callable: Function that formats a datetime.
        """
        if locale is None:
            locale = get_default_locale()

       
        def get_format_no_pattern(locale:Union[str, Locale]) -> Callable:
            """
            Called only when pattern is blank or None.
            Returns: 
                Callable: Function to format the datetime based on specified locale. 
            """
            # Get formatting styles for date and time
            date_format_style = self.__int2str_style.get(self.__date_style, 'short')
            time_format_style = self.__int2str_style.get(self.__time_style, 'short')
            
            # Formatting a datetime
            if self.__date_style >= 0 and self.__time_style >= 0:
                # Create the datetime pattern of this class.
                datetime_format_style = f"{date_format_style} {time_format_style}"  
                return lambda dt:format_datetime(dt, format = datetime_format_style, locale = locale) 
            # Formatting a time only
            elif self.__time_style >= 0:        
                return lambda dt:format_time(dt, format = time_format_style, locale = locale)          
            # Formatting a date only
            else:
                return lambda dt:format_date(dt, format = date_format_style, locale = locale)

        if GenericValidator.is_blank_or_null(pattern):
            # No pattern given; purely dependent on locale.
            return get_format_no_pattern(locale)
        else:
            # Use both locale AND pattern to format the datetime
            return lambda dt:format_datetime(datetime=dt, format=pattern, locale=locale)


    def is_valid(self, *, value:str, pattern:Optional[str]=None, locale:Optional[str]=None) -> bool:
        """
        Validate a date, time, or datetime string using the specified pattern and locale.

        Args:
            value (str): The input string to validate.
            pattern (str): LDML pattern string. Uses locale defaults if None.
            locale (str): Locale code (e.g., "en_US"). Uses system default if None.
            
        Returns:
            bool: True if parsable, False otherwise.
        """
        return (self._parse(value, pattern, locale, time_zone=None) is not None)
 

    def _parse(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None) -> Optional[object]:
        """
        Checks if the value is valid against a specified pattern. 
        If valid, parses a string into a datetime object.

        Note:
            Java uses the ``protected getFormat()`` to create an object, because
            `SimpleDateFormat.parse()` accepts a ``DateFormat``.
            Here, `DateParser.parse()` is used, which does NOT accept a callable or a formatter.
        
        Args:
            value (str): The value string validation is being performed on
            pattern (str): LDML pattern string. Uses locale defaults if None.
            locale (str): Locale code (e.g., "en_US"). Uses system default if None.
            time_zone (tzinfo): Time zone for parsing. Defaults to system zone if None.

        Returns:
            object: Parsed value or None if parsing fails.
        """
        if GenericValidator.is_blank_or_null(value):
            return None
      
        # Create the settings dict to call dateparser.parse() with,
        # And set the time_zone to the system default if `None`.
        settings = {'RETURN_AS_TIMEZONE_AWARE': True}
        if time_zone is None:
            time_zone = get_default_tzinfo()
        else:
            # If we are not using default, we need to tell dateparser parse to the passed in tzinfo
            settings.update({'TIMEZONE' : get_tzname(time_zone)})
        settings.update({'TO_TIMEZONE' : get_tzname(time_zone)})
        
        # Call the correct parser
        if self.__time_style >= 0 and self.__date_style >= 0:
            # Parsing datetime(not implemented here)
            return self.__parse_datetime(value, pattern, locale, time_zone, settings)
        elif self.__time_style >= 0:
            # Parsing time only
            return self.__parse_time(value, pattern, locale, time_zone, settings)
        else:
            # Parsing date only (by process of elimination)
            assert (self.__date_style < 0 and self.__time_style < 0) is False, f"ERROR: No specified date or time validation."
            return self.__parse_date(value, pattern, locale, time_zone, settings)
    

    def __parse_datetime(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None, settings=None) -> Optional[object]:
        """
        Checks if the value is valid against a specified pattern. 
        If valid, parses a datetime string into a datetime object.
        
        Note:
            A use case was not implemented in Java's Validator, so this function is untested.
        """
        if GenericValidator.is_blank_or_null(pattern):
            pattern = ""
        if locale is None:
            return parse(date_string=value, date_formats=[pattern], settings=settings)
        else:
            return fuzzy_parse(value=value, pattern=pattern, locale=locale, settings=settings)

      
    def __parse_date(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None, settings=None) -> Optional[object]:
        """
        Checks if the value is valid against a specified pattern. 
        If valid, parses a date or datetime string into a datetime object.
        """
        if GenericValidator.is_blank_or_null(pattern) or locale is None:
            try:
                # No pattern, use locale only (which may or may not be the default).
                if GenericValidator.is_blank_or_null(pattern):
                    date_format = self.__int2str_style.get(self.__date_style, 'short')
                    dt = ldml2strpdate(
                        value=value, 
                        style_format=date_format, 
                        locale=locale
                    )
                # Pattern provided, no locale (use pattern only)
                elif locale is None:
                    dt = parse_pattern_flexible(value, pattern)
                
                # Configure timezone
                if time_zone is not None:
                    dt = dt.replace(tzinfo=time_zone)
                
                return dt
            except Exception as e:
                return None

        # Parsing with locale and pattern (note, this is a last resort and not fully accurate).
        return fuzzy_parse(value=value, pattern=pattern, locale=locale, settings=settings)


    def __parse_time(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None, settings=None) -> Optional[object]:
        # TODO: Improve documentation
        """
        Checks if the value is valid against a specified pattern. 
        If valid, parses a time string into a datetime object, with the date fields set to the epoch: (1970, Jan, 1).
        """
        try:
            # No pattern providee; Use locale only (which may or may not be the default).
            if GenericValidator.is_blank_or_null(pattern):
                time_format = self.__int2str_style.get(self.__time_style, 'short')
                dt_time = ldml2strptime(
                    value=value,
                    style_format=time_format,
                    locale=locale
                )
            # Pattern provided, No locale (use pattern only)
            elif locale is None:
                dt_time = parse_pattern_strict(value, pattern)
            
            # Pattern AND locale provided. Use both.
            else:
                # Technically the same code as `locale is None` branch, but this case is kept separate
                # for easier debugging, in case of future issues.
                strptime_format = ldml_to_strptime_format(pattern)
                dt_time = datetime.strptime(value, strptime_format)
            
            # Remove the (year, month, day) component, and represent the datetime in terms of time only.
            if dt_time is not None:
                epoch_date = date(1970, 1, 1)
                return datetime.combine(epoch_date, dt_time.time(), tzinfo=time_zone)
                
        except Exception as e:
            return None


    def _process_parsed_value(self, value:object, formatter):
        """
        Process the parsed value, performing any further validation and type conversion required.
        (Abstract method)

        Args:
            value (object): The parsed object created.
            formatter (str): The format to parse the value with

        Returns:
            The parsee value converted to the appropriate type if valid, or ``None`` if invalid.
        """
        pass