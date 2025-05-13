""" 
Module Name: test_calendar_validator.py
Description:
    This file tests the implementation of CalendarValidator using AbstractCalendarValidator.  
    This file contains:
        Test cases from: 
            test.java.org.apache.commons.validator.routines.CalendarValidatorTest.java
            (https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/CalendarValidatorTest.java#L147)
        Additional test cases
Author: Juji Lau
License (Taken from apache.commons.validator.routines.CalendarValidatorTest.java):
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
    - Moved specific tests from TestAbstractCalendarValidator into this file (to avoid initialization errors)
    - Hardcoded several test cases (instead of using language libraries to derive it) 
        for readability, simplicity, and because Python does not have a ``DateFormat`` equivalent.
    - Moved commonly used values and objects into fixtures to leverage Pytest functionality.
"""
import pytest
from datetime import tzinfo, datetime
from typing import Final, Optional
from zoneinfo import ZoneInfo

from src.apache_commons_validator_python.util.datetime_helpers import (
    JavaToPyLocale, 
    date_get_time, 
    timezone_has_same_rules, 
    obj_to_str, 
    get_default_tzinfo
)
from src.apache_commons_validator_python.routines.abstract_calendar_validator import AbstractCalendarValidator
from src.apache_commons_validator_python.routines.calendar_validator import CalendarValidator
from src.test.routines.test_abstract_calendar_validator import TestAbstractCalendarValidator
from src.test.util.test_timezones import TestTimeZones


