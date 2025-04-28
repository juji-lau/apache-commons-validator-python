"""
Module Name: test_abstract_calendar.py
Description:
    This file contains:
        The base Calendar Test Case from test.java.org.apache.commons.validator.routines.AbstractCalendarValidatorTest.java
            Link: https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/AbstractCalendarValidatorTest.java
        Additional test cases

Author: Juji Lau

License (Taken from apache.commons.validator.routines.AbstractCalendarValidatorTest):
    Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements.
    See the NOTICE file distributed with this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software distributed under the License is
    distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and limitations under the License.

Changes:
"""
from __future__ import annotations
from typing import Final, Optional, Union
from datetime import date, time, tzinfo, timedelta, timezone, datetime

# from src.main.util.calendar_wrapper import Calendar
from src.main.util.Locale import Locale
from src.main.routines.abstract_calendar_validator import AbstractCalendarValidator

class TestAbstractCalendarValidator:
    """
    Base Calendar Test Case.

    Attributes:
        validator (AbstractCalendar): The concrete implementation of the Time validator to test. (Initialized in concrete classes)
        pattern_valid (list[str]): A list of valid dates in string format with dash ('-') separators to test.
        locale_valid (list[str]): A list of valid dates in string format with slash ('/') separators to test.
        pattern_expect (list[datetime]): TODO: add info
        pattern_invalid (list[str]): A list of invalid dates formated as stirngs with dash ('-') separators.
        locale_invalid (list[str]): A list of invalid dates formated as strings with slash ('/') separators.
    """

    @classmethod
    def _create_calendar(cls, zone:Optional[timezone], date:int, time:int) -> datetime:
        """
        Create a ``datetime`` instance for a specified time zone, date and time.

        Args:
            zone (timezone): The time zone.
            date (int): The date in yyyyMMdd format.
            time (int): The time in HH:mm:ss format.
        
        Returns:
            The new datetime instance.
        """
        # parse the input
        year = date // 10000
        month = (date % 10000) // 100
        day = date % 100
        hour = time // 10000
        min = (time % 10000) // 100
        sec = time % 100

        if zone is None:
            calendar = datetime(year, month, day, hour, min, sec, microsecond=0)
        else:
            calendar = datetime(year, month, day, hour, min, sec, microsecond=0, tzinfo=zone)
        return calendar


    @classmethod
    def _create_date(cls, zone:timezone, date:int, time:int) -> datetime:
        """
        Create a datetime instance for a specified time zone, date and time. 
       
        Note: 
        Since Java's `Date` tracks the time elapsed since the epoch, we return a datetime to incorporate 
        time-information rather than a `date`.

        Args:
            zone (TimeZone): The time zone.
            date (int): The date in yyyyMMdd format.
            time (int): The time in HH:mm:ss format.
        
        Returns:
            The new datetime instance.
        """
        calendar = cls._create_calendar(zone, date, time)
        return calendar
        # return calendar.date()
    
    # Instance level attributes:
    _validator:AbstractCalendarValidator
    
    # Class level attributes:
    _pattern_valid:list[str] = [
        "2005-01-01", 
        "2005-12-31", 
        "2004-02-29",       # valid leap
        "2005-04-30", 
        "05-12-31", 
        "2005-1-1", 
        "05-1-1"
    ]
    _locale_valid:list[str] = [
        "01/01/2005", 
        "12/31/2005",
        "02/29/2004",       # Valid leap
        "04/30/2005", 
        "12/31/05", 
        "1/1/2005",
        "1/1/05"
    ]

    _pattern_expect:list[datetime] = None

    _pattern_invalid:list[str] = [
        "2005-00-01"    # zero month
        "2005-01-00",   # zero day
        "2005-13-03",   # month invalid
        "2005-04-31",   # invalid day
        "2005-03-32",   # invalid day
        "2005-02-29",   # invalid leap
        "200X-01-01",   # invalid char
        "2005-0X-01",   # invalid char
        "2005-01-0X",   # invalid char
        "01/01/2005",   # invalid pattern
        "2005-01",      # invalid pattern
        "2005--01",     # invalid pattern
        "2005-01-"      # invalid pattern
    ]
    _locale_invalid:list[str] = [
        "01/00/2005"    # zero month
        "00/01/2005",   # zero day
        "13/01/2005",   # month invalid
        "04/31/2005",   # invalid day
        "03/32/2005",   # invalid day
        "02/29/2005",   # invalid leap
        "01/01/200X",   # invalid char
        "01/0X/2005",   # invalid char
        "0X/01/2005",   # invalid char
        "01-01-2005",   # invalid pattern
        "01/2005",      # invalid pattern
        # "/01/2005",   # invalid pattern, but passes on some cases in Java
        "01//2005-"     # invalid pattern
    ]

    @property
    def _pattern_expect(cls) -> list[date]:
        """Initializes a list of expected patterns if empty. Then, returns it."""
        if cls._pattern_expect is None:
            cls._pattern_expect = [
                cls._create_date(None, 20050101, 0), 
                cls._create_date(None, 20051231, 0), 
                cls._create_date(None, 20040229, 0),
                cls._create_date(None, 20050430, 0), 
                cls._create_date(None, 20051231, 0),
                cls._create_date(None, 20050101, 0), 
                cls._create_date(None, 20050101, 0)
        ]
        return cls._pattern_expect

    
    def setup_method(self) -> None:
        """ Sets up a calendar, initializing ``self._validator``."""
        pass

    def teardown_method(self) -> None:
        """Clears the calendar."""
        self._validator = None

    def test_format(self) -> None:
        """ 
        Tests ``validator.format()``.
        Actual test cases are moved to the implementing classes.
        """
        pass
        # create a datetime or Calendar.
        # val = self._validator
        # test = self._validator._parse("2005-11-28", "yyyy-MM-dd", None, None)
        # assert test is not None, "Test Date"
        # assert "28.11.05" == self._validator.format(test, "dd.MM.yy"), "Format pattern"
        # assert "11/28/05" == self._validator.format(test, Locale(language="en", country="US")), "Format locale"


    # def test_locale_invalid(self) -> None:
    #     """Tests Invalid Dates with "locale" validation. """
    #     locale = Locale(language="en", country="US")
    #     for i, invalid_locale in enumerate(self._locale_invalid):
    #         text = f"{i} value=[{invalid_locale}] passed "
    #         date = self._validator._parse(invalid_locale, None, locale, None)
    #         assert date is not None, f"validate_obj() {text}{date}"
    #         assert self._validator.is_valid(invalid_locale, locale) is False, f"is_valid() {text}"

        
    # def test_locale_valid(self) -> None:
    #     """ Test Valid Dates with "locale" validation. """
    #     locale = Locale(language="en", country="US")
    #     for i, valid_locale in enumerate(self._locale_valid):
    #         text = f"{i} value=[{valid_locale}] failed "
    #         date = self._validator._parse(valid_locale, None, locale, None)
    #         assert date is not None, f"validate_obj() {text}{date}"
    #         assert self._validator.is_valid(valid_locale, locale) is True, f"is_valid() {text}"
    #         if isinstance(date, datetime):
    #             date = date.date()
    #         assert self._pattern_expect[i] == date, f"compare {text}"


    # def test_pattern_invalid(self) -> None:
    #     """Test Invalid Dates with 'pattern' validation."""
    #     for i, invalid_pattern in enumerate(self._pattern_invalid):
    #         text = f"{i} value=[{invalid_pattern}] pased "
    #         date = self._validator._parse(invalid_pattern, "yy-MM-dd", None, None) 
    #         assert date is None, f"validate_obj() {text} {date}"
    #         assert self._validator.is_valid(invalid_pattern, "yy-MM-dd") is False, f"is_valid() {text}"


    # def test_pattern_valid(self) -> None:
    #     """Test Valid Dates with 'pattern' validation."""
    #     for i, valid_pattern in enumerate(self._pattern_valid):
    #         text = f"{i} value=[{valid_pattern}] failed "
    #         date = self._validator._parse(valid_pattern, "yy-MM-dd", None, None) 
    #         assert date is not None, f"validate_obj() {text} {date}"
    #         assert self._validator.is_valid(valid_pattern, "yy-MM-dd") is True, f"is_valid() {text}"
    #         if isinstance(date, datetime):
    #             date = date.date()
    #         assert self._pattern_expect[i] == date, f"compare {text}"
    

    def test_serialization(self) -> None:
        """ Test validator serialization"""
        pass