"""
Module Name: test_time_validator.py
Description:
    This file contains:
        Test cases from test.java.org.apache.commons.validator.routines.TimeValidatorTest.java
            Link: https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/TimeValidatorTest.java
        Additional test cases

Author: Juji Lau

License (Taken from apache.commons.validator.routines.TimeValidatorTest):
    Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements.
    See the NOTICE file distributed with this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software distributed under the License is
    distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and limitations under the License.

Changes:
    - Moved specific tests from TestAbstractCalendarValidator into this file (to avoid initialization errors)
    - Separated test_compare() into different test functions for better readability.
    - Moveed ``_create_date()`` and ``_create_time()`` functions into the module level so they can be called anywhere whithin the TestTimeValidator class.
    - Moved variables commonly used across multiple functions into the class (as class attributes) to improve readablility, and making it possible to leverage Pytest's ``@parameterize`` feature.
    - Hardcoded several test cases (instead of using language libraries to derive it) 
        for readability, simplicity, and because Python does not have a ``DateFormat`` equivalent.
    - set the locale system default locale in the ``setup()`` method and reset it to the original locale in the ``teardown()`` method
        most functions use the locale "en_GB" to test the system defaults. I did this to match.
    - TODO: check this: Moved commonly used values and objects into fixtures to leverage Pytest functionality.
    
    - Added a new property: `test_calendars(cls) -> dict[datetime] that 
        creates a bunch of datetime objects to be reused over the next few tests.
        This property not in Java's implementation, and was added purely for readability purposes.
"""
from __future__ import annotations

import pytest
from datetime import datetime, tzinfo
from dateutil.tz import gettz
from typing import Optional, Final, Callable
from src.main.routines.time_validator import TimeValidator
from src.main.util.datetime_helpers import J2PyLocale, locale_reg2dp, date_get_time, debug
from src.test.routines.test_abstract_calendar_validator import TestAbstractCalendarValidator
from src.test.util.test_timezones import TestTimeZones
# from icu import Locale, LocaleMatcher, Collator, ICUError
import locale

# Set the default ICU locale for your process
original_locale = locale.setlocale(locale.LC_ALL, None)

    # @classmethod
def _create_time(zone:tzinfo, time:int, millisecond:int) -> datetime:
    """
    Create a datetime instance for a specified time zone, date and time. 

    Args:
        zone (tzinfo): The time zone.
        dt_time (int): The time in HH:mm:ss format.
        millisecond (int): The milliseconds passed since the epoch.
    
    Returns:
        The new datetime instance.
    """
    # parse the input
    hour = time // 10000
    min = (time % 10000) // 100
    sec = time % 100
    microsecond = millisecond * 1000    # Java Calendars store milliseconds. Python datetimes store microseconds.
    # Define the date (epoch)
    year = 1970
    month = 1       # Python months are 1-indexed; Java's months are 0-indexed.
    day = 1

    calendar = datetime(year, month, day, hour=hour, minute=min, second=sec, microsecond = microsecond, tzinfo=zone)
    if zone is None:        # Ensure it's naive if tzinfo is none
        assert_msg = f"This datettime: {calendar} is aware when it should be naive."
        assert (calendar.tzinfo is None or calendar.tzinfo.utcoffset(calendar) is None), assert_msg
    return calendar


def _create_date(zone:tzinfo, time:int, millisecond:int) -> datetime:
    """
    Create a datetime instance for a specified time zone, date and time. 

    Args:
        zone (tzinfo): The time zone.
        dt_time (int): The time in HH:mm:ss format.
        millisecond (int): The milliseconds passed since the epoch.
    
    Returns:
        The new datetime instance.
    
    Changes from Java:
        Since Java's `Date` tracks the time elapsed since the epoch.
        Python's ``datetime.date`` does not track any unit of time less than a day.
        To match the functionality in Java's Validator, we return a datetime to incorporate time-information.      
    """
    calendar = _create_time(zone, time, millisecond)
    return calendar