class TestCalendarValidator(TestAbstractCalendarValidator):
    """
    Test Case for CalendarValidator.

    Attributes (Additional):
        cal_validator (CalendarValidator): The CalendarValidator test case.
    
    Constants:
        DATE_2005_11_23 (int): 
        TIME_12_03_45 (int):
    """
    __DATE_2005_11_23:Final[int] = 20051123
    __TIME_12_03_45:Final[int] = 120345

    def setup_method(self) -> None:
        """ Sets up the calendar validator."""
        self.__cal_validator:CalendarValidator = CalendarValidator()
        self._validator = self.__cal_validator
    
    @property
    def cal_validator(self):
        """ Returns this instance's cal_validator."""
        return self.__cal_validator


    def test_adjust_to_time_zone(self) -> None:
        """Test ``adjust_to_time_zone()`` method."""
        # Initialize calendars and times
        cal_est = TestAbstractCalendarValidator._create_calendar(TestTimeZones.EST, self.__DATE_2005_11_23, self.__TIME_12_03_45)
        date_est = date_get_time(cal_est)   # Represented by epoch time under the hood
        cal_gmt = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), self.__DATE_2005_11_23, self.__TIME_12_03_45)
        date_gmt = date_get_time(cal_gmt)   # Represented by epoch time under the hood
        cal_cet = TestAbstractCalendarValidator._create_calendar(TestTimeZones.EET, self.__DATE_2005_11_23, self.__TIME_12_03_45)
        date_cet = date_get_time(cal_cet)   # Represented by epoch time under the hood

        # Check the time offsets don't match
        assert date_get_time(cal_gmt) != date_get_time(cal_cet), f"Check GMT != CET"
        assert date_get_time(cal_gmt) != date_get_time(cal_est), f"Check GMT != EST"
        assert date_get_time(cal_cet) != date_get_time(cal_est), f"Check CET != EST"
         
        # EST to GMT and back
        cal_est = CalendarValidator.adjust_to_time_zone(cal_est, ZoneInfo("Etc/GMT"))
        assert date_gmt == date_get_time(cal_est), "EST to GMT"
        assert date_est != date_get_time(cal_est), "Check EST timezone change"
        cal_est = CalendarValidator.adjust_to_time_zone(cal_est, TestTimeZones.EST)
        assert date_est == date_get_time(cal_est), "back to EST"
        assert date_gmt != date_get_time(cal_est), "Check EST != GMT" 

        # CET to GMT and back
        cal_cet = CalendarValidator.adjust_to_time_zone(cal_cet, ZoneInfo("Etc/GMT"))
        assert date_gmt == date_get_time(cal_cet), "CET to GMT"
        assert date_cet != date_get_time(cal_cet), "Check CET timeone change"
        cal_cet = CalendarValidator.adjust_to_time_zone(cal_cet, TestTimeZones.EET)
        assert date_cet == date_get_time(cal_cet), "back to CET"
        assert date_gmt != date_get_time(cal_cet), "Check CET != GMT"

        # Adjust to TimeZone with Same rules
        cal_utc = TestAbstractCalendarValidator._create_calendar(TestTimeZones.UTC, self.__DATE_2005_11_23, self.__TIME_12_03_45)
        assert timezone_has_same_rules(cal_utc, ZoneInfo("Etc/GMT")), "SAME: UTC = GMT"
        # assert TestTimeZones.GMT == timezone.utc, "SAME: UTC = GMT"
        assert date_get_time(cal_utc) == date_get_time(cal_gmt), "SAME: Check time (A)"
        assert ZoneInfo("Etc/GMT") != cal_utc.tzinfo, "SAME: Check GMT(A)"
        assert TestTimeZones.UTC == cal_utc.tzinfo, "SAME: Check UTC(A)"
        
        cal_utc = CalendarValidator.adjust_to_time_zone(cal_utc, ZoneInfo("Etc/GMT"))
        assert date_get_time(cal_utc) == date_get_time(cal_gmt), "SAME: Check time (B)"
        assert ZoneInfo("Etc/GMT") == cal_utc.tzinfo, "SAME: Check GMT(B)"
        assert TestTimeZones.UTC != cal_utc.tzinfo, "SAME: Check UTC(B)"

    # Prepare variables for the tests of validation Methods.
    @pytest.fixture
    def expected_dt(self) -> datetime:
        """Standard datetime with system default locale and local timezone."""
        tz_local = get_default_tzinfo()
        return self._create_calendar(tz_local, 20051231, 0)
    
    @pytest.fixture
    def zone(self) -> tzinfo:
        """Different tzinfo from the system default."""
        local_offset = datetime.now().astimezone().utcoffset()
        if local_offset == TestTimeZones.EET.utcoffset(None):
            return TestTimeZones.EST
        return TestTimeZones.EET
    
    @pytest.fixture
    def expected_zone(self, zone) -> datetime:
        """Datetime with a different tzinfo that the system default."""
        return self._create_calendar(zone=zone, date=20051231, time=0)
    
    locale = JavaToPyLocale.GERMAN
    pattern = "yyyy-MM-dd"
    patternVal = "2005-12-31"
    germanPattern = "dd MMM yyyy"
    germanVal = "31 Dez. 2005"
    localeValShort = "31.12.05"
    localeValJava = "31.12.2005"        # German default short is actually dd.MM.yy
    defaultVal = "12/31/05"
    xxxx = "XXXX"
    default_locale = "en_US"

    @pytest.mark.parametrize (
        "assert_type, input_val, input_pattern, input_locale, assert_msg", [
            ("dt", defaultVal, None, default_locale, "validate(A) default"),
            ("dt", defaultVal, None, None, "validate(A) default, (en_US) "),    # Added test case, truly passing in no locale  
            ("dt", localeValShort, None, locale, "validate(A) locale "),   
            ("dt", localeValJava, None, locale, "validate(A) locale "),   
            ("dt", patternVal, pattern, default_locale, "validate(A) pattern "),
            ("dt", patternVal, pattern, None, "validate(A) pattern, no locale "), # Added test case, truly passing in no locale
            ("dt", germanVal, germanPattern, JavaToPyLocale.GERMAN, "validate(A) both"),
            
            (None, xxxx, None, default_locale, "validate(B) default"),
            (None, xxxx, None, None, "validate(B) default, no locale "),        # Added test case; truly passing in no locale
            (None, xxxx, None, locale, "validate(B) locale "),
            (None, xxxx, pattern, default_locale, "validate(B) pattern"),
            (None, xxxx, pattern, None, "validate(B) pattern, no locale "),     # Added test case; truly passing in no locale
            (None, "31 Dec 2005", germanPattern, JavaToPyLocale.GERMAN, "validate(B) both")
        ]
    )
    def test_validate(self, assert_type:Optional[str], expected_dt:datetime, input_val:str, input_pattern:str, input_locale:str, assert_msg:str) -> None:
        """
        Test `CalendarValidator.validate()` method.  
        # Also includes test cases in `test`AbstractCalendarValidatorTest.java`.
        """
        output_dt = CalendarValidator.get_instance().validate(value=input_val, pattern=input_pattern, locale=input_locale)
        if assert_type == "dt":
            assert output_dt is not None, f"Could not create a datetime for {assert_msg}"
            assert date_get_time(expected_dt) == date_get_time(output_dt), assert_msg
        else:
            assert output_dt is None, assert_msg

    
    @pytest.mark.parametrize (
        "input_val, input_pattern, input_locale, assert_msg", [
            (defaultVal, None, default_locale,  "validate(C) default"),
            (defaultVal, None, None,  "validate(C) default, no locale "),   # Added test case, truly passing in no locale
            (localeValShort, None, locale, "validate(C) locale "),
            (localeValJava, None, locale, "validate(C) locale "),   
            (patternVal, pattern, default_locale, "validate(C) pattern "),
            (patternVal, pattern, None, "validate(C) pattern, no locale "),   # Added test case, truly passing in no locale
            (germanVal, germanPattern, JavaToPyLocale.GERMAN, "validate(C) both"),  
        ]
    )
    def test_validate_timezone(self, expected_dt:datetime, expected_zone:datetime, zone:tzinfo, input_val, input_pattern:str, input_locale, assert_msg:str) -> None:
        """
        Test `CalendarValidator.is_valid()`method with a different timezone.  
        # Also includes test cases in `test`AbstractCalendarValidatorTest.java`.

        expected_zone: a different dt timezone from system default
        """
        # Ensure our system default datetime (expected_dt) is different from our testing datetime (expected_zone).
        assert expected_dt.tzinfo != expected_zone.tzinfo, "default/EET same"
        assert expected_zone.tzinfo == zone, "Incorrectly initialized test datetime"
        assert date_get_time(expected_zone) != date_get_time(expected_dt), f"The zone datetime represents the same time as default: {obj_to_str(expected_zone, expected_dt)}"
        
        # Time offsets from running java
        assert 1136005200000 == date_get_time(expected_dt), f"Verify correct time representation, default: {obj_to_str(1136005200000, expected_dt)}"
        assert 1135980000000 == date_get_time(expected_zone), f"Verify correct time representation, zone: {obj_to_str(1135980000000, expected_dt)}"

        # Actual tests:
        created_dt = CalendarValidator.get_instance().validate(value=input_val, pattern=input_pattern, locale=input_locale, time_zone=zone)
        assert date_get_time(expected_zone) == date_get_time(created_dt), obj_to_str(expected_zone, created_dt)


    @pytest.mark.parametrize (
        "assert_type, input_val, input_pattern, input_locale, assert_msg", [
            (True, defaultVal, None, default_locale, "isValid(A) default"),
            (True, defaultVal, None,  None, "isValid(A) default, no locale "),   # Added test case, truly passing in no locale
            (True, localeValShort, None, locale, "isValid(A) locale "),
            (True, localeValJava, None, locale, "isValid(A) locale "),
            (True, patternVal, pattern, default_locale, "isValid(A) pattern "),
            (True, patternVal, pattern,  None, "isValid(A) pattern, no locale "),   # Added test case, truly passing in no locale
            (True, germanVal, germanPattern, JavaToPyLocale.GERMAN, "isValid(A) both"),
            
            (False, xxxx, None, default_locale, "is_valid(B) default"),
            (False, xxxx, None, None, "is_valid(B) default, no locale "),   # Added test case, truly passing in no locale
            (False, xxxx, None, locale, "is_valid(B) locale "),
            (False, xxxx, pattern, default_locale, "is_valid(B) pattern"),
            (False, xxxx, pattern, None, "is_valid(B) pattern, no locale "),   # Added test case, truly passing in no locale
            (False, "31 Dec 2005", germanPattern, JavaToPyLocale.GERMAN, "is_valid(B) both"),
            (False, "31 Dec 2005", germanPattern, JavaToPyLocale.GERMAN, "is_valid(B) both")
        ]
    )
    def test_is_valid(self, assert_type:bool, input_val:str, input_pattern:str, input_locale:str, assert_msg:str) -> None:
        """
        Test `CalendarValidator.is_valid()`method.  
        # Also includes test cases in `test`AbstractCalendarValidatorTest.java`.
        """
        assert assert_type == CalendarValidator.get_instance().is_valid(value=input_val, pattern=input_pattern, locale=input_locale), assert_msg
   
    
    def test_compare(self) -> None:
        """ Test compare date methods. """
        same_time = 124522
        test_date = 20050823
        # Create some datetimes for testing
        diff_hour = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), test_date, 115922)    # same date, different time
        diff_min = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), test_date, 124422)    # same date, different time
        diff_sec = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), test_date, 124521)    # same date, different time

        value = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), test_date, same_time)    # test value
        cal20050824 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20050824, same_time)    # +1 day
        cal20050822 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20050822, same_time)    # -1 day

        cal20050830 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20050830, same_time)    # +1 week
        cal20050816 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20050816, same_time)    # -1 week

        cal20050901 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20050901, same_time)    # +1 month
        cal20050801 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20050801, same_time)    # same month
        cal20050731 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20050731, same_time)    # -1 month

        cal20051101 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20051101, same_time)    # +1 quarter (Feb Start)
        cal20051001 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20051001, same_time)    # +1 quarter
        cal20050701 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20050701, same_time)    # same quarter
        cal20050630 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20050630, same_time)    # -1 quarter

        cal20060101 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20060101, same_time)    # +1 year
        cal20050101 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20050101, same_time)    # same year
        cal20041231 = TestAbstractCalendarValidator._create_calendar(ZoneInfo("Etc/GMT"), 20041231, same_time)    # -1 year
        # Compare Overall
        assert 1 == self.cal_validator._compare(value, diff_hour, "hour"), "hour GT"
        assert 0 == self.cal_validator._compare(value, diff_min, "hour"), "hour EQ"
        assert 1 == self.cal_validator._compare(value, diff_min, "minute"), "mins GT"
        assert 0 == self.cal_validator._compare(value, diff_sec, "minute"), "mins EQ"
        assert 1 == self.cal_validator._compare(value, diff_sec, "second"), "secs GT"

        # Compare days
        assert -1 == self.cal_validator.compare_dates(value, cal20050824), "date LT"    # +1 day
        assert 0 == self.cal_validator.compare_dates(value, diff_hour), "date EQ"    # same day, diff hour
        assert 0 == self.cal_validator._compare(value, diff_hour, "day"), "date(B)"    # same day, diff hour
        assert 1 == self.cal_validator.compare_dates(value, cal20050822), "date GT"    # -1 day

        # Compare Weeks
        assert -1 == self.cal_validator.compare_weeks(value, cal20060101), "week GT, but year LT"    # Added test case
        assert -1 == self.cal_validator.compare_weeks(value, cal20050830), "week LT"    # +1 week
        assert 0  == self.cal_validator.compare_weeks(value, cal20050824), "week =1"    # +1 day
        assert 0 == self.cal_validator.compare_weeks(value, cal20050822), "week =2"    # same week
        assert 0 == self.cal_validator._compare(value, cal20050822, "week"), "week =3"    # same week
        assert 0 == self.cal_validator.compare_weeks(value, cal20050822), "week =4"    # -1 day
        assert 1 == self.cal_validator.compare_weeks(value, cal20050816), "week GT"    # -1 week
        assert 1 == self.cal_validator.compare_weeks(value, cal20041231), "week LT, but year GT"    # Added test case
        
        # Compare Months
        assert -1 == self.cal_validator.compare_months(value, cal20050901), "mnth LT"    # +1 month
        assert 0 == self.cal_validator.compare_months(value, cal20050830), "mnth =1"    # +1 week
        assert 0 == self.cal_validator.compare_months(value, cal20050801), "mnth =2"    # same month
        assert 0 == self.cal_validator.compare_months(value, cal20050816), "mnth =3"    # -1 week
        assert 1 == self.cal_validator.compare_months(value, cal20050731), "mnth GT"    # -1 month

        # Compare Quarters
        assert -1 == self.cal_validator.compare_quarters(value, cal20051101), "qtrA <1"    # +1 quarter (Feb)
        assert -1 == self.cal_validator.compare_quarters(value, cal20051001), "qtrA <2"    # +1 quarter
        assert 0 == self.cal_validator.compare_quarters(value, cal20050901), "qtrA =1"    # +1 month
        assert 0 == self.cal_validator.compare_quarters(value, cal20050701), "qtrA =2"    # same quarter
        assert 0 == self.cal_validator.compare_quarters(value, cal20050731), "qtrA =3"    # -1 month
        assert 1 == self.cal_validator.compare_quarters(value, cal20050630), "qtrA GT"    # -1 quarter
        # Change quarter 1 to start in Feb
        assert -1 == self.cal_validator.compare_quarters(value, cal20051101, 2), "qtrB LT"    # +1 quarter (Feb)
        assert 0 == self.cal_validator.compare_quarters(value, cal20051001, 2), "qtrB =1"    # same quarter
        assert 0 == self.cal_validator.compare_quarters(value, cal20050901, 2), "qtrB =2"    # +1 month
        assert 1 == self.cal_validator.compare_quarters(value, cal20050701, 2), "qtrB =3"    # same quarter
        assert 1 == self.cal_validator.compare_quarters(value, cal20050731, 2), "qtrB =4"    # -1 month
        assert 1 == self.cal_validator.compare_quarters(value, cal20050630, 2), "qtrB GT"    # -1 quarter
       
        # Compare Years
        assert -1 == self.cal_validator.compare_years(value, cal20060101), "year LT"    # +1 year
        assert 0 == self.cal_validator.compare_years(value, cal20050101), "year EQ"    # same year
        assert 1 == self.cal_validator.compare_years(value, cal20041231), "year GT"    # -1 year

        # invalid compare
        with pytest.raises(TypeError) as e:
            self.cal_validator._compare(value, value, -1)


    def test_date_time_style(self) -> None:
        """
        Test Date/Time style Validator (there isn't an implementation for this).
        The default contry is `US`, default language is `en`, and default timezone is `GMT`.
        """
        val = "12/31/05, 2:23 PM"
        us_val = "12/31/05, 2:23 PM"
        dt_validator = AbstractCalendarValidator(True, 3, 3)
        assert dt_validator.is_valid(value=val), "validate(A) default"
        assert dt_validator.is_valid(value=us_val, locale=JavaToPyLocale.US), "validate(A) locale."


    @pytest.fixture
    def cal20051231(self):
        return self._create_calendar(zone=ZoneInfo("Etc/GMT"), date=20051231, time=11500) 


    default_locale:str = "en_US"
    default_tz:tzinfo = TestTimeZones.GMT
    germanPattern:str = "dd MMM yyyy"
    patternA:str = "yyyy-MM-dd HH:mm"
    patternB:str = "yyyy-MM-dd z"
    @pytest.mark.parametrize(
        "expected_str, pattern, locale, time_zone, assert_msg", [
            # validator defaults to SHORT, but the format varies between JVMs
            ("12/31/05", None, default_locale, default_tz, "default"),
            ("12/31/05", None, None, default_tz, "default, no locale "),   # Added test case, truly passing in no locale
            ("12/31/05", None, default_locale, None, "default, no timezone"),   # Added test case, truly passing in no timezone
            ("12/31/05", None, None, None, "default, no locale no timezone"),   # Added test case, truly passing in no locale and no timezone
            ("12/31/05", None, JavaToPyLocale.US, default_tz, "locale"),
            ("12/31/05", None, JavaToPyLocale.US, None, "locale, no timezone"),   # Added test case, truly passing in no timezone

            ("2005-12-31 01:15", patternA, default_locale, default_tz, "patternA"),
            ("2005-12-31 01:15", patternA, None, default_tz, "patternA, no locale "),   # Added test case, truly passing in no locale
            ("2005-12-31 01:15", patternA, default_locale, None, "patternA, no timezone"),   # Added test case, truly passing in no timezone
            ("2005-12-31 01:15", patternA, None, None, "patternA, no locale no timezone"),   # Added test case, truly passing in no locale and no timezone
            ("2005-12-31 GMT", patternB, default_locale, default_tz, "patternB"),
            ("2005-12-31 GMT", patternB, None, default_tz, "patternB, no locale "),   # Added test case, truly passing in no locale
            ("2005-12-31 GMT", patternB, default_locale, None, "patternB, no timezone"),   # Added test case, truly passing in no timezone
            ("2005-12-31 GMT", patternB, None, None, "patternB, no locale no timezone"),   # Added test case, truly passing in no locale and no timezone
            ("31 Dez. 2005", germanPattern, JavaToPyLocale.GERMAN, default_tz, "both"),
            ("31 Dez. 2005", germanPattern, JavaToPyLocale.GERMAN, None, "both, no timezone"),   # Added test case, truly passing in no timezone
            # EST Time Zone
            ("12/30/05", None, default_locale, TestTimeZones.EST, "EST default"),
            ("12/30/05", None, None, TestTimeZones.EST, "EST default, no locale "),   # Added test case, truly passing in no locale
            ("12/30/05", None, JavaToPyLocale.US, TestTimeZones.EST, "EST locale"),
            ("2005-12-30 20:15", patternA, default_locale, TestTimeZones.EST, "EST patternA"),
            ("2005-12-30 20:15", patternA, None, TestTimeZones.EST, "EST patternA, no locale "),   # Added test case, truly passing in no locale
            ("2005-12-30 EST", patternB, default_locale, TestTimeZones.EST, "EST patternB"),
            ("2005-12-30 EST", patternB, None, TestTimeZones.EST, "EST patternB, no locale "),   # Added test case, truly passing in no locale
            ("30 Dez. 2005", germanPattern, JavaToPyLocale.GERMAN, TestTimeZones.EST, "EST both")
        ]
    )
    def test_format(self, expected_str:str, cal20051231:datetime, pattern:str, locale:str, time_zone:tzinfo, assert_msg:str) -> None:
        """
        Tests the CalendarValidator.format() function with default and custom patterns, locales, and time zones.
        The default contry is `US`, default language is `en`, and default timezone is `GMT`.
        """
        assert expected_str == self.cal_validator.format(value=cal20051231, pattern=pattern, locale=locale, time_zone=time_zone), assert_msg


    # -------- Test cases inherited from TestAbstractCalendarValidator ----------:

    def test_locale_invalid(self) -> None:
        """ 
        Test Invalid datetime strings with "locale" validation.
        Inherited from ``TestAbstractCalendarValidator.test_locale_invalid()``. 
        """
        for i, invalid_locale in enumerate(self._locale_invalid):
            text = f"{i} value=[{invalid_locale}] passed "
            date:object = self._validator._parse(value=invalid_locale, pattern=None, locale=JavaToPyLocale.US, time_zone=None)
            print(f"Created date: {date} from string: {invalid_locale}")
            assert date is None, f"validateObj() {text}"
            assert self._validator.is_valid(value=invalid_locale,locale=JavaToPyLocale.US) == False, f"is_valid() {text}"
    

    def test_locale_valid( self) -> None:
        """ 
        Test Valid datetime strings with "locale" validation.
        Inherited from ``TestAbstractCalendarValidator.test_locale_valid()``. 
        """
        for i, valid_locale in enumerate(self._locale_valid):
            text = f"{i} value=[{valid_locale}] failed "
            date:object = self._validator.validate(value=valid_locale, pattern=None, locale=JavaToPyLocale.US, time_zone=None)
            assert date is not None, f"validateObj() {text} {date}"
            assert self._validator.is_valid(value=valid_locale, locale=JavaToPyLocale.US) == True, f"is_valid() {text}"
            if isinstance(date, datetime):
                assert date_get_time(self._pattern_expect[i]) == date_get_time(date), f"compare {text}"

    
    def test_pattern_invalid(self) -> None:
        """ 
        Test Invalid datetime strings with "pattern" validation.
        Inherited from ``TestAbstractCalendarValidator.test_pattern_invalid()``. 
        """
        for i, invalid_pattern in enumerate(self._pattern_invalid):
            text = f"{i} value=[{invalid_pattern}] passed "
            date:object = self._validator._parse(value=invalid_pattern, pattern='yy-MM-dd', locale=None, time_zone=None)
            assert date is None, f"validate() {text} {date}"
            assert self._validator.is_valid(value=invalid_pattern, pattern="yy-MM-dd") == False, f"is_valid() {text}"


    def test_pattern_valid(self) -> None:
        """ 
        Test Valid datetime strings with "pattern" validation.
        Inherited from ``TestAbstractCalendarValidator.test_pattern_valid()``. 
        """
        for i, valid_pattern in enumerate(self._pattern_valid):
            text = f"{i} value=[{valid_pattern}] failed "
            date:object = self._validator._parse(value=valid_pattern, pattern='yy-MM-dd', locale=None, time_zone=None)
            assert date is not None, f"validateObj() {text} {date}"
            assert self._validator.is_valid(value=valid_pattern, pattern='yy-MM-dd') == True, f"is_valid() {text}"
            if isinstance(date, datetime):
                assert date_get_time(self._pattern_expect[i]) == date_get_time(date), f"compare {text}"
