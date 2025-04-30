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

from datetime import datetime, timezone, tzinfo, date, time
from dateparser import parse
from dateutil.tz import tzlocal
from babel import Locale
from babel.dates import format_datetime, format_time, format_date, parse_date, parse_time
# from src.main.util.datetime_helpers import update_tz, locale_reg2dp, get_default_tzinfo, val_is_naive, get_tzname, babel_parse_datetime, babel_parse_date, babel_parse_time
import src.main.util.datetime_helpers as dt_help
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
        print(f"FORMAT: value: {value}, pattern: {pattern}, locale: {locale}, timezone: {time_zone}")
        if value is None:
            return None
        # Decide the timezone:
        # If the time_zone is not given, and the value is timezone-aware, use the tzinfo from the value
        # If the time_zone is not given, and the value is timezone-naive, use the system default
        # If the time_zone is given update the value tzinfo to match
        if time_zone is None:
            if isinstance(value, datetime):
                # Grab existing tzinfo
                time_zone = value.tzinfo
            else:
                time_zone = tzlocal()
        else:
            # If timezone is given, update the object to match the timezone
            if isinstance(value, datetime):
                value = dt_help.update_tz(value, time_zone)
       
        # Create the function; self._get_format() Sets pattern and locale
        formatter = self._get_format(pattern=pattern, locale=locale)
        # formatter, = self._get_format(pattern, locale, time_zone)
        # print(f"TIMEZONE EXISTS: formattetr is: {formatter} and tz is  {time_zone} ")
        # Call the function using self._format()
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

        def get_format_locale(locale:Union[str, Locale] = None) -> Callable:
            """
            Returns a function to format the ``datetime`` or ``time`` for the specified locale.

            Args:
                locale (Union[str, Locale]): The locale to use; System default if ``None``.
            
            Returns:
                The function to format the object.
            
            Changes from Java:
                In the Java implementation, this was an overloaded function of ``protected Format getFormat()`` which only took a Locale.
                Instead of overloading the Python ``_get_format()``, I used a helper function to keep the logic closer to the
                Java implementation, hence easier to debug.
            """
            # date, time
            # no date, time
            # Last one is neither
                # date, no time
                # neither?? not represented
            # Locale is given; pattern is not; use locale
            if self.__date_style >= 0 and self.__time_style >= 0:
                # Formatting a datetime
                # Create the datetime pattern of this class.
                used_date_format = self.__int2str_style.get(self.__date_style, 'short')
                used_time_format = self.__int2str_style.get(self.__time_style, 'short')
                used_datetime_format = f"{used_date_format} {used_time_format}"  
                if locale is None:
                    # Use system default for locale
                    formatter = lambda dt:format_datetime(dt, format = used_datetime_format)
                else:
                    # Use provided locale AND initialized style
                    formatter = lambda dt:format_datetime(dt, format = used_datetime_format, locale = locale) 
            
            elif self.__time_style >= 0:
                # Formatting a time only
                used_time_format = self.__int2str_style.get(self.__time_style, 'short')
                if locale is None:
                    # Use system default
                    formatter = lambda dt:format_time(dt, format = used_time_format)
                else:
                    # Use provided locale AND initialized style
                    formatter = lambda dt:format_time(dt, format = used_time_format, locale = locale)

            else:
                # Formatting a date only
                used_date_format = self.__int2str_style.get(self.__date_style, 'short')
                if locale is None:
                    # Use system default
                    formatter = lambda dt:format_date(dt, format = used_date_format)
                else:
                    # Use provided locale AND initialized style
                    formatter = lambda dt:format_date(dt, format = used_date_format, locale = locale)
            return formatter

        if GenericValidator.is_blank_or_null(pattern):
            # No pattern given; purely dependent on locale (which may or may not be None).
            return get_format_locale(locale=locale)
        elif locale is None:
            # Locale is None, we have a pattern
            return lambda dt:format_datetime(datetime=dt, format=pattern)
        else:
            # Locale and pattern are BOTH given
            # TODO: Ensure that this function uses both pattern and locale for stricter check, instead of prioritizing one.
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
        print(f"IN SUPER ABS FORMATPASE: value: {value}, pattern: {pattern}, locale: {locale}, time_zone: {time_zone}")

        if GenericValidator.is_blank_or_null(value):
            return None
        
        # if both are none, use default
        # Automatically defaults to local timezone but need to make it timezone aware
        # if time_zone is None:
        #     # GOOD.
        #     settings = {'RETURN_AS_TIMEZONE_AWARE': True}
        # else:
        #     if val_is_naive(value):
        #         settings = {'RETURN_AS_TIMEZONE_AWARE': True, 'TIMEZONE':get_tzname(time_zone)}
        #     else:
        #         settings = {'RETURN_AS_TIMEZONE_AWARE': True, 'TO_TIMEZONE' : get_tzname(time_zone)}
        if time_zone is None:
            # Get local timezone
            time_zone = dt_help.get_default_tzinfo()
            # settings = {'RETURN_AS_TIMEZONE_AWARE': True}
        # else:
        # if dt_help.val_is_naive(value):
        #     settings = {'RETURN_AS_TIMEZONE_AWARE': True, 'TIMEZONE':dt_help.get_tzname(time_zone)}
        # #     settings = {'RETURN_AS_TIMEZONE_AWARE': True, 'TO_TIMEZONE' : dt_help.get_tzname(time_zone)}

        # else:
        #     settings = {'RETURN_AS_TIMEZONE_AWARE': True, 'TO_TIMEZONE' : dt_help.get_tzname(time_zone)}
        # # if string is none, and timezone is some, do naive, and convert the dt to timezone
        # settings = {'RETURN_AS_TIMEZONE_AWARE': True, 'TO_TIMEZONE' : time_zone.tz_name()}
        # # if string is some, and timezone is some, use string representation, and convert to timezone
       
       
        settings = {'RETURN_AS_TIMEZONE_AWARE': True, 'TO_TIMEZONE' : dt_help.get_tzname(time_zone)}
        if time_zone != dt_help.get_default_tzinfo():
            settings.update({'TIMEZONE' : dt_help.get_tzname(time_zone)})

        # # if string is some, and timezone is none, use string.
        # settings = {'RETURN_AS_TIMEZONE_AWARE': True}

        # settings = {}
        # if time_zone is not None:
        #     settings.update({'TO_TIMEZONE':time_zone.tzname()})
        # else:
        #     time_zone = dt_help.get_default_tzinfo()
        #     print(f"DEFAULT TO LOCAL TIMEZONE")
        # tz_name = time_zone.tzname()
        # settings = {'TIMEZONE': tz_name, 'RETURN_AS_TIMEZONE_AWARE': True}
        print(f"ABSTRACT.parse, SETTINGS: {settings}")
        if self.__time_style >= 0 and self.__date_style >= 0:
            print(f"Parsing datetime")
            return self.__parse_datetime(value, pattern, locale, time_zone, settings)
        elif self.__time_style >= 0:
            print(f"Parsing time only")
            return self.__parse_time(value, pattern, locale, time_zone, settings)
        else:
            print(f"Parsing date only")
            if self.__date_style < 0 and self.__time_style < 0:
                print(f"ERROR, no specified DATE or TIME validation??")
            return self.__parse_date(value, pattern, locale, time_zone, settings)
    
    def __parse_datetime(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None, settings=None) -> Optional[object]:
        return 0
        def parse_datetime_locale(value:str, locale:Union[str, Locale] = None, settings:dict=None) -> object:
            """
            Returns the ``datetime`` or ``time`` object based on the passed in locale.
            Uses system default if ``None``.
            Only called if there is no pattern.

            Args:
                locale (Union[str, Locale]): The locale to use when parsing; System default if ``None``.
                time_zone (tzinfo): The timezone to parse the object to.

            Returns: 
                The parsed ``datetime`` or ``time`` object.
            
            Changes from Java:
                This function does not exist in Java. It was created to mimic the logic in our
                ``_get_format()``, since we need the logic but cannot use the function.
                (See documentation for ``_parse()`` for a more detailed explanation.)
            """
            # Only called if pattern is None
            # Formatting a datetime or date
            if locale is None:
                # Pattern AND locale is None
                dt = parse(date_string=value, settings=settings)
                print(f"abstract.__dtparser used default locale: {dt}")

                # dt = dt_help.babel_parse_datetime(value, locale, pattern, time_zone)
                # date = parse_date(string=value, locale=locale, format=pattern)
                # time = parse_time(string=value, locale=locale, format=pattern)
                # dt = datetime.combine(date, time, tzinfo = time_zone)
                # Use system default for locale
                # formatter = lambda dt:format_datetime(dt, format = used_datetime_format)
            else:
                # Use provided locale AND initialized style
                dt = dt_help.babel_parse_datetime(value=value, locale=locale, pattern=None, time_zone=time_zone)
                if dt is None:
                    dp_locale = dt_help.locale_reg2dp(locale)
                    dt = parse(date_string=value, locales=[dp_locale], settings=settings)
                    if dt is None:
                        print(f"REGULAR PARSE FAILED, {value}")
                    # TODO: refactor bulky parse
                        if "_" in locale:
                            lang, country = locale.split("_")
                            dt = parse(value, languages = [lang], settings=settings)
                            if dt is None:
                                dt = parse(value, region=country, settings=settings)
                        else:
                            # Try language only
                            dt = parse(value, languages = [dp_locale], settings=settings)
                            if dt is None:
                                # Try country only
                                dt = parse(value, region = dp_locale, settings=settings)
                if dt is None:
                    print(f"ABSTRACT.PARSE_HELPER failed; returning None.")
                else:
                    print(f"Abstract.parse_locale, dt: {dt}")
                return dt

        if GenericValidator.is_blank_or_null(pattern):
            # No pattern, use locale only (which may or may not be the default).
            dt = parse_datetime_locale(value, locale, settings=settings)
            return dt
        elif locale is None:
            # Pattern provided, no locale (use pattern only)
            dt = parse(date_string=value, date_formats=[pattern], settings=settings)
            print(f"ABSTRACT.PARSE, No locale: Value: {value}, settings: {settings}, result: {dt}")

        else:
            print(f"Locale and pattern BOTH given; use both")
            # TODO: Figure bulky parse
            dp_locale = dt_help.locale_reg2dp(locale)
            dt = parse(date_string=value, date_formats=[pattern], locales=[dp_locale], settings=settings)
            if dt is None:
                if "_" in locale:
                    lang, country = locale.split("_")
                    dt = parse(value, date_formats = [pattern], languages = [lang], settings=settings)
                    if dt is None:
                        dt = parse(value, date_formats = [pattern], region=country, settings=settings)
                else:
                    # Try language only
                    dt = parse(value, languages = [dp_locale], settings=settings)
                    if dt is None:
                        # Try country only
                        dt = parse(value, region = dp_locale, settings=settings)
                if dt is None:
                    print(f"ABSTRACT.PARSE FAILED, returning None")
                    # return None
                print(f"ABSTRACT.PARSE, Locale and Pattern given: Value: {value}, settings: {settings}, result: {dt}")
                return dt

      
    def __parse_date(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None, settings=None) -> Optional[object]:
        # parsing date only
        print(f"ABSTRACT: PARSING DATE ONLY")
        def parse_date_locale(value:str, locale:Union[str, Locale] = None, time_zone:tzinfo=None, settings =None) -> object:
            """
            Returns the ``datetime`` object based on the passed in locale.
            Uses system default if ``None``.
            Only called if there is no pattern.

            Args:
                locale (Union[str, Locale]): The locale to use when parsing; System default if ``None``.
                time_zone (tzinfo): The timezone to parse the object to.

            Returns: 
                The parsed ``datetime`` object.
            
            Changes from Java:
                This function does not exist in Java. It was created to mimic the logic in our
                ``_get_format()``, since we need the logic but cannot use the function.
                (See documentation for ``_parse()`` for a more detailed explanation.)
            """

            # Only called if we are parsing a time AND pattern is not given
            if locale is None:
                # Pattern AND locale is None
                # settings = {'RETURN_AS_TIMEZONE_AWARE': True}
                print(f"Settings b4: {settings} and value {value}")

                # if time_zone != dt_help.get_default_tzinfo():
                #     settings.update({'TIMEZONE' : dt_help.get_tzname(time_zone)})
                # print(f"Settings afta: {settings} and value {value}")
                dt = parse(date_string=value, settings=settings)
                # print(f"CUrr dt: {dt} and time: {dt_help.date_get_time(dt)}")
                # dt = dt.astimezone(time_zone)
                # print(f"New dt: {dt} and time: {dt_help.date_get_time(dt)}")
                # dt = dt_help.babel_parse_date(value, pattern=pattern, time_zone=time_zone)
                # if dt is None:
                #     print(f"Babel parser failed, try dateparser")
                #     dt = parse(date_string=value, settings=settings)
                #     if dt is None:
                #         print(f"babel and dateparser failed.")
                # print(f"PARSED DT: {dt}, and INFO: {dt.tzinfo}")
            else:
                # Use provided locale AND initialized style
                dt = dt_help.babel_parse_date(value, locale, pattern, time_zone)
                if dt is None:
                    print(f"Babel parse date failed., Try dp.parse()")
                    dp_locale = dt_help.locale_reg2dp(locale)
                    dt = parse(date_string=value, locales=[dp_locale], settings=settings)
                    if dt is None:
                    # TODO: refactor bulky parse
                        if "_" in locale:
                            lang, country = locale.split("_")
                            dt = parse(value, languages = [lang], settings=settings)
                            if dt is None:
                                dt = parse(value, region=country)
                        else:
                            # Try language only
                            dt = parse(value, languages = [dp_locale], settings=settings)
                            if dt is None:
                                # Try country only
                                dt = parse(value, region = dp_locale, settings=settings)
            if dt is None:
                print(f"ABSTRACT.PARSE_dt_HELPER failed; returning None.")
            else:
                print(f"Abstract.parse_dt helper returning dt: {dt}")
            return dt


        if GenericValidator.is_blank_or_null(pattern):
            # No pattern, use locale only (which may or may not be the default).
            print(f"No pattern provided; using locale as defaults")
            return parse_date_locale(value, locale, time_zone, settings=settings)
    
        elif locale is None:
            print(f"Pattern provided; no locale. Use pattern only, value = {value}, pattern: {pattern}")
            # Pattern provided, no locale (use pattern only)
            dt = parse(date_string=value, date_formats=[pattern], settings=settings)
        else:
            print(f"Locale and pattern BOTH given; use both with bulky parse: locale: {locale}, pattern: {pattern}, value: {value}")
            # TODO: Figure bulky parse
            dp_locale = dt_help.locale_reg2dp(locale)
            dt = parse(date_string=value, date_formats=[pattern], locales=[dp_locale], settings=settings)
            if dt is None:
                if "_" in locale:
                    lang, country = locale.split("_")
                    dt = parse(value, date_formats = [pattern], languages = [lang], settings=settings)
                    if dt is None:
                        dt = parse(value, date_formats = [pattern], region=country, settings=settings)
                else:
                    # Try language only
                    dt = parse(value, languages = [dp_locale], settings=settings)
                    if dt is None:
                        # Try country only
                        dt = parse(value, region = dp_locale, settings=settings)
        if dt is None:
            print(f"ABSTRACT.PARSE date FAILED, returning None")
        else:
            print(f"ABSTRACT.PARSE date retruning {dt}")
        return dt


    def __parse_time(self, value:str, pattern:Optional[str]=None, locale:Optional[str]=None, time_zone:Optional[tzinfo]=None, settings=None) -> Optional[object]:
        # parsing time only
        # return 0
        print(f"ABSTRACT: PARSING TIME ONLY")
        def parse_time_locale(value:str, locale:Union[str, Locale] = None, time_zone:tzinfo=None, settings=None) -> object:
            """
            Returns the ``time`` object based on the passed in locale.
            Uses system default if ``None``.
            Only called if there is no pattern.

            Args:
                locale (Union[str, Locale]): The locale to use when parsing; System default if ``None``.
                time_zone (tzinfo): The timezone to parse the object to.

            Returns: 
                The parsed ``time`` object.
            
            Changes from Java:
                This function does not exist in Java. It was created to mimic the logic in our
                ``_get_format()``, since we need the logic but cannot use the function.
                (See documentation for ``_parse()`` for a more detailed explanation.)
            """
            # Only called if we are parsing a time AND pattern is not given
            time_format = self.__int2str_style.get(self.__time_style, 'short')
            if locale is None:
                # Pattern AND locale is None
                # babel.parse_time() keeps parsing date strings as times, but parses time find.
                    # Locale does not do anything
                    # Getting a pattern based on locale...
                # dateparser.parse() keeps parsing date strings as dates, setting time to zero
                    # But parses time strings fine
                    # putting a locale doesn't do anything
                    # Does not really respect formats
                # dateutil.parser.parse() acts like dateparser.parse()
                
                # t = parse_time(string=value, format=time_format)
                # dt = parse(value, settings=settings)
                # TRY STRPTIME
                # can use time_style because no pattern is given here
                try:
                    used_format = dt_help.ldml2strptime(style_format=time_format)
                    dt = datetime.strptime(value, used_format)
                except Exception as e:
                    print(f"INVALID ARGS: {e}")
                    dt = None
                print(f"PARSED TiME no Locale: {dt}")
                return dt
            else:
                # Use provided locale AND initialized style
                try:
                    used_format = dt_help.ldml2strptime(style_format=time_format, locale=locale)
                    dt = datetime.strptime(value, used_format)
                except Exception as e:
                    print(f"INVALID ARGS: {e}")
                    dt = None
                # For now, just return dt
                print(f"PARSED TiME Yes Locale: {dt}")
                return dt
                # used_format = dt_help.ldml2strptime(style_format=time_format, locale=locale)
                # dt = datetime.strptime(value, used_format)
                print(f"STRPTIME Parsing: {dt}")
                if dt is None:
                    dt = dt_help.babel_parse_time(value, locale, pattern, time_zone)
                if dt is None:
                    print(f"Babel parse time failed; try dp.parse()")
                    dp_locale = dt_help.locale_reg2dp(locale)
                    dt = parse(date_string=value, locales=[dp_locale], settings=settings)
                    if dt is None:
                    # TODO: refactor bulky parse
                        if "_" in locale:
                            lang, country = locale.split("_")
                            dt = parse(value, languages = [lang], settings=settings)
                            if dt is None:
                                dt = parse(value, region=country, settings=settings)
                        else:
                            # Try language only
                            dt = parse(value, languages = [dp_locale])
                            if dt is None:
                                # Try country only
                                dt = parse(value, region = dp_locale, settings=settings)
                if dt is None:
                    print(f"ABSTRACT.PARSE_HELPER failed; returning None.")
            # Get the the time component only, and join it with a datetime initialized at epoch
            # t = t.time()
            # dt = datetime(0, 0, 0, tzinfo=None)
            # return datetime.combine(dt, t)

            return dt

        if GenericValidator.is_blank_or_null(pattern):
            # No pattern, use locale only (which may or may not be the default).
            t = parse_time_locale(value, locale, time_zone)
            if t is None:
                return None

        elif locale is None:
            # Pattern provided, no locale (use pattern only)
            t = parse(date_string=value, date_formats=[pattern])
        else:
            # Locale and pattern BOTH given; use both
            print(f"Parsingn time locale and pattern BOTH given; use both with bulky parse: locale: {locale}, pattern: {pattern}, value: {value}")
            # TODO: Figure bulky parse
            dp_locale = dt_help.locale_reg2dp(locale)
            t = parse(date_string=value, date_formats=[pattern], locales=[dp_locale])
            if t is None:
                if "_" in locale:
                    lang, country = locale.split("_")
                    t = parse(value, date_formats = [pattern], languages = [lang])
                    if t is None:
                        t = parse(value, date_formats = [pattern], region=country)
                else:
                    # Try language only
                    t = parse(value, languages = [dp_locale])
                    if t is None:
                        # Try country only
                        t = parse(value, region = dp_locale)
        if t is None:
            print(f"ABSTRACT.PARSE FAILED, returning None")
            return None
        print(f"Parsing time got: {t}")
        # Now change it by setting the year, month, day to the epoch.
        if t.time() == time(0, 0, 0):
            print(f"TIME: parsed a date stirng possibly, dt: {t}, and time: {t.time()}, and value: {value}")
            try:
                parse_time(value)
            except Exception as e:
                print(f"Really was an invalid time string... {e}")
                return None
        epoch_date = date(1970, 1, 1)
        t = datetime.combine(epoch_date, t.time())
        print(f"Parsing time got: Resetting to epoch: Got: {t}")
        return t


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