class TestTimeValidator(TestAbstractCalendarValidator):
    """
    Test suite for TimeValidator.

    Inherits from TestAbstractCalendarValidator to run base validation tests.

    Attributes (Additional from base class):
        time_validator (TimeValidator): The TimeValidator test case.
    """  

    #  Class level attributes:
    _pattern_valid:list[str] = [
        "23-59-59", 
        "00-00-00", 
        "00-00-01", 
        "0-0-0", 
        "1-12-1", 
        "10-49-18", 
        "16-23-46"
    ]
   
    _pattern_expect:list[datetime] = [
        _create_date(None, 235959, 0), 
        _create_date(None, 0, 0), 
        _create_date(None, 1, 0), 
        _create_date(None, 0, 0), 
        _create_date(None, 11201, 0), 
        _create_date(None, 104918, 0), 
        _create_date(None, 162346, 0)
    ]

    _locale_valid:list[str] = [
        "23:59", 
        "00:00", 
        "00:01", 
        "0:0", 
        "1:12", 
        "10:49", 
        "16:23"
    ]

    _locale_expect:list[datetime] = [
        _create_date(None, 235900, 0),
        _create_date(None, 0, 0), 
        _create_date(None, 100, 0), 
        _create_date(None, 0, 0),
        _create_date(None, 11200, 0), 
        _create_date(None, 104900, 0),
        _create_date(None, 162300, 0)
    ]

    _pattern_invalid:list[str] = [
        "24-00-00",     # midnight,
        "24-00-01",     # past midnight
        "25-02-03",     # invalid hour
        "10-61-31",     # invalid minute
        "10-01-61",     # invalid second
        "05:02-29",     # invalid sep
        "0X-01:01",     # invalid sep
        "05-0X-01",     # invalid char
        "10-01-0X",     # invalid char
        "01:01:05",     # invalid pattern
        "10-10",        # invalid pattern
        "10--10",       # invalid pattern
        "10-10-"        # invalid pattern
    ]

    _locale_invalid:list[str] = [
       "24:00",     # midnight
        "24:00",    # past midnight
        "25:02",    # invalid hour
        "10:61",    # invalid minute
        "05-02",    # invalid sep
        "0X:01",    # invalid sep
        "05:0X",    # invalid char
        "01-01",    # invalid pattern
        "10:",      # invalid pattern
        "10::1",    # invalid pattern
        "10:1:"     # invalid pattern
    ]
 

    def setup_method(self):
        # self.__time_validator:TimeValidator = TimeValidator()
        print(f"CREATING TINME SETUP")
        try:
            locale.setlocale(locale.LC_ALL, 'en_GB')
        except Exception as e:
            print(f"FAILED TO SET LOCALE TO en_GB; original: {original_locale}")
        self._validator = TimeValidator()
    
    def teardown_method(self) -> None:
        super().teardown_method()
        locale.setlocale(locale.LC_ALL, original_locale)
    
    # Test Compare methods:
    
    # Constants
    tz_gmt:tzinfo = gettz("GMT")
    # locale_GB:str = 'en_GB'     # The default locale in this test file
    test_time:Final[int] = 154523
    min:Final[int] = 100
    hour:Final[int] = 10000
    # Various datetimes for compare testing
    value = _create_time(tz_gmt, test_time, 400)

    milliGreater = _create_time(tz_gmt, test_time, 500)     # > milli sec
    milliLess = _create_time(tz_gmt, test_time, 300)     # < milli sec

    secGreater = _create_time(tz_gmt, test_time + 1, 100)     # +1 sec
    secLess = _create_time(tz_gmt, test_time - 1, 100)     # -1 sec

    minGreater = _create_time(tz_gmt, test_time + min, 100)     # +1 min
    minLess = _create_time(tz_gmt, test_time - min, 100)     # -1 min

    hourGreater = _create_time(tz_gmt, test_time + hour, 100)     # +1 hour
    hourLess = _create_time(tz_gmt, test_time - hour, 100)     # -1 hour
    
    # Compare time (hours, minutes, seconds, microseconds)
    @pytest.mark.parametrize (
        "compare_dt, expected_output, assert_msg", [
            (milliGreater, -1, "milli LT"),     # > milli
            (value, 0, "mili EQ"),              # same time
            (milliLess, 1, "milli GT")          # < milli
        ]
    )
    def test_compare_time(self, compare_dt:datetime, expected_output:int, assert_msg:str) -> None:
        """ Tests the ``TimeValidator.compare_time()`` method."""
        assert self._validator.compare_time(self.value, compare_dt) == expected_output, assert_msg


    # Compare seconds (hours, minutes, seconds)
    @pytest.mark.parametrize (
        "compare_dt, expected_output, assert_msg", [
            (secGreater, -1, "secs LT"),    # +1 sec
            (milliGreater, 0, "secs = 1"),  # > milli
            (value, 0, "secs = 2"),         # same time
            (milliLess, 0, "secs = 3"),     # < milli
            (secLess, 1, "secs GT"),        # -1 sec
        ]
    )
    def test_compare_seconds(self, compare_dt:datetime, expected_output:int, assert_msg:str) -> None:
        """ Tests the ``TimeValidator.compare_seconds()`` method."""
        assert self._validator.compare_seconds(self.value, compare_dt) == expected_output, assert_msg


    # Compare minutes (hours, minutes)
    @pytest.mark.parametrize (
        "compare_dt, expected_output, assert_msg", [
            (minGreater, -1, "mins LT"),    # +1 min
            (secGreater, 0, "mins = 1"),    # +1 sec
            (value, 0, "mins = 2"),         # same time
            (secLess, 0, "mins = 3"),       # -1 sec
            (minLess, 1, "mins GT")        # -1 min
        ]
    )
    def test_compare_minutes(self, compare_dt:datetime, expected_output:int, assert_msg:str) -> None:
        """ Tests the ``TimeValidator.compare_minutes()`` method."""
        assert self._validator.compare_minutes(self.value, compare_dt) == expected_output, assert_msg


    # Compare hours
    @pytest.mark.parametrize (
        "compare_dt, expected_output, assert_msg", [
            (hourGreater, -1,"hour LT"),    # +1 hour
            (minGreater, 0, "hour = 1"),    # +1 min
            (value, 0, "hour = 2"),         # same time
            (minLess, 0, "hour = 3"),       # -1 min
            (hourLess, 1, "hour GT"),       # -1 hour
        ]
    )
    def test_compare_hours(self, compare_dt:datetime, expected_output:int, assert_msg:str) -> None:
        """ Tests the ``TimeValidator.compare_hours()`` method."""
        assert self._validator.compare_hours(self.value, compare_dt) == expected_output, assert_msg
    

    # Test validation methods: (format(), is_valid(), validate()):

    # Constants
    val = "4:49 PM"
    val_us = "4:49 PM"
    locale = 'en_GB'
    val_gb = "16:49"


    @pytest.mark.parametrize (
        "expected_str, input_pattern, input_locale, assert_msg", [
            ("16-49-23", "HH-mm-ss", None, "Format pattern"),
            (val_us, None, J2PyLocale.US, "Format locale"),
            (val, None, None, "Format default"),
            (val_gb, None, locale, "Format great Britain")
        ]
    )
    def test_format(self, expected_str:str, input_pattern:str, input_locale:str, assert_msg:str) -> None:
        """ Test Invalid dates with "locale" validation."""
        # The JVM format varies; calculate expected results.
        test = TimeValidator.get_instance().validate(value="16:49:23", pattern="HH:mm:ss", locale='en-GB', time_zone=None)
        assert test is not None, "Test Date"
        assert expected_str == self._validator.format(value=test, pattern=input_pattern, locale=input_locale), assert_msg

    def test_locale_invalid(self) -> None:
        """ Test invalid dates with ``Locale`` validation. """
        for i, invalid_locale in enumerate(self._locale_invalid):
            text = f"{i} value=[{invalid_locale}] passed "
            date = self._validator.validate(value=invalid_locale, locale=J2PyLocale.US)
            print(f"Created date: {date} from string: {invalid_locale}")
            assert date is None, f"validate() {text}"
            assert self._validator.is_valid(value=invalid_locale,locale=J2PyLocale.UK) == False, f"is_valid() {text}"
    
    # def test_locale_valid( self) -> None:
    #     """ Test invalid dates with ``Locale`` validation. """
    #     for i, valid_locale in enumerate(self._locale_valid):
    #         text = f"{i} value=[{valid_locale}] failed "
    #         dt = self._validator.validate(valid_locale, J2PyLocale.UK)
    #         assert dt is not None, f"validate() {text}"
    #         assert self._validator.is_valid(valid_locale, J2PyLocale.UK) == True, f"is_valid() {text}"
    #         assert date_get_time(self._locale_expect[i]) == date_get_time(dt), f"FAILED: {debug(self._locale_expect[i], dt)}"
    #         # assert date_get_time(self._locale_expect[i]) == date_get_time(dt), f"compare {text}"

    # def test_pattern_invalid(self) -> None:
    #     """ Test Invalid dates with "pattern" validation."""
    #     pass
    # from babel.dates import parse_time

    # def test_pattern_valid (self) -> None:
    #     """Test valid dates with "pattern" validation. """
    #     pass
    

    def test_timezone_default(self) -> None:
        """Test timezone functionality using default timezone, locale of british, and pattern."""
        # result:datetime = self._validator.validate(value="18:01", time_zone = self.tz_gmt)
        result:datetime = self._validator.validate(value="18:01", locale='en_GB')

        assert result is not None, "Default result"
        # assert TimeZones.GMT == result.getTimeZone(), "default zone"
        assert 18 == result.hour, "default hour"
        assert 1 == result.minute, "zone minute"
        # assert None == result.tzinfo
        assert False == True, f"TZ info: {result.tzinfo}, result: {result}"
    

    # def test_timezone_est(self) -> None:
    #     """ Test time timezone functionality using est timezone, and default loacale and pattern."""
    #     result:datetime = self._validator.validate(value = "16:49", time_zone = TestTimeZones.EST)
    #     assert result is not None, "Default result"
    #     assert TestTimeZones.EST == result.tzinfo, "zone zone"
    #     assert 16 == result.hour, "zone hour"
    #     assert 49 == result.minute, "zone minute"
    
    
    # def test_timezone_est_pattern(self) -> None:
    #     """ Test timezone functionality using est timezone, default locale, and a custom pattern."""
    #     result:datetime = self._validator.validate(value = "14-34", pattern = "HH-mm", time_zone = TestTimeZones.EST)
    #     assert result is not None, "pattern result"
    #     assert TestTimeZones.EST == result.tzinfo, "pattern zone"
    #     assert 14 == result.hour, "zone hour"
    #     assert 34 == result.minute, "zone minute"


    # def test_timezone_est_locale(self) -> None:
    #     """Test timezone functionality using est timezone, custom locale, and a default pattern."""
    #     # us_cal = datetime(2005, 1, 1, hour=19, minute=18, tzinfo="en_US")        # Python months are 1 based
    #     us_val = "7:18 PM"
    #     result:datetime = self._validator.validate(value = us_val, locale = J2PyLocale.US, time_zone = TestTimeZones.EST)
    #     assert result is not None, f"locale result: {us_val}"
    #     assert TestTimeZones.EST == result.tzinfo, f"locale zone: {us_val}"
    #     assert 19 == result.hour, f"locale hour: {us_val}"
    #     assert 18 == result.minute, f"locale minute: {us_val}"

    
    # def test_timezone_est_pattern_locale(self) -> None:
    #     """ Test timezone functionality using est timezone, and a custom locale and pattern."""
    #     dt_pattern = "dd/MMM/yy HH-mm"
    #     # de_cal = datetime(2005, 11, 31, hour=21, minute=5, locale = J2PyLocale.GERMAN)          # Python months are 1 based
    #     german_sample = "31/Dez./05 21-05"
    #     result:datetime = self._validator.validate(value = german_sample, pattern = dt_pattern, locale = J2PyLocale.GERMAN, time_zone = TestTimeZones.EST)
    #     assert result is not None, f"pattern result: {german_sample}"
    #     assert TestTimeZones.EST == result.tzinfo, "pattern zone"
    #     assert 2005 == result.year, "pattern day"
    #     assert 12 == result.month, "pattern day"        # Java months are (0-11); Python's months are (1-12)
    #     assert 31 == result.day, "pattern day"
    #     assert 21 == result.hour, "pattern hour"
    #     assert 5 == result.minute, "pattern minute"
    #     result = None


    # def test_timezone_pattern_locale(self) -> None:
    #     """Test timezone functionality using default timezone, and a custom locale and pattern."""
    #     dt_pattern = "dd/MMM/yy HH-mm"
    #     german_sample = "31/Dez./05 21-05"
    #     result:datetime = self._validator.validate(value = german_sample, pattern = dt_pattern, locale = J2PyLocale.GERMAN)
    #     assert result is not None, f"Pattern result: {german_sample}"
    #     assert self.tz_gmt == result.tzinfo, "pattern zone"
    #     assert 2005 == result.year, "pattern day"
    #     assert 12 == result.month, "pattern day"        # Java months are (0-11); Python's months are (1-12)
    #     assert 31 == result.day, "pattern day"
    #     assert 21 == result.hour, "pattern hour"
    #     assert 5 == result.minute, "pattern minute"
    #     result = None

    
    # @pytest.fixture
    # def expected_zone(self, zone) -> datetime:
    #     """Datetime with a different tzinfo that the system default."""
    #     return self._create_calendar(zone=zone, date=20051231, time=0)

    # locale = J2PyLocale.GERMAN
    # pattern = "yyyy-MM-dd"
    # patternVal = "2005-12-31"
    # germanPattern = "dd MMM yyyy"
    
    # # 
    # germanVal = "31 Dez. 2005"


    # localeVal = "31.12.2005"
    # defaultVal = "12/31/05"
    # xxxx = "XXXX"
    # default_locale = "en_US"

    # @pytest.mark.parametrize (
    #     "assert_type, input_val, input_pattern, input_locale, assert_msg", [
    #         ("dt", defaultVal, None, default_locale, "validate(A) default"),
    #         ("dt", localeVal, None, locale, "validate(A) locale "),
    #         ("dt", patternVal, pattern, default_locale, "validate(A) pattern "),
    #         ("dt", germanVal, germanPattern, J2PyLocale.GERMAN, "validate(A) both"),
    #         (None, xxxx, None, default_locale, "validate(B) default"),
    #         (None, xxxx, None, locale, "validate(B) locale "),
    #         (None, xxxx, pattern, default_locale, "validate(B) pattern"),
    #         (None, "31 Dec 2005", germanPattern, J2PyLocale.GERMAN, "validate(B) both")
    #     ]
    # )
    # def test_validate(self, assert_type:Optional[str], expected_dt:datetime, input_val:str, input_pattern:str, input_locale:str, assert_msg:str) -> None:
    #     """
    #     Test `DateValidator.validate()`method.  
    #     # Also includes test cases in `test`AbstractCalendarValidatorTest.java`.
    #     """
    #     # Don't rely on specific German format - it varies between JVMs
    #     output_dt = DateValidator.get_instance().validate(value=input_val, pattern=input_pattern, locale=input_locale)
    #     if assert_type == "dt":
    #         assert expected_dt.date() == output_dt.date(), assert_msg
    #     else:
    #         assert output_dt is None, assert_msg

    # @pytest.mark.parametrize (
    #     "input_val, input_pattern, input_locale, assert_msg", [
    #         (defaultVal, None, default_locale,  "validate(C) default"),
    #         (localeVal, None, locale, "validate(C) locale "),
    #         (patternVal, pattern, default_locale, "validate(C) pattern "),
    #         (germanVal, germanPattern, J2PyLocale.GERMAN, "validate(C) both"),  
    #     ]
    # )
    # def test_validate_timezone(self, expected_dt:datetime, expected_zone:datetime, zone:tzinfo, input_val, input_pattern:str, input_locale, assert_msg:str) -> None:
    #     """
    #     Test `DateValidator.is_valid()`method with a different timezone.  
    #     # Also includes test cases in `test`AbstractCalendarValidatorTest.java`.
    #     """
    #     # Want to check the timezone differences; can't use .time() because that's time-zone naive. 
    #     # Can't use .date() because that's in-sensitive to hours.
    #     assert expected_dt.tzinfo != expected_zone.tzinfo, f"default/EET same {zone}"
    #     assert expected_zone.date() == DateValidator.get_instance().validate(value=input_val, pattern=input_pattern, locale=input_locale, time_zone=zone).date(), assert_msg

    # @pytest.mark.parametrize (
    #     "assert_type, input_val, input_pattern, input_locale, assert_msg", [
    #         # True
    #         (True, defaultVal, None, default_locale, "isValid(A) default"),
    #         (True, localeVal, None, locale, "isValid(A) locale "),
    #         (True, patternVal, pattern, default_locale, "isValid(A) pattern "),
    #         (True, germanVal, germanPattern, J2PyLocale.GERMAN, "isValid(A) both"),
    #         # False
    #         (False, xxxx, None, default_locale, "is_valid(B) default"),
    #         (False, xxxx, None, locale, "is_valid(B) locale "),
    #         (False, xxxx, pattern, default_locale, "is_valid(B) pattern"),
    #         (False, "31 Dec 2005", germanPattern, J2PyLocale.GERMAN, "is_valid(B) both")
    #     ]
    # )
    # def test_is_valid(self, assert_type:bool, input_val:str, input_pattern:str, input_locale:str, assert_msg:str) -> None:
    #     """
    #     Test `CalendarValidator.is_valid()`method.  
    #     # Also includes test cases in `test`AbstractCalendarValidatorTest.java`.
    #     """
    #     assert assert_type == DateValidator.get_instance().is_valid(value=input_val, pattern=input_pattern, locale=input_locale), assert_msg