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
from abc import ABC, abstractmethod
from typing import Any, Union, Optional, Final, Callable
from calendar import Calendar
import locale

from datetime import datetime, timezone, tzinfo
from dateparser import parse
from dateutil.tz import tzlocal
from babel.dates import format_datetime, format_time, format_date, parse_date, parse_time
from src.main.util.datetime_helpers import update_tz, locale_reg2dp
from src.main.util.utils import integer_compare, to_lower
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


    # def __calculate_quarter(self, datetime:datetime, month_of_first_quarter:int) ->int:
    #     """
    #     Calculate the quarter for the specified datetime.

    #     Args:
    #         datetime (datetime): The datetime value
    #         month_of_first_quarter: (int): The month that the first quarter starts.

    #     Returns:
    #         The calculated quarter.
    #     """
    #     # year = datetime.get(datetime.Field.YEAR)
    #     year = datetime.

    #     month:Final[int] = datetime.get(datetime.Field.MONTH) + 1
    #     relative_month:Final[int] = month-month_of_first_quarter if month >= month_of_first_quarter else month + 12 - month_of_first_quarter
    #     # relative_month = month-month_of_first_quarter
    #     # if not (month >= month_of_first_quarter):
    #     #     month += 12

    #     quarter:Final[int] = (relative_month//3) + 1
    #     if month < month_of_first_quarter:
    #         year-=1

    #     return (year*10) + quarter  


    def _compare(self, value:datetime, compare:datetime, field:str) -> int:
        """
        Compares a datetime value to another, indicating whether it is equal, less than or more than at a specified level.
        
        **Note**:
        In Java's ``AbstractCalendarValidator.compare(), the ``field`` parameter is an integer representing
        the enum mapping to Java's Calendar's fields.  Python's datetime class properties are not mapped to an enum, so the translation
        in this file has users pass in the name of the datetime property they want to compare.  This is more consistent
        with Python's datetime module, and will prevent confusion.
        
        We also removed attributes from Java's ``AbstractCalendarValidator.compare()`` that are not part of Python's datetime class.
        Removed comparing: ``Calendar.WEEK_OF_YEAR``, ``Calendar.DAY_OF_YEAR``, and ``Calendar.WEEK_OF_MONTH``, ``Calendar.DATE``, ``Calendar.DAY_OF_WEEK``, and ``Calendar.DAY_OF_WEEK_IN_MONTH``.
        Added comparing: ``datetime.day``
        Args:
            value (datetime): The datetime value.
            compare (datetime): The datetime to check the value against.
            field (int): The name of the datetime attribute to compare.
                For example, ``field = "year"`` will compare ``value.year`` and ``compare.year``.
                Case and space insensitive; "YEAR", "Year", " Year ", etc. will all work.

        Returns:
            0 if the first value is equal to the second.
            -1 if the first value is less than the second.
            1 if the first value is greater than the second.
        """ 
        # process field
        field = to_lower(field)
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
        raise NotImplementedError("python's datetime does not have quarters. Will implement if time permits.")
    #     value_quarter = self.__calculate_quarter(value, month_of_first_quarter)
    #     compare_quarter = self.__calculate_quarter(compare, month_of_first_quarter)
    #     return integer_compare(value_quarter, compare_quarter)


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
            ValueError if the field is invalid
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


    # @override
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
            print(f"_FORMAT before: {value} and tz: {value.tzinfo}")
            print(f"_FORMAT>FORMATWRE: {formatter}")
            todo = formatter(value)
            print(f"RETURNING THIS: {todo}")
            return formatter(value)


    def format(self, *, value:object=None, pattern:str=None, locale:str=None, time_zone:timezone=None) -> str:
        """
        Format an object into a string using the specified locale, and/or timezone.
        If arguments are missing, the system's default will be used.

        Args:
            value The value validation is being performed on.
            locale (str): A locale string (e.g., "en_US") used for formatting. 
                If locale is ``None`` or empty, the system default is used.
            pattern (str): The pattern used to format the value.
            time_zone (timezone): The timezone used to format the date, 
                If ``None``, the system default will be used unless value is a `datetime`.
    
        Returns:
            The value formatted as a string.

        """
        print(f"FORMAT: value: {value}, pattern: {pattern}, locale: {locale}, timezone: {time_zone}")
        if value is None:
            return None
        # Decide the timezone:
        # If the time_zone is not given, and the value is timezone-aware, use the tzinfo from the value
        # If the time_zone is not given, and the value is timezone-naive, use the system default
        # If the time_zone is given update the value tzinfo to match
        if time_zone is None:
            if isinstance(value, datetime):
                time_zone = value.tzinfo
        else:
            value = update_tz(value, time_zone)
        # Create the function; self._get_format() Sets pattern and locale
        formatter = self._get_format(pattern=pattern, locale=locale, time_zone=time_zone)
        # formatter, = self._get_format(pattern, locale, time_zone)
        # print(f"TIMEZONE EXISTS: formattetr is: {formatter} and tz is  {time_zone} ")
        # Call the function using self._format()
        return self._format(value=value, formatter=formatter)
   

    def _get_format(self, pattern: Optional[str], locale:Optional[str], time_zone:Optional[tzinfo]):
        """
        Returns a function to format the ``date`` or ``time`` object based on the specified *pattern* and/or locale.
        
        Args:
            locale (str): The locale to use for the currency format, system default if ``None``.
            pattern (str): The pattern used to validate the value against or 
                ``None`` to use the default for the locale.
            time_zone (tzinfo): The timezone information to use when formatting; use the system default if None.  
                **This was an added argument from the original Java ``AbstractCalendarValidator.getFormat()`` function,
                to interface with Python's functions better.**
        
        Returns:
            The function to format the object based on the pattern, locale, or the system default.
        """
        # from dateparser import parse
        # If the timezone is not provided, use system default

        # print(f"GET_FORMAT: pattern: {pattern}, locale: {locale}, timezone: {time_zone}")
        if time_zone is None:
            time_zone = tzlocal()
            # print(f"_getformat, tz is none: {time_zone}")
            
        # Explicitly set a locale if None
        if locale is None:
            used_locale = Locale.getdefaultlocale().language
            print(f"_getformat, used_locale none: {used_locale}")

        else:
            used_locale = locale
        
        output = {
            "pattern":pattern,
            "timezone":time_zone,
            "locale":used_locale,
            "function":None,
            "type": "datetime"
        }

        # Get the formatting pattern if it's not provided. (Use babel's ``short`` style by default.)
        used_date_format = self.__int2str_style.get(self.__date_style, 'short')
        used_time_format = self.__int2str_style.get(self.__time_style, 'short')
        used_datetime_format = f"{used_date_format} {used_time_format}"

        # if pattern is None or ""
        if GenericValidator.is_blank_or_null(pattern):
            if self.__date_style >= 0 and self.__time_style >= 0:
                    # print(f"111 _get_format both ds and ts")
                    # output["function"] = format_datetime()
                    # output["pattern"] = used_datetime_format
                    # print(f"1111 _get_format both ds and ts {output}")
                return lambda dt:format_datetime(dt, format=used_datetime_format, locale=used_locale, tzinfo=time_zone)
                # if locale is None:
                #     # Use system default
                #     pass

                # else:
                #     # use locale
                #     pass
            elif self.__time_style >= 0:
                print(f"222 _get_format just ts")
                output["function"] = format_time
                output["pattern"] = used_time_format
                output["type"] = "time"
                print(f"222 _get_format just t {output}")

                return lambda time:format_time(time, format=used_time_format, locale=used_locale, tzinfo=None)
            else:
                # Need to update the timezone accordingly
                # Try returning a tuple: (pattern, locale, timezone, function to call)
                # return (used_date_format, locale, time_zone, format_date())
                # date = self._parse(value=, locale=used_locale, settings=settings)
                output["function"] = format_date
                output["pattern"] = used_time_format
                output["type"] = "date"
                print(f"333 _get_format only ds {output}")

                        # return output
                return lambda date:format_date(date, format=used_date_format, locale=used_locale)
                # settings = {'TO_TIMEZONE' : str(time_zone)}
                # used_locale = used_locale.replace("_", "-")
                # lang, locale = used_locale.split('-')

                # return lambda date:str((parse(str(date), date_formats=[used_date_format], locales=['en-001'], settings=settings)).date())
                # return lambda dt:format_datetime(dt, format=used_date_format, locale=used_locale, tzinfo=time_zone)
                # if self.__date_style >= 0:
                # else:
                #     use_date_style = date_format.SHORT
                # if locale is None:
                #     pattern = 
                # else:
                    # pattern = 
            # return datetime.strftime(pattern)
        
        elif locale is None:

            # If there's a pattern but no locale, use the system default
            # Babel uses the system default if locale is not provided
            output["function"] = format_datetime
            # output["pattern"] = pattern
            output["locale"] = None
            output["type"] = "datetime"
            print(f"444_get_format have pattern, NO locale {output}")
            return lambda dt:format_datetime(dt, format=pattern)
        else:
            # If there's a pattern AND a locale
            output["function"] = format_datetime
            # output["pattern"] = pattern
            # output["locale"] = used_locale
            output["type"] = "datetime"
            print(f"555 _get_format have pattern AND locale, {output}")
            return lambda dt:format_datetime(dt, format=pattern, locale=used_locale)

    def is_valid(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None) -> bool:
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
 
    
    # def _parse(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None) -> Optional[object]:
    #     """
    #     Checks if the value is valid against a specified pattern.

    #     Args:
    #         value (str): The value validation is being performed on.
    #         pattern (str): The pattern used to validate the value against, or the default for locale if ``None``.
    #         locale (str): The locale to use for the date format, if ``None``, the system default will be used.
    #         time_zone (timezone): The time zone used to parse the date. If ``None``, the system default will be used.
        
    #     Returns:
    #         The parsed value if valid, or ``None`` if invalid.
    #     """
    #     print(f"IN SUPER ABS FORMATPASE: value: {value}, pattern: {pattern}, locale: {locale}, time_zone: {time_zone}")

    #     if value is not None:
    #         value = value.strip()
    #     if GenericValidator.is_blank_or_null(value):
    #         # Nothing to parse
    #         print(f"PARSE Time validation 1")
    #         return None
        
    #     # if pattern is None, use default
    #     # if pattern is None:
    #     #     pattern = 'short'
    #     # formatter = self._get_format(pattern, locale)
    #     if time_zone is not None:
    #         print(f"PARSE: Time validation 2")
    #         # This is an aware datetime; create the datetime and set the timezone.
    #         # Set the timezone
    #         # date = parse_date(string=value, locale=locale, format=pattern)
    #         date = parse(value)
    #         print(f"PARSE: Time validation 2: parse date done: {date}")
    #         time = parse_time(value)
    #         # time = parse_time(string=value, locale=locale, format=pattern)
    #         print(f"PARSE: Time validation 2: parse time done: {time}")
   
    #         dt = datetime.combine(date, time, tzinfo = time_zone)
    #         # dt.replace(tzinfo = time_zone)
    #         print(f"PARSE: time validation 2: parse datetime done: {dt}")
    #         return dt
    #     # Timezone is none, but there's a locale
    #     if locale is not None:
    #         print(f"PARSE Time validation 3")
    #         # parse() is picky with locale inputs, so try multiple ways to get a value.
    #         dp_locale = locale_reg2dp(locale)
    #         dt = parse(date_string=value, locales=[dp_locale])
    #         if dt is None:
    #             if "_" in locale:
    #                 lang, country = locale.split("_")
    #                 dt = parse(value, languages = [lang])
    #                 if dt is None:
    #                     dt = parse(value, region=country)
    #         return dt
    #     # Locale and timezone are BOTH none
    #     print(f"PARSE Time validation 5")
    #     dt = parse(date_string=value)
    #     # Return a naive object
    #     # dt = parse(date_string=value, settings={'RETURN_AS_TIMEZONE_AWARE': False})
    #     print(f"CREATED DT: {dt}")
    #     return dt


    
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
        """
        # if value is not None:
        #     value = value.strip()
        if GenericValidator.is_blank_or_null(value):
            return None
        if pattern is not None:
            # use locale default
            formatter = self._get_format(pattern, locale)
        else:
            pass

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