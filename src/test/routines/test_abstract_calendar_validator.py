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
from src.main.util.datetime_helpers import get_default_tzinfo, JavaToPyLocale
from src.main.routines.abstract_calendar_validator import AbstractCalendarValidator
import locale

# Set the default ICU locale for the process
original_locale = locale.setlocale(locale.LC_ALL, None)

def _create_calendar(zone:Optional[timezone], date:int, time:int) -> datetime:
    """
    Create a ``datetime`` instance for a specified time zone, date and time.

    Args:
        zone (timezone): The time zone. Use system default if ``None``.
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
        # Get default tzinfo
        calendar = datetime(year, month, day, hour, min, sec, microsecond=0)
    else:
        calendar = datetime(year, month, day, hour, min, sec, microsecond=0, tzinfo=zone)
    return calendar


def _create_date(zone:tzinfo, date:int, time:int) -> datetime:
    """
    Create a datetime instance for a specified time zone, date and time. 

    Args:
        zone (tzinfo): The time zone.
        date (int): The date in yyyyMMdd format.
        time (int): The time in HH:mm:ss format.
    
    Returns:
        The new datetime instance.
    
    Changes from Java:
        Since Java's `Date` tracks the time elapsed since the epoch.
        Python's ``datetime.date`` does not track any unit of time less than a day.
        To match the functionality in Java's Validator, we return a datetime to incorporate time-information.
    """
    calendar = _create_calendar(zone, date, time)
    return calendar


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
    _pattern_expect:list[datetime] = [
       _create_date(None, 20050101, 0), 
       _create_date(None, 20051231, 0), 
       _create_date(None, 20040229, 0),
       _create_date(None, 20050430, 0), 
       _create_date(None, 20051231, 0),
       _create_date(None, 20050101, 0), 
       _create_date(None, 20050101, 0)
    ]
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

    @classmethod
    def _create_calendar(self, zone:Optional[timezone], date:int, time:int) -> datetime:
        """
        Calls module function so implementing classes can use it.
        Create a ``datetime`` instance for a specified time zone, date and time.

        """
        return _create_calendar(zone, date, time)
    

    @classmethod
    def _create_date(self, zone:tzinfo, date:int, time:int) -> datetime:
        """
        Calls module function so implementing classes can use it.
        Create a datetime instance for a specified time zone, date and time. 

        """
        return _create_date(zone, date, time)

    
    def setup_method(self) -> None:
        """ Sets up a calendar, initializing ``self._validator``."""
        pass

    def teardown_method(self) -> None:
        """Clears the calendar."""
        print(f"Calling teardown: abstract")
        self._validator = None


    # -------- Tests moved to implementing test classes ----------:

    def test_format(self) -> None:
        """ 
        Tests ``validator.format()``.
        Actual test cases are moved to the applicable implementing test class(es): 
            ``test_date_validator.py``.
        """
        pass


    def test_locale_invalid(self) -> None:
        """
        Test Invalid datetime strings with "locale" validation. 
        
        Actual test cases are moved to the applicable implementing test class(es): 
            ``test_calendar_validator.py``
            ``test_date_validator.py``.
        """
        pass

        
    def test_locale_valid(self) -> None:
        """ 
        Test Valid datetime strings with "locale" validation.

        Actual test cases are moved to the applicable implementing test class(es): 
            ``test_calendar_validator.py``
            ``test_date_validator.py``.
        """
        pass


    def test_pattern_invalid(self) -> None:
        """
        Test Invalid datetime strings with "pattern" validation.

        Actual test cases are moved to the applicable implementing test class(es): 
            ``test_calendar_validator.py``
            ``test_date_validator.py``.
        """
        pass


    def test_pattern_valid(self) -> None:
        """ 
        Test Valid datetime strings with "pattern" validation.

        Actual test cases are moved to the applicable implementing test class(es): 
            ``test_calendar_validator.py``
            ``test_date_validator.py``.
        """
        pass


    def test_serialization(self) -> None:
        """ Test validator serialization (We did not implement serialization."""
        pass