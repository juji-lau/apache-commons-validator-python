""" 
Module Name: abstract_calendar_validator.py

Description: Translates apache.commons.validator.routines.AbstractCalendarValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/AbstractCalendarValidator.java
 
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
    - Removed Java's Calendar fields that don't have an equivalent datetime field.
    
    Modified ``AbstractCalendarValidator.compare(Calendar value, Calendar compare, int field)`` have users pass in a string 
    instead of an int. Python's datetime validator does not map its properties to integers, hence using integers will be confusing
    to Python users.

    Implemented ``parse()`` in the concrete subclasses instead.

"""
from babel import Locale
from babel.dates import (
    format_datetime, 
    format_time, 
    format_date
)
from datetime import datetime, timezone, tzinfo, date
from dateparser import parse
from typing import Union, Optional, Callable

from src.main.util.datetime_helpers import (
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
from src.main.util.utils import (
    integer_compare, 
    to_lower
)
from src.main.util.Locale import Locale
from src.main.generic_validator import GenericValidator
from src.main.routines.abstract_format_validator import AbstractFormatValidator


class AbstractCalendarValidator(AbstractFormatValidator):
    """
    Abstract class for Date/Time/Calendar validation

    This is a base class for building Date/Time Validators using format parsing.

    Attributes:
        date_style (int): The date style to use for Locale validation.
        time_style (int): The time style to use for Locale validation.
        int2str_style (dict[int, str]): Maps the integer date and time style to a string argument for ``babel.format()``.
        serializable (bool): Indicates if the object is serializable.
        cloneable (bool): Indicates if the object can be cloned.
    """
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
        Constructs an instance with the specified *strict*, *time*, and *date* style parameters.
        
        Args:
            strict (bool): ``True`` if strict ``Format`` parsing should be used.
            date_style (int): The date style to use for Locale validation.
            time_style (int): The time style to use for Locale validation.
        """
        super().__init__(strict)
        self.__date_style = date_style
        self.__time_style = time_style
    

    def __calculate_compare_result(self, value:datetime, compare:datetime, field:str) -> int:
        """
        Compares the field from two datetimes indicating whether the field for the first 
        datetime is equal to, less than or greater than the field from the second datetime.

        Args:
            value (datetime): The datetime value.
            compare (datetime): The datetime to check the value against.
            field (int): The attribute to compare for the datetimes.

        Returns:
            0 if the field for both datetimes are equal. 
            -1 if the field for the first datetime (value) it is less than the field for the second (compare).
            1 if the field for the first datetime (value) is greater than the seconds.
        """
        return integer_compare(getattr(value, field), getattr(compare, field))


    def __calculate_quarter(self, calendar:datetime, month_of_first_quarter:int) ->int:
        """
        Calculate the quarter for the specified datetime.

        Args:
            datetime (datetime): The datetime value
            month_of_first_quarter: (int): The month that the first quarter starts.

        Returns:
            The calculated quarter.
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
        Compares a datetime value to another, indicating whether it is equal, less than or more than at a specified level.
        
        Args:
            value (datetime): The datetime value.
            compare (datetime): The datetime to check the value against.
            field (int): The name of the datetime attribute to compare.
                For example: ``field = "year"`` will compare ``value.year`` and ``compare.year``.
                Case and space insensitive: "YEAR", "Year", " Year ", etc. will all work.

        Returns:
            0 if the first value is equal to the second.
            -1 if the first value is less than the second.
            1 if the first value is greater than the second.

        **Changes from Java**:
            In Java's ``AbstractCalendarValidator.compare()``, the ``field`` parameter is an integer representing
            the enum mapping to Java's Calendar's fields.  Python's datetime class properties are not mapped to an enum, so the translation
            in this file has users pass in the name of the datetime property they want to compare.  This is more consistent
            with Python's datetime module, and will prevent confusion.
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
        Compares a datetime's quarter value to another, indicating whether it is 
        equal, less than or more than the specified quarter.

        Args:
            value (datetime): The datetime value.
            compare (datetime): The `datetime` to check the value against.
            month_of_first_quarter (int): The  month that the first quarter starts.
        
        Returns:
            0 if the first quarter is equal to the second.
            -1 if the first quarter is less than the second.
            1 if the first quarter is greater than the second.
        """
        value_quarter = self.__calculate_quarter(value, month_of_first_quarter)
        compare_quarter = self.__calculate_quarter(compare, month_of_first_quarter)
        print(f"Value: {value_quarter}, compare; {compare_quarter}")
        return integer_compare(value_quarter, compare_quarter)


    def _compare_time(self, value:datetime, compare:datetime, field:int) -> int:
        """
        Compares a datetime time value to another, indicating whether it is equal, 
        less than or more than at a specified level.
             
        **Note**:
        In Java's ``AbstractdatetimeValidator.compare(), the ``field`` parameter is an integer representing
        the enum mapping to Java's Calendar's fields.  Python's datetime class properties are not mapped to an enum, so the translation
        in this file has users pass in the name of the datetime property they want to compare.  This is more consistent
        with Python's datetime module, and will prevent confusion.

        Removed comparing ``Calendar.MICROSECOND``
        Added comparing ``datetime.millisecond``
        
        Args:
            value (datetime): The datetime value.
            compare (datetime): The `datetime` to check the value against.
            field (int): The name of the datetime attribute to compare.
                For example, ``field = "minute"`` will compare ``value.minute`` and ``compare.minute``.
                Case and space insensitive; "MINUTE", "minute", " Minute ", etc. will all work.

        Returns:
            0 if the first value is equal to the second.
            -1 if the first value is less than the second.
            1 if the first value is greater than the second.
   
        Raises:
            ``ValueError`` if the field is invalid
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
        Format a ``date`` value as a string with the sepcified ``formatter``.

        Args:
            value (Any): The value to be formatted.
            formatter (Callable): The format string to use.

        Returns:
            The formatted date as a string, or ``None`` if the value is ``None``.
        """
        if value is None:
            return None
        
        # Convert it to a date
        if isinstance(value, datetime):
            return formatter(value)


    def format(self, *, value:object=None, pattern:str=None, locale:Union[str, Locale]=None, time_zone:timezone=None) -> str:
        """
        Format an object into a string using the specified pattern and/or locale.

        Args:
            value (object): The value validation is being performed on.
            pattern (str): The pattern used to format the value.
            locale (str): A locale string (e.g., "en_US") used for formatting. 
                If locale is ``None`` or empty, the system default is used.
            time_zone (timezone): The timezone used to format the date, 
                If ``None``, the system default will be used unless value is a `datetime`.
    
        Returns:
            The value formatted as a String.

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
        Returns a function to format the ``datetime`` or ``time`` for the specified *pattern* and/or `locale`.
        
        Args:
            pattern (str): The pattern used to validate the value against. 
                If ``None``, we use the default for the `Locale`.
            locale (str): The locale to use for the currency format. System default if None. 
 
        Returns:
            The function to format the object based on the pattern, locale, or the system default.
        """
        if locale is None:
            locale = get_default_locale()

       
        def get_format_no_pattern(locale:Union[str, Locale]) -> Callable:
            """
            Returns a function to format the ``datetime`` or ``time`` for the specified locale.
            Called when pattern is blank or None.

            Args:
                locale (Union[str, Locale]): The locale to use.
            
            Returns:
                The function to format the object.
            
            Changes from Java:
                In the Java implementation, this was an overloaded function of ``protected Format getFormat()`` which only took a Locale.
                Instead of overloading the Python ``_get_format()``, I used a helper function to keep the logic closer to the
                Java implementation, hence easier to debug.
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
        Validate using the specified locale.

        Args:
            value (str): The value validation is being performed on.
            pattern (str): The pattern used to format the value.
            locale (str): The locale to use for the Format, defaults to the system if None.

        Returns:
            ``True`` if the value is valid; ``False`` otherwise.
        """
        return (self._parse(value, pattern, locale, time_zone=None) is not None)
 

    def _parse(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None) -> Optional[object]:
        """
        Checks if the value is valid against a specified pattern.

        Args:
            value (str): The value string validation is being performed on
            pattern (Optional[str]): The pattern (e.g., 'yyyy-MM-dd') used to validate the value against. 
                If ``None``, the default pattern for the ``locale`` is used.
            locale (Optional[str]): The locale to use for the datetime format (e.g., 'en_US'). System default if ``None``.
            time_zone (Optional[tzinfo]): The timezone used to parse the datetime. System default if ``None``.

        Returns:
            Optional[datetime]: The parsed value if valid, or ``None`` if parsing fails.
       
        Changes from Java:
            Java uses the ``protected getFormat()`` defined in the file to create an object, because
            there is a ``parse()`` function that accepts a ``DateFormat``.
            For Python, we will use DateParser.parse(), which does NOT accept a callable or a formatter.
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
        A use case was not implemented in Java's Validator, so this function is untested.
        """
        if GenericValidator.is_blank_or_null(pattern):
            pattern = ""
        if locale is None:
            return parse(date_string=value, date_formats=[pattern], settings=settings)
        else:
            return fuzzy_parse(value=value, pattern=pattern, locale=locale, settings=settings)

      
    def __parse_date(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None, settings=None) -> Optional[object]:
        # TODO: Improve documentation
        """
        Returns the ``datetime`` object parsed from the value stirng based on the passed in locale and timezone.
        Uses system default for the locale and timezone if any of them are ``None``.

        Args:
            value (str): TODO
            pattern (str): TODO
            locale (Union[str, Locale]): The locale to use when parsing; System default if ``None``.
            time_zone (tzinfo): The timezone to parse the object to.
            settings (dict): TODO            

        Returns: 
            The parsed ``datetime`` object.
        
        Changes from Java:
            This function does not exist in Java. It was created to mimic the logic in our
            ``_get_format()``, since we need the logic but cannot use the function.
            (See documentation for ``_parse()`` for a more detailed explanation.)
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
        Returns the ``datetime`` object parsed from the value stirng based on the passed in locale and timezone.
        Sets the year, month, day to the epoch (Jan 1, 1970), so the ``datetime`` represents time.
        Uses system default for the locale and timezone if any of them are ``None``.

        Args:
            value (str): TODO
            pattern (str): TODO
            locale (Union[str, Locale]): The locale to use when parsing; System default if ``None``.
            time_zone (tzinfo): The timezone to parse the object to.
            settings (dict): TODO

        Returns: 
            The parsed ``datetime`` object that represents the timestring value by seting the 
            datetime fields: (year, month, day) to the epoch: (1970, Jan, 1).
        
        Changes from Java:
            This function does not exist in Java. It was created to mimic the logic in our
            ``_get_format()``, since we need the logic but cannot use the function.
            (See documentation for ``_parse()`` for a more detailed explanation.)
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